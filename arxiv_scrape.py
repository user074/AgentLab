import arxiv
#create search query
search = arxiv.Search(
  query = "computer vision machine learning",
  max_results = 10,
  sort_by = arxiv.SortCriterion.SubmittedDate
)
#get results
for result in arxiv.Client().results(search):
  print(result.title)
  print(result.pdf_url)

#download pdf example will download the first result
paper = next(arxiv.Client().results(search))
paper.download_pdf(filename="downloaded-paper.pdf")

