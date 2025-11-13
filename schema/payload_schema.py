from pydantic import BaseModel, Field
from typing import List


class GeneratePlannerRequest(BaseModel):
    student_id: str = Field(..., description="학생 ID")
    date: str = Field(..., description="플래너 기준 날짜 (YYYY-MM-DD)")

# --------------

class GenerateLevelTestRequest(BaseModel):
    soup_level: str
    workbooks: str # 문제집들이 ,로 연결된 str
    unit_list: dict 
    # unit_checked_rate: Dict # ex. {"소인수분해 - 소인수분해": "해당 subject_unit_id에 포함된 모든 planner의 row에 있는 모든 checked의 합/개수"}
     # 일단 이건 보류

# --------------

class EvaluateLevelTestRequest(BaseModel):
    level_test_result: List
    # grade: str
    # num_questions: int
    # user_answer_image: str
    # text: str
    # unit_number: str
    # unit_name: str
    # answer: Optional[str]
    # answer_text: Optional[str]
    # topic: Optional[str]

# class GradeResponse(BaseModel):
#     result: Dict[str, Any]
