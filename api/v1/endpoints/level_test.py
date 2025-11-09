import asyncio
from fastapi import APIRouter
from graphs import evaluate_level_test_graph, eval_simple_level_test, generate_level_test
from schema import GenerateLevelTestRequest, EvaluateLevelTestRequest, create_eval_quiz_input_payload
router = APIRouter()


async def _process_row(row, num_questions):
    if getattr(row, "user_answer_image", None):
        graph_input = create_eval_quiz_input_payload(
            num_questions=num_questions,
            user_answer_image=row.get("user_answer_image"),
            question_text=row.get("text"),
            answer=row.get("answer"),
            answer_text=row.get("answer_text"),
            topic=row.get("topic")
        )
        graph = evaluate_level_test_graph()
        response = await graph.ainvoke(input=graph_input)
        return response.get("final_eval_result")
    else:
        response = await eval_simple_level_test(
            question_text=row.get("text"),
            user_answer=row.get("user_answer_text"),
            answer=row.get("answer")
        )
        return response.get("eval_result")



# http://127.0.0.1:8000/v1/level-test/generate
@router.post("/generate", status_code=200)
async def get_level_test(request: GenerateLevelTestRequest):
    '''create new level test'''
    result = await generate_level_test(request.soup_level, request.workbooks, request.unit_list)
    
    return {"level_test": result}


# http://127.0.0.1:8000/v1/level-test/evaluate
@router.post("/evaluate", status_code=200) #
async def evaluator(request: EvaluateLevelTestRequest):
    ''' evaluate 서술형 문제 단위만 slm 태우기'''
    evaluate_results = []
    num_questions=len(request.level_test_result)
    for row in request.level_test_result:
        if row.get("user_answer_image"):
            graph_input = create_eval_quiz_input_payload(
                num_questions=num_questions, 
                user_answer_image=row.get("user_answer_image"),
                question_text=row.get("text"),
                answer=row.get("answer"),
                answer_text=row.get("answer_text"),
                topic=row.get("topic")
            )

            graph = evaluate_level_test_graph()
            response = await graph.ainvoke(input=graph_input)
            evaluate_result = response.get("final_eval_result")
            
            evaluate_results.append(evaluate_result)
        
        else:
            response = await eval_simple_level_test(question_text=row.get("text"),
                                                    user_answer=row.get("user_answer_text"),
                                                    answer=row.get("answer"))
            
            evaluate_result = response.get("eval_result")
            evaluate_results.append(evaluate_result)

    return {"evaluate_result": evaluate_results}
