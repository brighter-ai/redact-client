import logging
import os
import tempfile
import threading
import time
import urllib.parse
import uuid
from io import FileIO
from pathlib import Path
from typing import IO, Any, Dict, Optional, Union
from uuid import UUID

import httpx

from redact.api_versions import REDACT_API_VERSIONS
from redact.errors import RedactConnectError, RedactResponseError
from redact.settings import Settings
from redact.utils import normalize_url
from redact.v3.data_models import (
    JobArguments,
    JobLabels,
    JobPostResponse,
    JobResult,
    OutputType,
    ServiceType,
)

settings = Settings()

_client_creation_lock = threading.Lock()
_client_singleton: Optional[httpx.Client] = None  # see get_singleton_client

# limit post requests, because their concurrency seems to put a lot of strain on the API Management
_post_lock = threading.BoundedSemaphore(2)

log = logging.getLogger("redact-requests")


def get_singleton_client():
    global _client_singleton
    with _client_creation_lock:
        if _client_singleton is None:
            _client_singleton = httpx.Client()
        return _client_singleton


class RedactRequests:
    """
    Helper class wrapping requests to the Redact API.
    """

    API_VERSION = REDACT_API_VERSIONS.v3

    def __init__(
        self,
        redact_url: str = settings.redact_url_default,
        subscription_id: Optional[str] = None,
        api_key: Optional[str] = None,
        httpx_client: Optional[httpx.Client] = None,
    ):
        self.redact_url = normalize_url(redact_url)
        self.api_key = api_key
        self.subscription_id = subscription_id
        self._headers = {"Accept": "*/*"}
        self.retry_total_time_limit: float = 600  # 10 minutes in seconds

        if self.api_key:
            self._headers["api-key"] = self.api_key
        if self.subscription_id:
            self._headers["Subscription-Id"] = self.subscription_id

        # httpx.Client client is thread safe, see https://github.com/encode/httpx/discussions/1633
        self._client = httpx_client or get_singleton_client()

    def post_job(
        self,
        file: FileIO,
        service: ServiceType,
        out_type: OutputType,
        job_args: Optional[JobArguments] = None,
        licence_plate_custom_stamp: Optional[IO] = None,
        custom_labels: Optional[Union[str, IO, JobLabels]] = None,
    ) -> JobPostResponse:
        """
        Post the job via a post request.
        """

        try:
            _ = file.name
        except AttributeError as e:
            raise ValueError(
                "Expecting 'file' argument to have a 'name' attribute, i.e., FileIO."
            ) from e

        url = urllib.parse.urljoin(
            self.redact_url, f"{service}/{self.API_VERSION}/{out_type}"
        )

        if not job_args:
            job_args = JobArguments()

        custom_labels_filelike: bytes
        if isinstance(custom_labels, JobLabels):
            custom_labels_filelike = custom_labels.json().encode("utf8")
        elif isinstance(custom_labels, str):
            custom_labels_filelike = custom_labels.encode("utf8")
        else:
            custom_labels_filelike = custom_labels

        files = {"file": file}
        if licence_plate_custom_stamp:
            files["licence_plate_custom_stamp"] = licence_plate_custom_stamp
        if custom_labels:
            files["custom_labels"] = custom_labels_filelike

        upload_debug_uuid = uuid.uuid4()
        with _post_lock:
            log.debug(f"Posting to {url} debug id (not output_id): {upload_debug_uuid}")
            # TODO: Remove the timeout when Redact responds quicker after uploading large files
            response = self._retry_on_network_problem_with_backoff(
                self._client.post,
                debug_uuid=upload_debug_uuid,
                url=url,
                files=files,
                params=job_args.dict(exclude_none=True),
                headers=self._headers,
                timeout=60.0,
            )
            log.debug(
                f"Post response to debug id (not output_id) {upload_debug_uuid}: {response}"
            )
            if response.status_code != 200:
                raise RedactResponseError(
                    response=response, msg=f"Error posting job: {response.content}"
                )

            return JobPostResponse(**response.json())

    def get_output(
        self,
        service: ServiceType,
        out_type: OutputType,
        output_id: UUID,
        ignore_warnings: bool = False,
    ) -> JobResult:
        """
        Retrieves job result as object in memory.
        """

        url = self._get_output_download_url(service, out_type, output_id)

        query_params = self._get_output_download_query_params(ignore_warnings)

        debug_uuid = uuid.uuid4()
        response = self._retry_on_network_problem_with_backoff(
            self._client.get,
            debug_uuid,
            url,
            params=query_params,
            headers=self._headers,
        )

        if response.status_code != 200:
            raise RedactResponseError(
                response=response,
                msg=f"Error downloading job result for output_id {output_id}: "
                f"{response.content.decode()}",
            )

        return JobResult(
            content=response.content, media_type=response.headers["Content-Type"]
        )

    def _stream_output_to_file(
        self, debug_uuid, output_id, file: Path, url, params, headers
    ):
        with self._client.stream(
            "GET", url, params=params, headers=headers
        ) as response:
            if response.status_code != 200:
                raise RedactResponseError(
                    response=response,
                    msg=f"Error downloading job result for output_id {output_id}, debug_uuid {debug_uuid}: "
                    f"{response.read().decode()}",
                )
            temp_file = tempfile.NamedTemporaryFile(
                "wb", dir=str(file.parent), delete=False
            )
            finished = False
            try:
                with temp_file:
                    for chunk in response.iter_bytes():
                        temp_file.write(chunk)
                finished = True
            finally:
                if finished:
                    os.rename(temp_file.name, str(file))
                else:
                    os.unlink(temp_file.name)

    def write_output_to_file(
        self,
        service: ServiceType,
        out_type: OutputType,
        output_id: UUID,
        file: Path,
        ignore_warnings: bool = False,
    ) -> None:
        """
        Retrieves job result and streams it to file, greatly reducing memory load
        and resolving memory fragmentation problems.
        """

        url = self._get_output_download_url(service, out_type, output_id)

        query_params = self._get_output_download_query_params(ignore_warnings)

        debug_uuid = uuid.uuid4()
        self._retry_on_network_problem_with_backoff(
            self._stream_output_to_file,
            debug_uuid,
            debug_uuid,
            output_id,
            file,
            url,
            params=query_params,
            headers=self._headers,
        )

    def _get_output_download_query_params(self, ignore_warnings: bool):
        return {
            "ignore_warnings": ignore_warnings,
        }

    def _get_output_download_url(
        self, service: ServiceType, out_type: OutputType, output_id: UUID
    ):
        return urllib.parse.urljoin(
            self.redact_url, f"{service}/{self.API_VERSION}/{out_type}/{output_id}"
        )

    def get_status(
        self, service: ServiceType, out_type: OutputType, output_id: UUID
    ) -> Dict:

        url = urllib.parse.urljoin(
            self.redact_url,
            f"{service}/{self.API_VERSION}/{out_type}/{output_id}/status",
        )

        debug_uuid = uuid.uuid4()
        response = self._retry_on_network_problem_with_backoff(
            self._client.get, debug_uuid, url, headers=self._headers
        )

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg="Error getting job status")

        return response.json()

    def get_labels(
        self,
        service: ServiceType,
        out_type: OutputType,
        output_id: UUID,
        timeout: float = 60.0,
    ) -> JobLabels:

        url = urllib.parse.urljoin(
            self.redact_url,
            f"{service}/{self.API_VERSION}/{out_type}/{output_id}/labels",
        )

        debug_uuid = uuid.uuid4()
        response = self._retry_on_network_problem_with_backoff(
            self._client.get, debug_uuid, url, headers=self._headers, timeout=timeout
        )

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg="Error getting labels")

        return JobLabels.parse_obj(response.json())

    def delete_output(
        self, service: ServiceType, out_type: OutputType, output_id: UUID
    ) -> Dict:

        url = urllib.parse.urljoin(
            self.redact_url, f"{service}/{self.API_VERSION}/{out_type}/{output_id}"
        )

        debug_uuid = uuid.uuid4()
        response = self._retry_on_network_problem_with_backoff(
            self._client.delete, debug_uuid, url, headers=self._headers
        )

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg="Error deleting job")

        return response.json()

    def get_error(
        self, service: ServiceType, out_type: OutputType, output_id: UUID
    ) -> Dict:

        url = urllib.parse.urljoin(
            self.redact_url,
            f"{service}/{self.API_VERSION}/{out_type}/{output_id}/error",
        )

        debug_uuid = uuid.uuid4()
        response = self._retry_on_network_problem_with_backoff(
            self._client.get, debug_uuid, url, headers=self._headers
        )

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg="Error getting job error")

        return response.json()

    def _calculate_retry_backoff(
        self,
        debug_uuid: uuid.UUID,
        retry_start: float,
        retry_delay: float,
        exc_info: BaseException,
    ):

        if retry_start == -1:
            retry_start = time.time()
            retry_delay = 1  # start by waiting 2 seconds - going to double it below

        retry_runtime = time.time() - retry_start
        if retry_runtime > self.retry_total_time_limit:
            log.debug("Aborting retry due to exceeding retry limit")
            return retry_start, -1
        max_retry_delay_remaining = max(
            1, self.retry_total_time_limit - retry_runtime
        )  # max to ensure positive
        retry_delay = min(2 * retry_delay, max_retry_delay_remaining)

        log.debug(
            f"Network exception '{exc_info}' caught on request {debug_uuid}, "
            f"retrying after {retry_delay:.2f}s."
        )
        return retry_start, retry_delay

    def _retry_on_network_problem_with_backoff(
        self, func, debug_uuid: uuid.UUID, *positional_arguments, **keyword_arguments
    ) -> Any:

        retry_start = -1
        retry_delay = -1

        while True:
            try:
                return func(*positional_arguments, **keyword_arguments)
            except (
                httpx.NetworkError,
                httpx.TimeoutException,
                httpx.ProtocolError,
            ) as e:
                retry_start, retry_delay = self._calculate_retry_backoff(
                    debug_uuid, retry_start, retry_delay, e
                )
                if retry_delay < 0:
                    raise RedactConnectError(
                        f"Error communicating with {self.redact_url}: {e}"
                    ) from e

            time.sleep(retry_delay)
