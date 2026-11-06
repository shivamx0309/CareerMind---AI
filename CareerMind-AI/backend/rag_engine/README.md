# RAG Knowledge Engine (`backend/rag_engine`)

## Overview
The Retrieval-Augmented Generation (RAG) Engine grounds AI generation in authoritative career taxonomies, interview guides, and industry benchmarks.

## Responsibilities
- **Vector Store Orchestration**: Interface with ChromaDB / Qdrant for semantic vector indexing.
- **Document Chunking & Hybrid Search**: Implement semantic chunking and BM25 + dense vector hybrid search for accurate knowledge retrieval.
- **Context Injection**: Retrieve real-time industry benchmark context and inject into LLM prompts for grounded career recommendations.
