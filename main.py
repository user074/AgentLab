import argparse
import arxiv
import openai
import os
import tiktoken
from summarizer import *
from arxiv_scrape import *
# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"



def generate_summary(text):
    # Use OpenAI API to generate a summary
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        max_tokens=150
    )
    summary = response.choices[0].text.strip()
    return summary

def search_and_summarize(api_key,query, max_result=10, sort_by=arxiv.SortCriterion.SubmittedDate):
    openai.api_key=api_key
    # Search arXiv
    search_result = search_arxiv(query, max_result, sort_by)
    
    # Get results
    titles, urls = get_arxiv_results(search_result, download=False)
    
    # Generate summaries for each paper
    for title in titles:
        # You need to fetch the content of the paper for summarization
        # This is just a placeholder. You may need to fetch the abstract or full text of the paper.
        # Generate summary using OpenAI API
        summary_prep = summarize_text_file(f"{title}.pdf")
        summary=instruct_text_wfile(summary_prep,summary_instructions)
        strengths = instruct_text_wfile('condensed_condensed_paper.txt', strengths_instructions)
        weaknesses = instruct_text_wfile('condensed_condensed_paper.txt', weaknesses_instructions)

        final_summary = '**Summary**'+'\n'+summary + '\n\n' + '**Strengths**'+'\n'+strengths + '\n\n' + '**Weaknesses**'+'\n'+weaknesses

        with open('literature_review.txt', 'w') as file:
            file.write(final_summary)
                
def main():
    parser = argparse.ArgumentParser(description="Search arXiv and generate summaries of papers using OpenAI.")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("api_key", type=str, help="openai api key")
    parser.add_argument("--max_results", type=int, default=10, help="Maximum number of results")
    parser.add_argument("sort_by", type=str, default="submittedDate",
                        help="Sort criterion for search results")

    args = parser.parse_args()
    if args.sort_by=='submittedDate':
        sort_by=arxiv.SortCriterion.SubmittedDate
    search_and_summarize(args.api_key,args.query,args.max_results,sort_by)

if __name__ == "__main__":
    main()
