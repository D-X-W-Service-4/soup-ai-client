import asyncio
from fastapi import APIRouter
from graphs import evaluate_level_test_graph, eval_simple_level_test, generate_level_test
from schema import GenerateLevelTestRequest, EvaluateLevelTestRequest, create_eval_quiz_input_payload
router = APIRouter()
from tqdm import tqdm

# http://127.0.0.1:8000/v1/level-test/generate
@router.post("/generate", status_code=200)
async def get_level_test(request: GenerateLevelTestRequest):
    '''create new level test'''
    print("generate level test input payload: ", request)
    result = await generate_level_test(request.soup_level, request.workbooks, request.unit_list)
    
    return {"level_test": result}


# http://127.0.0.1:8000/v1/level-test/evaluate
@router.post("/evaluate", status_code=200) #
async def evaluator(request: EvaluateLevelTestRequest):
    print("evaluate level test input payload: ", request)
    print("\n\n------------------------------------------------------------------------")
    evaluate_results = []
    num_questions=len(request.level_test_result)
    for row in tqdm(request.level_test_result, total=num_questions):
        if row.get("user_answer_image"):
            print(f"→ 서술형 O / 서술형 대비모드 O ||| answer: {row.get('answer_text')} / user answer: {row.get('user_answer_text')}")
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
    
            print("essay 서술형 대비모드 채점 result: ", evaluate_result)
            evaluate_results.append(evaluate_result)
            print("------------------------------------------------------------------------")

        elif row.get("question_format") == "선택형":
            print(f"→ 서술형 X, answer ||| {row.get('answer')} / user answer: {row.get('user_answer_text')}")
            response = await eval_simple_level_test(question_text=row.get("text"),
                                                    user_answer=row.get("user_answer_text"),
                                                    answer=row.get("answer"))
            
            evaluate_result = response.get("eval_result")
            print("서술형 채점 result: ", evaluate_result["is_correct"])

            evaluate_results.append(evaluate_result)
            print("------------------------------------------------------------------------")
        
        elif row.get("question_format") == "단답형":
            print(f"→ 서술형 O / 서술형 대비모드 X ||| answer: {row.get('answer_text')} / user answer: {row.get('user_answer_text')}")
            response = await eval_simple_level_test(question_text=row.get("text"),
                                                    user_answer=row.get("user_answer_text"),
                                                    answer=row.get("answer_text"))
            
            evaluate_result = response.get("eval_result")
            print("선택형 채점 result: ", evaluate_result["is_correct"])
            evaluate_results.append(evaluate_result)
            print("------------------------------------------------------------------------")

    return {"evaluate_result": evaluate_results}
