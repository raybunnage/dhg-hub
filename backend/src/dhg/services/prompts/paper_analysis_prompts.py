"""Prompts for paper analysis service."""

STRENGTH_WEAKNESS_PROMPT = """
Analyze the provided academic paper and identify its key strengths and weaknesses. 
Focus on:
1. Methodology
2. Data analysis
3. Research design
4. Writing clarity
5. Results interpretation
6. Literature review

Format your response in markdown with two sections:
## Strengths
- [Strength points]

## Weaknesses
- [Weakness points]
"""

IMPROVEMENT_SUGGESTIONS_PROMPT = """
Based on the identified strengths and weaknesses, provide specific recommendations 
for improving the paper. For each suggestion:

1. Clearly state the recommended change
2. Explain the rationale behind it
3. Describe the expected impact

Format each suggestion as:
## Recommendation
[Specific change to make]

## Rationale
[Explanation of why this change would improve the paper]

## Expected Impact
[How this change would strengthen the paper]
"""

REWRITE_PROMPT = """
Rewrite the provided section of the paper incorporating the suggested improvements. 
Maintain the original paper's voice and technical depth while implementing the 
recommended changes. Focus on:

1. Clarity of expression
2. Technical accuracy
3. Logical flow
4. Integration of improvements

The rewrite should be thorough but preserve the paper's core findings and methodology.
"""

RATIONALE_DOCUMENT_PROMPT = """
Create a comprehensive document explaining the reasoning behind all suggested 
improvements to the paper. Include:

1. Overview of the paper's current state
2. Summary of major improvement areas
3. Detailed explanation of each suggestion
4. Expected impact on paper quality
5. Implementation considerations

Format in markdown with clear sections and subsections.
"""
