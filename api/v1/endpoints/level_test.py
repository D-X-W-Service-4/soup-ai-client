import json
from fastapi import APIRouter, HTTPException

from graphs import evaluate_level_test_graph, generate_level_test
from schema import GenerateLevelTestRequest, EvaluateEssayLevelTestRequest, create_eval_quiz_input_payload
router = APIRouter()

# http://127.0.0.1:8000/level-test/generate
@router.post("/generate", status_code=200)
async def get_level_test(request: GenerateLevelTestRequest):
    '''create new level test'''
    result = await generate_level_test(request.soup_level, request.workbooks, request.unit_list)
    
    return {"level_test": result}


# http://127.0.0.1:8000/level-test/evaluate
@router.post("/evaluate", status_code=200) #
async def evaluator(request: EvaluateEssayLevelTestRequest):
    ''' evaluate 서술형 문제 단위만'''
    quizs = request.quizzes
    graph_input = create_eval_quiz_input_payload(quizs)
    main_graph = evaluate_level_test_graph()
    response = await main_graph.ainvoke(input=graph_input)
    evaluate_result = response.get("result")

    return evaluate_result