import arxiv
#create search query
# class paper_search:
#   def __init__(self, max_result=10,sort_by=arxiv.SortCriterion.SubmittedDate):
#     self.max_result = max_result
#     self.sort_by=sort_by

def search_arxiv(query, max_result=10, sort_by=arxiv.SortCriterion.SubmittedDate):
    search = arxiv.Search(query=query, max_results=max_result, sort_by=sort_by)
    return search

def get_arxiv_results(search, download=False):
    papers_title = []
    papers_url = []
    
    for result in arxiv.Client().results(search):
        papers_title.append(result.title)
        papers_url.append(result.pdf_url)
        
        if download:
            result.download_pdf(filename=f"{result.title}.pdf")
    
    return papers_title, papers_url

#download pdf example will download the first result
# paper = next(arxiv.Client().results(search))
# paper.download_pdf(filename="downloaded-paper.pdf")

