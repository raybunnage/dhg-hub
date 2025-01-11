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

SOURCE_QUERY_PROMPT = """Please analyze this academic paper and provide the following information in a JSON format:
{
    "title": "full paper title",
    "authors": ["list of authors"],
    "journal": "journal name",
    "publication_date": "publication date (YYYY-MM-DD if available, else YYYY-MM)",
    "doi": "DOI if available",
    "volume": "volume number if available",
    "issue": "issue number if available",
    "pages": "page range if available"
}
Please ensure the output is valid JSON format."""

PAPER_ANALYSIS_PROMPT = """You are a research paper analysis expert. Before providing your critique, carefully examine and reflect on the paper's content, methodology, and results. 

Analysis Steps:
1. First, thoroughly understand the paper's:
   - Core research questions and objectives
   - Theoretical framework
   - Methodological approach
   - Key findings and their implications
   
2. Then critically evaluate:
   - How well the results address the research questions
   - Whether the conclusions logically follow from the evidence
   - If alternative interpretations were adequately considered
   - The broader implications for the field

Please provide your analysis in the following JSON format:
{
    "paper_overview": {
        "research_objectives": "clear statement of the paper's goals",
        "theoretical_framework": "description of underlying theory",
        "methodology_summary": "overview of methods used"
    },
    "results_analysis": {
        "key_findings": [
            "main result 1",
            "main result 2"
        ],
        "evidence_quality": "assessment of the evidence strength",
        "alternative_explanations": "discussion of other possible interpretations"
    },
    "strengths": [
        {
            "aspect": "specific strength area",
            "description": "detailed explanation",
            "impact": "why this strengthens the paper"
        }
    ],
    "weaknesses": [
        {
            "aspect": "specific weakness area",
            "description": "detailed explanation",
            "impact": "why this weakens the paper"
        }
    ],
    "improvement_suggestions": [
        {
            "area": "aspect requiring improvement",
            "current_state": "description of current approach",
            "recommended_changes": "specific detailed changes",
            "implementation_steps": ["step 1", "step 2", ...],
            "rationale": "comprehensive explanation of why these changes would improve the paper",
            "expected_impact": "specific benefits after implementation"
        }
    ],
    "restructuring_recommendations": {
        "organization": [
            {
                "section": "specific section",
                "current_issues": "problems with current structure",
                "suggested_changes": "detailed restructuring suggestions",
                "rationale": "why these changes would improve readability/flow"
            }
        ],
        "flow_improvements": "suggestions for better logical progression",
        "clarity_enhancements": "recommendations for clearer presentation"
    }
}

Guidelines for analysis:
1. Evaluate methodology rigor and appropriateness:
   - Research design suitability
   - Method implementation quality
   - Controls and validation approaches
   
2. Assess data analysis depth:
   - Statistical method appropriateness
   - Analysis comprehensiveness
   - Robustness checks
   - Treatment of uncertainties/limitations

3. Review research objectives clarity:
   - Hypothesis formulation
   - Question specificity
   - Alignment with methodology

4. Examine conclusion strength:
   - Evidence support level
   - Alternative explanation consideration
   - Limitation acknowledgment
   - Future direction identification

5. Evaluate field contribution:
   - Novelty assessment
   - Impact potential
   - Knowledge gap addressing
   - Theoretical/practical implications

6. Assess presentation quality:
   - Logical structure
   - Argument progression
   - Visual aid effectiveness
   - Technical clarity

Please ensure all responses are:
- Specific and actionable
- Well-justified with clear reasoning
- Supported by examples from the paper
- Constructive and improvement-focused
- Considerate of both theoretical and practical implications"""
