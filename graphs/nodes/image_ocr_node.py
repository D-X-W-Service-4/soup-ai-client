from graphs.states import EvaluateLevelTestState
from utils import imagefile_to_b64_png, call_kanana_generate


async def node_image_ocr(state: EvaluateLevelTestState) -> EvaluateLevelTestState:
    image_url= state.get("image_url", None)
    if image_url:
        image_b64 = imagefile_to_b64_png(image_url)
        payload = {
            "image_url": image_url,
            "image_b64": image_b64,
        }

        data = await call_kanana_generate(payload)
        print("ocr reslult: ", data)
        if data:
            return {**state,
                    "student_ocr": data.get("text", "풀이 없음")
                    }
        else: 
            return {
                **state,
                "student_ocr": "풀이 없음"
                }
    else:
        return {
            **state,
            "student_ocr": "풀이 없음"
            }