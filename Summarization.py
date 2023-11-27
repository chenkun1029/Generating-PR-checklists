import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from language_tool_python import LanguageTool
import pandas as pd


def generate_summary(model, tokenizer, article, keywords=None):
    # Tokenize the input article
    inputs = tokenizer([article], max_length=1024, return_tensors='pt', truncation=True)

    # Introduce keywords to the input for better focus (customize as needed)
    if keywords:
        inputs['input_ids'] = introduce_keywords(inputs['input_ids'], tokenizer, keywords)

    # Generate summary with adjusted parameters
    summary_ids = model.generate(
        inputs['input_ids'],
        num_beams=4,
        min_length=50,
        max_length=200,
        length_penalty=2.0,
        early_stopping=True
    )

    # Decode and post-process the summary
    summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    # Additional post-processing steps
    summary = remove_redundant_sentences(summary)
    summary = correct_grammar(summary)

    return summary


def introduce_keywords(input_ids, tokenizer, keywords):
    # Introduce keywords to the input text (customize as needed)
    keyword_tokens = tokenizer(keywords, return_tensors='pt')['input_ids']

    # Concatenate the keyword tokens to the original input
    input_ids = torch.cat([input_ids, keyword_tokens], dim=1)
    return input_ids


def remove_redundant_sentences(text):
    sentences = text.split('.')
    filtered_sentences = [sentences[i] for i in range(len(sentences))
                          if i == 0 or sentences[i] != sentences[i - 1]]
    return '. '.join(filtered_sentences)


def correct_grammar(text):
    tool = LanguageTool('en-US')

    matches = tool.check(text)
    corrected_text = tool.correct(text, matches)

    return corrected_text


def process_csv(input_csv, output_csv):
    model_path = 'models/huggingface/bart_large_cnn'  # Local model path
    model = BartForConditionalGeneration.from_pretrained(model_path)
    tokenizer = BartTokenizer.from_pretrained(model_path)

    keywords = ["test", "documentation", "contributing", "title",
                "code style", "branch", "cla", "commit message", "description"]

    df = pd.read_csv(input_csv)

    df['summary'] = df['text'].apply(lambda x: generate_summary(model, tokenizer, x))
    df.to_csv(output_csv, index=False)


if __name__ == '__main__':
    process_csv('text_for_summarization.csv', 'output_summary.csv')
