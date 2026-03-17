from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from .database import engine, Base, get_db
from . import models
from .schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    StepCreate, StepUpdate, StepResponse,
    RuleCreate, RuleUpdate, RuleResponse,
    ExecutionCreate, ExecutionResponse
)
from .rule_engine import find_next_step, validate_condition_syntax

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Halleyx Workflow Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# ── WORKFLOWS ──────────────────────────────────────────────

@app.post("/workflows", response_model=WorkflowResponse, tags=["Workflows"])
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)):
    wf = models.Workflow(
        id=str(uuid.uuid4()), name=payload.name, description=payload.description,
        input_schema=payload.input_schema or {}, start_step_id=payload.start_step_id,
        version=1, is_active=True
    )
    db.add(wf); db.commit(); db.refresh(wf)
    return wf

@app.get("/workflows", response_model=List[WorkflowResponse], tags=["Workflows"])
def list_workflows(search: Optional[str] = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(models.Workflow)
    if search:
        q = q.filter(models.Workflow.name.ilike(f"%{search}%"))
    return q.offset(skip).limit(limit).all()

@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse, tags=["Workflows"])
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    return wf

@app.put("/workflows/{workflow_id}", response_model=WorkflowResponse, tags=["Workflows"])
def update_workflow(workflow_id: str, payload: WorkflowUpdate, db: Session = Depends(get_db)):
    wf = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    if payload.name is not None: wf.name = payload.name
    if payload.description is not None: wf.description = payload.description
    if payload.input_schema is not None: wf.input_schema = payload.input_schema
    if payload.start_step_id is not None: wf.start_step_id = payload.start_step_id
    if payload.is_active is not None: wf.is_active = payload.is_active
    wf.version += 1
    wf.updated_at = datetime.utcnow()
    db.commit(); db.refresh(wf)
    return wf

@app.delete("/workflows/{workflow_id}", tags=["Workflows"])
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    db.delete(wf); db.commit()
    return {"message": "Deleted"}

# ── STEPS ──────────────────────────────────────────────────

@app.post("/workflows/{workflow_id}/steps", response_model=StepResponse, tags=["Steps"])
def create_step(workflow_id: str, payload: StepCreate, db: Session = Depends(get_db)):
    wf = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    if payload.step_type not in ["task", "approval", "notification"]:
        raise HTTPException(400, "step_type must be: task, approval, or notification")
    step = models.Step(
        id=str(uuid.uuid4()), workflow_id=workflow_id, name=payload.name,
        step_type=payload.step_type, order=payload.order, metadata_=payload.metadata_ or {}
    )
    db.add(step); db.commit(); db.refresh(step)
    return step

@app.get("/workflows/{workflow_id}/steps", response_model=List[StepResponse], tags=["Steps"])
def list_steps(workflow_id: str, db: Session = Depends(get_db)):
    return db.query(models.Step).filter(models.Step.workflow_id == workflow_id).order_by(models.Step.order).all()

@app.put("/steps/{step_id}", response_model=StepResponse, tags=["Steps"])
def update_step(step_id: str, payload: StepUpdate, db: Session = Depends(get_db)):
    step = db.query(models.Step).filter(models.Step.id == step_id).first()
    if not step: raise HTTPException(404, "Step not found")
    if payload.name is not None: step.name = payload.name
    if payload.step_type is not None: step.step_type = payload.step_type
    if payload.order is not None: step.order = payload.order
    if payload.metadata_ is not None: step.metadata_ = payload.metadata_
    step.updated_at = datetime.utcnow()
    db.commit(); db.refresh(step)
    return step

@app.delete("/steps/{step_id}", tags=["Steps"])
def delete_step(step_id: str, db: Session = Depends(get_db)):
    step = db.query(models.Step).filter(models.Step.id == step_id).first()
    if not step: raise HTTPException(404, "Step not found")
    db.delete(step); db.commit()
    return {"message": "Deleted"}

# ── RULES ──────────────────────────────────────────────────

@app.post("/steps/{step_id}/rules", response_model=RuleResponse, tags=["Rules"])
def create_rule(step_id: str, payload: RuleCreate, db: Session = Depends(get_db)):
    step = db.query(models.Step).filter(models.Step.id == step_id).first()
    if not step: raise HTTPException(404, "Step not found")
    if not validate_condition_syntax(payload.condition):
        raise HTTPException(400, "Invalid condition syntax")
    rule = models.Rule(
        id=str(uuid.uuid4()), step_id=step_id, condition=payload.condition,
        next_step_id=payload.next_step_id, priority=payload.priority
    )
    db.add(rule); db.commit(); db.refresh(rule)
    return rule

@app.get("/steps/{step_id}/rules", response_model=List[RuleResponse], tags=["Rules"])
def list_rules(step_id: str, db: Session = Depends(get_db)):
    return db.query(models.Rule).filter(models.Rule.step_id == step_id).order_by(models.Rule.priority).all()

@app.put("/rules/{rule_id}", response_model=RuleResponse, tags=["Rules"])
def update_rule(rule_id: str, payload: RuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not rule: raise HTTPException(404, "Rule not found")
    if payload.condition is not None:
        if not validate_condition_syntax(payload.condition):
            raise HTTPException(400, "Invalid condition syntax")
        rule.condition = payload.condition
    if payload.next_step_id is not None: rule.next_step_id = payload.next_step_id
    if payload.priority is not None: rule.priority = payload.priority
    rule.updated_at = datetime.utcnow()
    db.commit(); db.refresh(rule)
    return rule

@app.delete("/rules/{rule_id}", tags=["Rules"])
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not rule: raise HTTPException(404, "Rule not found")
    db.delete(rule); db.commit()
    return {"message": "Deleted"}

# ── EXECUTIONS ─────────────────────────────────────────────

@app.post("/workflows/{workflow_id}/execute", response_model=ExecutionResponse, tags=["Execution"])
def execute_workflow(workflow_id: str, payload: ExecutionCreate, db: Session = Depends(get_db)):
    wf = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    if not wf.is_active: raise HTTPException(400, "Workflow is not active")
    if not wf.start_step_id: raise HTTPException(400, "No start step defined")

    execution = models.Execution(
        id=str(uuid.uuid4()), workflow_id=workflow_id, workflow_version=wf.version,
        status="in_progress", data=payload.data, logs=[], current_step_id=wf.start_step_id,
        triggered_by=payload.triggered_by, started_at=datetime.utcnow()
    )
    db.add(execution); db.commit()

    current_step_id = wf.start_step_id
    logs = []
    steps_run = 0

    while current_step_id and steps_run < 50:
        steps_run += 1
        step = db.query(models.Step).filter(models.Step.id == current_step_id).first()
        if not step:
            logs.append({"error": f"Step {current_step_id} not found"})
            execution.status = "failed"
            break

        step_log = {
            "step_name": step.name, "step_type": step.step_type,
            "status": "completed", "started_at": datetime.utcnow().isoformat(),
            "evaluated_rules": [], "selected_next_step": None, "error_message": None
        }
        rules = db.query(models.Rule).filter(models.Rule.step_id == step.id).all()
        if rules:
            next_step_id, evaluated = find_next_step(rules, payload.data)
            step_log["evaluated_rules"] = evaluated
            step_log["selected_next_step"] = next_step_id
        else:
            next_step_id = None

        step_log["ended_at"] = datetime.utcnow().isoformat()
        logs.append(step_log)
        current_step_id = next_step_id

    if steps_run >= 50:
        execution.status = "failed"
    elif execution.status != "failed":
        execution.status = "completed"

    execution.logs = logs
    execution.current_step_id = current_step_id
    execution.ended_at = datetime.utcnow()
    db.commit(); db.refresh(execution)
    return execution

@app.get("/executions", response_model=List[ExecutionResponse], tags=["Execution"])
def list_executions(workflow_id: Optional[str] = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(models.Execution)
    if workflow_id: q = q.filter(models.Execution.workflow_id == workflow_id)
    return q.order_by(models.Execution.started_at.desc()).offset(skip).limit(limit).all()

@app.get("/executions/{execution_id}", response_model=ExecutionResponse, tags=["Execution"])
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    ex = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    if not ex: raise HTTPException(404, "Execution not found")
    return ex

@app.post("/executions/{execution_id}/cancel", response_model=ExecutionResponse, tags=["Execution"])
def cancel_execution(execution_id: str, db: Session = Depends(get_db)):
    ex = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    if not ex: raise HTTPException(404, "Execution not found")
    if ex.status not in ["pending", "in_progress"]: raise HTTPException(400, "Cannot cancel")
    ex.status = "canceled"; ex.ended_at = datetime.utcnow()
    db.commit(); db.refresh(ex)
    return ex

@app.post("/executions/{execution_id}/retry", response_model=ExecutionResponse, tags=["Execution"])
def retry_execution(execution_id: str, db: Session = Depends(get_db)):
    ex = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    if not ex: raise HTTPException(404, "Execution not found")
    if ex.status != "failed": raise HTTPException(400, "Only failed executions can be retried")
    ex.status = "in_progress"; ex.retries += 1; ex.ended_at = None
    db.commit(); db.refresh(ex)
    return ex
