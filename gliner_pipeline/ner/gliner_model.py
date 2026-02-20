from gliner import GLiNER
import torch
from gliner_pipeline.config import MODEL_NAME, DEVICE

class GLiNERService:

    def __init__(self):
        self.model = GLiNER.from_pretrained(MODEL_NAME)
        self.model.model = self.model.model.to(DEVICE)

    def predict(self, text: str, labels):
        return self.model.predict_entities(text, labels)