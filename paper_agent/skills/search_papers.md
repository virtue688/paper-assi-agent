# Skill: search_papers

## goal
Retrieve papers from arXiv and Semantic Scholar for a keyword and optional time range.

## input
- keyword: research topic
- years: optional year window
- top_k: maximum number of papers

## output
- title
- abstract
- url
- authors
- year
- venue
- source
- pdf_url

## instruction
Search multiple sources, normalize into the unified Paper schema, and deduplicate by paper id or normalized title.

## prompt template
Find recent papers about `{keyword}` in the last `{years}` years and preserve source metadata.
