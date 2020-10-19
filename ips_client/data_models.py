from enum import Enum
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class JobPostResponse(BaseModel):
    output_id: UUID


class JobState(str, Enum):
    pending = 'pending'
    active = 'active'
    finished = 'completed'
    failed = 'failed'


class JobStatus(BaseModel):

    output_id: UUID
    state: JobState
    estimated_time_to_completion: Optional[float] = None

    def is_running(self):
        return self.state in [JobState.active, JobState.pending]
