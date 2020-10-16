from enum import Enum
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class IPSJobPostResponse(BaseModel):
    output_id: UUID


class IPSJobState(str, Enum):
    pending = 'pending'
    active = 'active'
    finished = 'completed'
    failed = 'failed'


class IPSJobStatus(BaseModel):

    output_id: UUID
    state: IPSJobState
    estimated_time_to_completion: Optional[float] = None

    def is_running(self):
        return self.state in [IPSJobState.active, IPSJobState.pending]
