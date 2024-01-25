import arxiv

search = arxiv.Search(
  query = "3D generation",
  max_results = 100,
  sort_by = arxiv.SortCriterion.SubmittedDate
)
for result in search.results():
  print(result.entry_id, '->', result.title)