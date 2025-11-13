
from openai import AsyncOpenAI
from typing import Dict, Any
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
VASTAI_HOST=os.getenv("VASTAI_HOST")
EXAONE_PORT=os.getenv("EXAONE_PORT") 
REMOTE_API_KEY=os.getenv("REMOTE_API_KEY", "conference_service_ai")

vllm_client = AsyncOpenAI(
    base_url=f"http://{VASTAI_HOST}:{EXAONE_PORT}/v1", 
    api_key=REMOTE_API_KEY
    )

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# REMOTE_TIMEOUT_S = os.getenv("REMOTE_TIMEOUT_S", "120")


async def ask_llm(prompt: str) -> str:
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return resp.choices[0].message.content.strip()


async def ask_exaone(prompt: str) -> str:
    resp = await vllm_client.chat.completions.create(
        model="LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=220
    )
    return resp.choices[0].message.content.strip()
import json

def ensure_json(s: str, default: dict = None) -> dict:
    """
    LLM 출력에서 JSON 부분만 스마트하게 추출하여 파싱합니다.
    마크다운, 앞뒤 잡담, 그리고 '보이지 않는 특수 공백'을 처리합니다.
    """
    if default is None:
        default = {}

    if not s:
        print("Warning: LLM 출력이 비어있음")
        return default

    # 1. JSON 구간({ ... }) 추출
    start_idx = s.find('{')
    end_idx = s.rfind('}')

    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        print(f"Warning: 유효한 JSON 브라켓을 찾을 수 없음.")
        return default

    json_str = s[start_idx : end_idx + 1]

    # 2. [중요] 특수 공백 문자 제거 (이 부분이 핵심 해결책입니다)
    # \xa0 : Non-breaking space (웹/LLM 출력에서 흔함)
    # \u3000 : Ideographic space (전각 공백, 한글/일어 텍스트에서 가끔 등장)
    json_str = json_str.replace('\xa0', ' ').replace('\u3000', ' ')

    # 3. 파싱 시도
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Warning: JSON 파싱 실패 (DecodeError).")
        print(f"- 에러 메시지: {e}")
        # 디버깅을 위해 repr()로 출력해보면 숨은 문자가 보입니다.
        print(f"- 문제의 문자열(repr): {repr(json_str)}") 
        return default
    

def safe(val, default="없음"):
    return default if val is None else val


def normalize_text(name: str) -> str:
    name = re.sub(r"\(.*?\)", "", name)
    return name.strip()

# async def call_exaone_async(
#     prompt: str,
#     max_new_tokens: int = 220,
#     top_p: float | None = None,
#     do_sample: bool = False,
#     stop: list[str] | None = None,
# ) -> str:

#     url = f"http://{VASTAI_HOST}:{EXAONE_PORT}/v1/chat/completions"
#     headers = {"Authorization": f"Bearer {REMOTE_API_KEY}", "Content-Type": "application/json"}
#     payload = {
#         "model": "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
#         "messages": [{"role": "user", "content": prompt}],
#         "max_new_tokens": max_new_tokens,
#     }
#     if top_p is not None:
#         payload["top_p"] = top_p
#     if stop is not None:
#         payload["stop"] = stop

#     timeout = httpx.Timeout(REMOTE_TIMEOUT_S) if isinstance(REMOTE_TIMEOUT_S, (int, float)) else REMOTE_TIMEOUT_S
#     async with asyncio.Semaphore(16):
#         async with httpx.AsyncClient(timeout=timeout) as client:
#             resp = await client.post(url, headers=headers, json=payload)
#     if resp.status_code != 200:
#         # 어디로 쐈는지, 무엇이 왔는지 바로 보이게
#         raise HTTPException(status_code=resp.status_code, detail=f"[{resp.status_code}] POST {url} -> {resp.text}")

#     data = resp.json()
#     return data["choices"][0]["message"]["content"]