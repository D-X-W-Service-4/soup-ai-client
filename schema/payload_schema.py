from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union, Dict


class GeneratePlannerRequest(BaseModel):
    student_id: str = Field(..., description="학생 ID")
    date: str = Field(..., description="플래너 기준 날짜 (YYYY-MM-DD)")

# --------------

class GenerateLevelTestRequest(BaseModel):
    soup_level: str
    workbooks: str # 문제집들이 ,로 연결된 str
    unit_list: List # ex ["소인수분해 - 소인수분해"] list of subject_units "name"
    # unit_checked_rate: Dict # ex. {"소인수분해 - 소인수분해": "해당 subject_unit_id에 포함된 모든 planner의 row에 있는 모든 checked의 합/개수"}
     # 일단 이건 보류

# --------------
     
class EvaluateEssayLevelTestRequest(BaseModel):
    problem_text: str
    student_ocr: str
    answer_key: str
    rubric: Optional[str] = None
    max_score: int = 5

# class GradeResponse(BaseModel):
#     result: Dict[str, Any]
