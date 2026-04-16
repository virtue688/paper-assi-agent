# Skill: build_review

## goal
Build a structured academic-style literature review for a research keyword.

## input
- keyword
- enriched paper list
- method tags

## output
- background
- problem definition
- technical route taxonomy
- representative methods
- datasets and metrics
- challenges
- future directions
- references

## instruction
Search first, aggregate evidence, classify technical routes, then synthesize a review. Do not simply concatenate abstracts.

## prompt template
Write a literature review for `{keyword}` using these papers: `{papers}`.
