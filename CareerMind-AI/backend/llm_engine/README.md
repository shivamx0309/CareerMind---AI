# LLM Engine (`backend/llm_engine`)

## Overview
The LLM Engine manages generative AI operations, local LLM orchestration via Ollama, prompt engineering, and commercial API fallbacks.

## Responsibilities
- **Local Inference (Ollama / vLLM)**: Run privacy-compliant local LLMs (Llama 3, Mistral 7B) for candidate analysis without cloud data leakage.
- **Cloud Fallbacks**: Seamless routing to OpenAI (GPT-4o) or Google Gemini when local compute is constrained or high reasoning is requested.
- **Prompt Registry & Structured Output**: Enforce strict JSON output schemas via instructor / Pydantic for resume critique, summary generation, and cover letters.
