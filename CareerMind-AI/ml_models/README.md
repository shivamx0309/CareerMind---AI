# Machine Learning Models (`ml_models/`)

## Overview
Local storage and registry for serialized model artifacts, training checkpoints, and pre-trained weights.

## Subdirectories
- `checkpoints/`: Intermediate training checkpoints and optimization states.
- `fine_tuned/`: Fine-tuned NER and domain-adapted transformer models.
- `pretrained/`: Downloaded base models and tokenizers cached locally.

*Note: Heavy model weights (`.bin`, `.pt`, `.safetensors`) are ignored by Git.*
