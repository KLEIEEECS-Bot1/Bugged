from pydantic import BaseModel, Field

class DetectRequest(BaseModel):
    text: str = Field(..., min_length=1)

class DetectResponse(BaseModel):
    proba_ai: float
    proba_human: float
    decision: str
    votes: dict
    borderline: bool
    latency_ms: int
    model_versions: dict
