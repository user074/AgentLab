import os
import pandas as pd
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline
import textract

def set_openai_api_key(api_key: str):
    os.environ["OPENAI_API_KEY"] = api_key

# Set your OpenAI API key
set_openai_api_key('your-api-key')

def read_pdf(file_path: str):
    """
    Read a PDF file and extract text using GPT-3.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    doc = textract.process(file_path)
    text = doc.decode('utf-8')
    return text


def query(text: str, question: str) -> str:
    """
    Query the given text with a question using GPT-2 and return the result.

    Args:
        text (str): The text to query against.
        question (str): The question to query with.

    Returns:
        str: The result of the query.
    """
    # Initialize the GPT-2 model and question answering pipeline
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

    # Generate an answer using GPT-3
    answer = qa_pipeline(question=question, context=text)

    return answer['answer']

