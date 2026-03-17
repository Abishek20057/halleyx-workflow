from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = {}
    start_step_id: Optional[str] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    start_step_id: Optional[str] = None
    is_active: Optional[bool] = None

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    version: int
    is_active: bool
    input_schema: Optional[Dict[str, Any]] = None
    start_step_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class StepCreate(BaseModel):
    name: str
    step_type: str
    order: Optional[int] = 0
    metadata_: Optional[Dict[str, Any]] = {}

class StepUpdate(BaseModel):
    name: Optional[str] = None
    step_type: Optional[str] = None
    order: Optional[int] = None
    metadata_: Optional[Dict[str, Any]] = None

class StepResponse(BaseModel):
    id: str
    workflow_id: str
    name: str
    step_type: str
    order: int
    metadata_: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class RuleCreate(BaseModel):
    condition: str
    next_step_id: Optional[str] = None
    priority: Optional[int] = 1

class RuleUpdate(BaseModel):
    condition: Optional[str] = None
    next_step_id: Optional[str] = None
    priority: Optional[int] = None

class RuleResponse(BaseModel):
    id: str
    step_id: str
    condition: str
    next_step_id: Optional[str] = None
    priority: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ExecutionCreate(BaseModel):
    data: Dict[str, Any]
    triggered_by: Optional[str] = "anonymous"

class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    workflow_version: int
    status: str
    data: Optional[Dict[str, Any]] = None
    logs: Optional[List[Any]] = None
    current_step_id: Optional[str] = None
    retries: int
    triggered_by: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    class Config:
        from_attributes = True
