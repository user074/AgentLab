import os
import pandas as pd
from transformers import GPT2TokenizerFast
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import textract

def set_openai_api_key(api_key: str):
    """Set the OpenAI API key."""
    os.environ["OPENAI_API_KEY"] = api_key

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

def read_pdf(file_path: str):
    """
    Read a PDF file and return a FAISS vector database.
    
    Args:
        file_path (str): Path to the PDF file.
    
    Returns:
        FAISS: A vector database that can be queried for similarity.
    """
    doc = textract.process(file_path)
    
    with open('temp_file.txt', 'w') as f:
        f.write(doc.decode('utf-8'))

    with open('temp_file.txt', 'r') as f:
        text = f.read()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=24,
        length_function=count_tokens,
    )
    chunks = text_splitter.create_documents([text])

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(chunks, embeddings)
    return db

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def query(db, question: str) -> str:
    """
    Query the given database with a question and return the result.

    Args:
        db: The FAISS vector database to query against.
        question (str): The question to query with.

    Returns:
        str: The result of the query.
    """
    chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
    docs = db.similarity_search(question)
    return chain.run(input_documents=docs, question=question)

