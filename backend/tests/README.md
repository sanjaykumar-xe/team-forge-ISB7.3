# Backend Automated Test Suite

This directory contains pytest test suites covering unit and integration testing of the backend agent pipeline, schemas, and services.

---

## 📋 Test Files

| Test File | Coverage |
| :--- | :--- |
| **`test_agents.py`** | Unit tests for individual agents (`IdeaExtractionAgent`, `MarketAnalysisAgent`, `CompetitorAnalysisAgent`, `SWOTAgent`, `MVPAgent`, `GTMAgent`). Tests mock LLM outputs and schema conformance. |
| **`test_milestone2.py`** | Integration tests validating multi-agent handoffs, data contract invariants, and pipeline error recovery. |

---

## 🚀 Running Tests

```bash
# Run all tests via pytest
pytest backend/tests -v

# Run a specific test module
pytest backend/tests/test_agents.py -v
```
