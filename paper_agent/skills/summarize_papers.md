# Skill: summarize_papers

## goal
Generate concise research summaries and method highlights for papers.

## input
- title
- abstract
- optional PDF text

## output
- summary
- highlights
- method_tags

## instruction
Use the LLM when available. If the model is unavailable, produce a heuristic fallback summary from title and abstract.

## prompt template
Summarize this paper with task, method, contribution, limitation, and one-sentence highlight:
`{paper_text}`
