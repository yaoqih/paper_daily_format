from datasets import load_dataset
import evaluate
from transformers import (
    AutoTokenizer,
    TFAutoModelForSequenceClassification,
)

raw_datasets = load_dataset("glue", "mnli")

model_checkpoint = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)


def preprocess_function(examples):
    return tokenizer(examples["premise"], examples["hypothesis"], truncation=True)


tokenized_datasets = raw_datasets.map(preprocess_function, batched=True)

train_dataset = tokenized_datasets["train"].to_tf_dataset(
    columns=["input_ids", "labels"], batch_size=16, shuffle=True
)

validation_dataset = tokenized_datasets["validation_matched"].to_tf_dataset(
    columns=["input_ids", "labels"], batch_size=16, shuffle=True
)

model = TFAutoModelForSequenceClassification.from_pretrained(model_checkpoint)

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam")

model.fit(train_dataset)