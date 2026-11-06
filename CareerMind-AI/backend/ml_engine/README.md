# Machine Learning Engine (`backend/ml_engine`)

## Overview
The Machine Learning Engine provides classical machine learning pipelines, tabular candidate scoring, feature extraction, and classification models.

## Responsibilities
- **Feature Engineering**: Transform extracted resume metadata (years of experience, education tier, skill count, tenure stability) into structured feature vectors.
- **Resume Scoring & Ranking**: Train and infer using Scikit-learn, LightGBM, and XGBoost models for resume quality assessment.
- **Model Serialization**: Manage model serialization and artifact persistence (`.joblib` / `.pkl`).
