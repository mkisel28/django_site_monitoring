from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import os

BASE_DIR_CLASSIFICATION = os.path.dirname(os.path.abspath(__file__))

relative_path = "news-category-classification-distilbert"
ABSOLUTE_PATH = os.path.join(BASE_DIR_CLASSIFICATION, relative_path)

tokenizer = AutoTokenizer.from_pretrained(ABSOLUTE_PATH)
model = AutoModelForSequenceClassification.from_pretrained(ABSOLUTE_PATH, from_tf=True)

def classify(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    probabilities = torch.nn.functional.softmax(logits, dim=1)
    predicted_class_id = torch.argmax(probabilities, dim=1).item()
    predicted_label = model.config.id2label[predicted_class_id]
    return predicted_label
  