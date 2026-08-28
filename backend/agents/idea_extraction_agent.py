"""
Idea Extraction Agent
----------------------
Extracts structured information (product name, industry, target audience, core problem,
and domain keywords) from unstructured startup idea submissions using Groq LLM.
Includes explicit per-idea status logging (response received, JSON parsed, fallback status).
"""

import os
import json
import re
import time
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


# Primary and backup model pool available on the Groq key
MODELS_TO_TRY = [
    "qwen/qwen3.8-27b",
    "allam-2-7b",
    "groq/compound-mini",
]


def _groq_call_with_model_fallback(messages: list[dict], max_tokens: int = 512, temperature: float = 0.0) -> tuple[str, str]:
    """
    Attempts to call Groq using primary model with automatic fallback to secondary models
    and exponential backoff on 429 rate limits. Returns (response_text, model_used).
    """
    client = get_groq_client()
    last_exc = None

    for model in MODELS_TO_TRY:
        for attempt in range(2):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return resp.choices[0].message.content, model
            except Exception as exc:
                last_exc = exc
                err_str = str(exc).lower()
                if "429" in err_str or "rate limit" in err_str or "rate_limit" in err_str:
                    wait = 2 ** attempt
                    time.sleep(wait)
                else:
                    break

    raise last_exc


_EXTRACTION_SYSTEM_PROMPT = """\
Extract structured information from a startup idea for market research purposes. Respond ONLY with valid JSON, no markdown fences: {"product_name": "..." (use provided name if given, else infer a short name), "industry": "...", "target_audience": "...", "core_problem": "one sentence describing the actual problem being solved", "keywords": ["...", "...", "..."] (3-5 specific domain terms, not generic words like 'app' or 'platform')}
"""


class IdeaExtractionAgent:
    """Agent responsible for understanding and structuring a startup idea."""

    def _fallback_extraction(
        self,
        idea: str,
        product_name: str | None = None,
        industry: str | None = None,
        target_audience: str | None = None,
        reason: str = "Unknown error",
    ) -> dict:
        """Deterministic fallback if Groq is unavailable or parsing fails."""
        # Strip common conversational starters
        cleaned = re.sub(
            r'^(i want to (build|create|make|launch|develop|start)\s+|'
            r'(a|an )?[a-z]+ (app|platform|tool|service|system|web app|website|marketplace|saas|startup|product|solution) (that|which|to|for|helping)\s+|'
            r'(a|an) (startup|product|solution) (that|to|for)\s+)',
            '', idea.strip(), flags=re.IGNORECASE
        )
        words = [w for w in re.findall(r'[a-zA-Z0-9]+', cleaned) if len(w) > 2]
        generic = {
            "app", "platform", "tool", "service", "system", "that", "helps", "help", "with", "for",
            "and", "the", "you", "your", "our", "their", "user", "users", "people", "built", "designed"
        }
        filtered_words = [w.lower() for w in words if w.lower() not in generic]
        inferred_keywords = filtered_words[:4] or [w.lower() for w in words[:4]]

        inferred_name = product_name.strip() if product_name and product_name.strip() else (" ".join(inferred_keywords[:2]).title() or "Startup")
        inferred_industry = industry.strip() if industry and industry.strip() else "Technology / Software"
        inferred_audience = target_audience.strip() if target_audience and target_audience.strip() else "General Consumers / Businesses"

        print(f"  [IdeaExtractionAgent] Fallback triggered: YES | Reason: {reason}")
        return {
            "product_name": inferred_name,
            "industry": inferred_industry,
            "target_audience": inferred_audience,
            "core_problem": f"Solving user challenges regarding: {idea.strip()}",
            "keywords": inferred_keywords,
        }

    def extract(
        self,
        idea: str,
        product_name: str | None = None,
        industry: str | None = None,
        target_audience: str | None = None,
    ) -> dict:
        """
        Takes raw startup idea inputs and returns a structured dictionary:
        {
            "product_name": str,
            "industry": str,
            "target_audience": str,
            "core_problem": str,
            "keywords": list[str]
        }
        """
        user_parts = [f"Idea: {idea}"]
        if product_name and product_name.strip():
            user_parts.append(f"Explicit Product Name: {product_name.strip()}")
        if industry and industry.strip():
            user_parts.append(f"Explicit Industry: {industry.strip()}")
        if target_audience and target_audience.strip():
            user_parts.append(f"Explicit Target Audience: {target_audience.strip()}")
        user_msg = "\n".join(user_parts)

        try:
            raw, model_used = _groq_call_with_model_fallback(
                messages=[
                    {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=512,
            )
            print(f"  [IdeaExtractionAgent] (a) Got Groq response from model: '{model_used}'")

            # Clean markdown fences or think tags
            content = raw.strip()
            if "<think>" in content and "</think>" in content:
                content = content.split("</think>")[-1].strip()
            if content.startswith("```"):
                content = re.sub(r'^```[a-z]*\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

            parsed = json.loads(content)
            print(f"  [IdeaExtractionAgent] (b) Parsed successfully as JSON: {list(parsed.keys())}")
            print("  [IdeaExtractionAgent] (c) Fallback triggered: NO (Groq LLM succeeded)")

            result = {
                "product_name": product_name.strip() if product_name and product_name.strip() else parsed.get("product_name", "Startup"),
                "industry": industry.strip() if industry and industry.strip() else parsed.get("industry", "Software"),
                "target_audience": target_audience.strip() if target_audience and target_audience.strip() else parsed.get("target_audience", "Target Market"),
                "core_problem": parsed.get("core_problem", idea),
                "keywords": parsed.get("keywords", []),
            }

            if not isinstance(result["keywords"], list) or not result["keywords"]:
                result["keywords"] = [w for w in re.findall(r'[a-zA-Z]{3,}', idea)[:4]]

            return result

        except Exception as exc:
            reason = f"{type(exc).__name__}: {str(exc)}"
            return self._fallback_extraction(idea, product_name, industry, target_audience, reason=reason)
