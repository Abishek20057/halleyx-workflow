import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    input_schema = Column(JSON, default={})
    start_step_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    steps = relationship("Step", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")

class Step(Base):
    __tablename__ = "steps"
    id = Column(String, primary_key=True, default=gen_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    name = Column(String, nullable=False)
    step_type = Column(String, nullable=False)  # task, approval, notification
    order = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    workflow = relationship("Workflow", back_populates="steps")
    rules = relationship("Rule", back_populates="step", cascade="all, delete-orphan")

class Rule(Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True, default=gen_uuid)
    step_id = Column(String, ForeignKey("steps.id"), nullable=False)
    condition = Column(String, nullable=False)
    next_step_id = Column(String, nullable=True)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    step = relationship("Step", back_populates="rules")

class Execution(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True, default=gen_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    workflow_version = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed, canceled
    data = Column(JSON, default={})
    logs = Column(JSON, default=[])
    current_step_id = Column(String, nullable=True)
    retries = Column(Integer, default=0)
    triggered_by = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    workflow = relationship("Workflow", back_populates="executions")
