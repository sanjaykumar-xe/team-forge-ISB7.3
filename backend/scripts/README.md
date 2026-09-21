# Backend Scripts & Benchmark Suite

This directory contains executable validation, regression, and benchmarking scripts used to verify system accuracy, anti-hallucination guarantees, agent tool-calling, and live API endpoints.

---

## 📋 Available Scripts

| Script | Purpose & Description | Execution Command |
| :--- | :--- | :--- |
| **`smoke_test.py`** | Quick sanity check verifying FastAPI health endpoint and basic agent initialization. | `python backend/scripts/smoke_test.py` |
| **`test_milestone2_e2e.py`** | End-to-end integration test validating sequential agent pipeline against mock/live payloads. | `python backend/scripts/test_milestone2_e2e.py` |
| **`run_eval.py`** | System-wide benchmark evaluating validation quality, schema conformance, and latency metrics across benchmark ideas. | `python backend/scripts/run_eval.py` |
| **`run_agentic_verification.py`** | Deep verification of CrewAI autonomous tool-calling, verifying that `MarketResearchAgent` executes Tavily search tools. | `python backend/scripts/run_agentic_verification.py` |
| **`run_evidence_verification.py`** | Verification of anti-hallucination grounding: checks that numerical claims and competitor names correlate directly with search sources. | `python backend/scripts/run_evidence_verification.py` |
| **`run_5_regression_ideas.py`** | Regression test executing the full 9-stage pipeline across 5 diverse benchmark ideas (B2B, B2C, HealthTech, EdTech, FinTech). | `python backend/scripts/run_5_regression_ideas.py` |

---

## 🚀 Usage

Ensure your virtual environment is activated and `.env` is configured with valid `GROQ_API_KEY` and `TAVILY_API_KEY`:

```bash
# From workspace root
python backend/scripts/smoke_test.py
python backend/scripts/run_agentic_verification.py
```
