# NLP Engine (`backend/nlp_engine`)

## Overview
The NLP Engine performs natural language preprocessing, tokenization, Named Entity Recognition (NER), and skill taxonomy normalization.

## Responsibilities
- **Text Normalization**: Stopword removal, lemmatization, section boundary normalization.
- **Named Entity Recognition (NER)**: Custom spaCy and HuggingFace pipelines trained to extract candidate names, degrees, institutions, job titles, and organizations.
- **Skill Extraction & Taxonomy Alignment**: Extract technical and soft skills, cross-referencing against standard taxonomies (ESCO, O*NET, Stack Overflow Skill Graph).
