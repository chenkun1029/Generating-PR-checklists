import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import torch


def extract_features(model, tokenizer, text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()


def classify_text(model, tokenizer, text):
    # Tokenize and encode the text
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)

    # Make prediction
    with torch.no_grad():
        outputs = model(**inputs)

    # Get predicted class
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    class_labels = ["test", "documentation", "contributing", "title",
                    "code style", "branch", "cla", "commit message", "description"]

    if 0 <= predicted_class < len(class_labels):
        return class_labels[predicted_class]
    else:
        return "not_matched"


def process_file(input_file, output_csv):
    # Load the pre-trained model and tokenizer
    model_name = 'bert-base-uncased'
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)

    # Read the input file
    df = pd.read_csv(input_file)
    sentence_features = []

    # Extract features for each sentence
    for sentence in df['text']:
        features = extract_features(model, tokenizer, sentence)
        sentence_features.append(features)
    features = sentence_features

    # Train and evaluate a classifier
    labels = df['label'].tolist()
    classifier, accuracy = train_and_evaluate(features, labels)

    # Classify each sentence and create a new column for predicted class
    df['predicted_class'] = df['text'].apply(lambda x: classify_text(model, tokenizer, x))

    df.to_csv(output_csv, index=False)


def train_and_evaluate(features, labels):
    # Train a simple logistic regression classifier
    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(features, labels)

    # Evaluate on the training set
    predictions = classifier.predict(features)
    accuracy = accuracy_score(labels, predictions)

    return classifier, accuracy


if __name__ == '__main__':
    process_file('your_input_file.csv', 'output_classification.csv')
