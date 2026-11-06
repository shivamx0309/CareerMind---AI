# Deep Learning Engine (`backend/dl_engine`)

## Overview
The Deep Learning Engine leverages neural networks, transformer architectures, and sentence embeddings to perform semantic analysis beyond keyword matching.

## Responsibilities
- **Semantic Embeddings**: Compute contextual vector representations of resumes and job descriptions using SentenceTransformers (`all-MiniLM-L6-v2`, `bge-base-en-v1.5`).
- **Bi-Encoder & Cross-Encoder Architectures**: Rapid retrieval candidate filtering via bi-encoders, followed by precise cross-encoder reranking.
- **PyTorch Model Pipeline**: Support custom PyTorch modules for deep semantic matching and domain adaptation.
