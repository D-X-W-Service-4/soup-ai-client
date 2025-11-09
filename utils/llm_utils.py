
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


def ensure_json(s: str) -> Dict[str, Any]:
    """LLM 결과가 JSON 문자열이어야 하는 노드에서 파싱."""
    s = s.strip()
    # 코드블록 제거 방지용 최소 처리
    if s.startswith("```"):
        s = s.strip("`")
        # ```json ... ``` 케이스
        if s.lower().startswith("json"):
            s = s[4:].strip()
    return json.loads(s)


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