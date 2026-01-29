import os
from functools import lru_cache

import torch
from transformers import AutoTokenizer, RobertaForSequenceClassification

MODEL_NAME = os.getenv("HF_MODEL_NAME", "alxdev/echocheck-political-stance")
MAX_LENGTH = 512
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LABEL_MAP = {0: "center", 1: "left", 2: "right"}


class PoliticalClassifier:
    """
    Singleton classifier that loads model once and reuses for all predictions
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        print(f"Loading model from HuggingFace: {MODEL_NAME}")
        print(f"Device: {DEVICE}")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.to(DEVICE)
        self.model.eval()

        print("Model loaded succesfully")
        self._initialized = True

    def predict(self, text: str) -> dict:
        """
        Predict political stance of the given text.

        Args:
            text: The text to classify (article, statement, etc.)

        Returns:
            Dictionary containing:
            - prediction: The predicted class (left, center, right)
            - confidence: Confidence score for the prediction
            - probabilities: Probability scores for all classes
        """

        inputs = self.tokenizer(
            text,
            max_length=MAX_LENGTH,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        inputs = {key: value.to(DEVICE) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)

        probs = probabilities.cpu().numpy()[0]
        predicted_class = probs.argmax()

        return {
            "prediction": LABEL_MAP[predicted_class],
            "confidence": float(probs[predicted_class]),
            "probabilities": {
                "center": float(probs[0]),
                "left": float(probs[1]),
                "right": float(probs[2]),
            },
        }


@lru_cache
def get_classifier() -> PoliticalClassifier:
    """Get or create the classifier singleton instance"""
    return PoliticalClassifier()
