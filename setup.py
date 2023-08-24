from setuptools import setup, find_packages

setup(
    name="agentlab",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "langchain==0.0.150",
        "pypdf",
        "pandas",
        "matplotlib",
        "tiktoken",
        "textract",
        "transformers",
        "openai",
        "faiss-cpu",
    ],
)
