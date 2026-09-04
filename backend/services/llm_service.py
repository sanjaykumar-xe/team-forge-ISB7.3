"""
Team Forge — Central LLM Service with Cascading Model Failover
--------------------------------------------------------------
Provides unified, resilient access to Groq Cloud LLMs with:
- Cascading model failover (Primary -> Backup 1 -> Backup 2 -> Backup 3)
- Exponential backoff on HTTP 429 / rate limits
- Strict JSON cleaning (stripping markdown fences, think tags, trailing text)
- JSON validation and fallback handling
"""

import os
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY", "")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# Primary and backup model pool available on Groq
GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "allam-2-7b",
    "groq/compound",
    "groq/compound-mini",
    "qwen/qwen3.6-27b",
]



def clean_json_response(raw_text: str) -> str:
    """Cleans markdown fences, think tags, and leading/trailing noise from JSON strings."""
    if not raw_text:
        return "{}"
    
    text = raw_text.strip()
    
    # Strip <think> ... </think> reasoning blocks if present
    if "<think>" in text and "</think>" in text:
        text = text.split("</think>")[-1].strip()
        
    # Strip markdown code blocks (```json ... ``` or ``` ...)
    if "```" in text:
        # Match content between triple backticks
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
        else:
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()
            
    # Locate first '{' or '[' and last '}' or ']'
    start_brace = text.find("{")
    start_bracket = text.find("[")
    
    start_idx = -1
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start_idx = start_brace
        end_idx = text.rfind("}")
    elif start_bracket != -1:
        start_idx = start_bracket
        end_idx = text.rfind("]")
    else:
        end_idx = -1
        
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx + 1]
        
    return text


def execute_groq_completion(
    messages: List[Dict[str, str]],
    max_tokens: int = 2048,
    temperature: float = 0.1,
    models: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Executes a chat completion across model pool with automatic failover and rate limit backoff.
    Returns (response_text, model_name).
    """
    client = get_groq_client()
    target_models = models or GROQ_MODELS
    last_exc = None

    for model in target_models:
        for attempt in range(2):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                content = resp.choices[0].message.content or ""
                return content, model
            except Exception as exc:
                last_exc = exc
                err_msg = str(exc).lower()
                if "429" in err_msg or "rate limit" in err_msg or "rate_limit" in err_msg:
                    sleep_time = (2 ** attempt) + 0.5
                    time.sleep(sleep_time)
                else:
                    break

    raise last_exc if last_exc else RuntimeError("Groq completion failed across all models.")


def call_groq_json(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 2500,
    temperature: float = 0.1,
) -> Dict[str, Any]:
    """
    Invokes Groq with instructions to return valid JSON, parses the output,
    and returns a Python dictionary.
    """
    messages = [
        {"role": "system", "content": f"{system_prompt}\nYou MUST respond ONLY with valid JSON. Do not include preamble or conversational text."},
        {"role": "user", "content": prompt},
    ]
    
    raw_content, model_used = execute_groq_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    cleaned = clean_json_response(raw_content)
    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError as err:
        # Secondary recovery attempt: remove trailing commas or unescaped characters
        try:
            fixed = re.sub(r",\s*([\]}])", r"\1", cleaned)
            return json.loads(fixed)
        except Exception:
            raise ValueError(f"Failed to parse JSON from Groq ({model_used}): {err}\nRaw snippet: {cleaned[:300]}")
