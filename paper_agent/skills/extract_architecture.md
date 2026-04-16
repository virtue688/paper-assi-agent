# Skill: extract_architecture

## goal
Extract or infer the model overview architecture.

## input
- paper metadata
- optional PDF path
- optional PDF text

## output
- architecture_image_path
- architecture_text

## instruction
Priority 1: try to extract a likely overview figure from early PDF pages when captions or page text mention overview, architecture, framework, pipeline, or model.

Priority 2: if extraction fails, generate a structured text fallback describing input, backbone, core modules, and output.

## prompt template
Describe the architecture of this paper with input, backbone, core modules, and output:
`{paper_text}`
