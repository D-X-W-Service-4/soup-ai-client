# schema/grade.py
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Settings(BaseModel):
    REMOTE_BASE: str = Field(default=os.getenv("REMOTE_BASE", "http://85.218.235.6:32016/v1"))
    REMOTE_API_KEY: str = Field(default=os.getenv("REMOTE_API_KEY", "conference_service_ai"))
    REMOTE_TIMEOUT_S: int = Field(default=int(os.getenv("REMOTE_TIMEOUT_S", "120")))

settings = Settings()

class GradeRequest(BaseModel):
    problem_text: str
    student_ocr: str
    answer_key: str
    rubric: Optional[str] = None
    max_score: int = 5

class GradeResponse(BaseModel):
    result: Dict[str, Any]
