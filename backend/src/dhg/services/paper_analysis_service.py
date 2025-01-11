import logging
import os
from typing import Dict, List, Optional
from pathlib import Path
from dhg.services.pdf_anthropic import PdfAnthropic

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PaperAnalysisService:
    def __init__(self, anthropic_service):
        """Initialize the service."""
        self.anthropic_service = anthropic_service
        logger.info("PaperAnalysisService initialized")

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        logger.info(f"Extracting text from PDF: {pdf_path}")
        # You'll need to implement PDF text extraction here
        # Consider using libraries like PyPDF2 or pdfplumber
        # For now, returning mock text
        return "Sample paper text..."

    def _create_analysis_prompt(self, paper_text: str) -> str:
        """Create the prompt for paper analysis."""
        return f"""You are a research paper analysis expert. Please analyze the following academic paper and identify its key strengths and weaknesses. 
Focus on methodology, research design, data analysis, conclusions, and overall scientific rigor.

Paper text:
{paper_text}

Please provide your analysis in the following JSON format:
{{
    "strengths": [
        "strength 1",
        "strength 2",
        ...
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2",
        ...
    ]
}}
"""

    def extract_strengths_and_weaknesses(self, pdf_path: str) -> Dict:
        """Extract strengths and weaknesses from the paper using Claude."""
        logger.info(f"Extracting strengths and weaknesses from: {pdf_path}")

        try:
            pdf_processor = PdfAnthropic(self.anthropic_service, pdf_path)
            
            prompt = """You are a research paper analysis expert. Please analyze this academic paper and identify its key strengths and weaknesses. 
Focus on methodology, research design, data analysis, conclusions, and overall scientific rigor.

Please provide your analysis in the following JSON format:
{
    "strengths": [
        "strength 1",
        "strength 2",
        ...
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2",
        ...
    ]
}"""

            responses = pdf_processor.process_pdf(custom_prompts=[prompt])
            
            try:
                analysis = eval(responses[0])  # Convert string to dict
                return analysis
            except Exception as e:
                logger.error(f"Error parsing Claude response: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error in extract_strengths_and_weaknesses: {str(e)}")
            raise

    def generate_improvement_suggestions(self, analysis: Dict) -> List:
        """Generate improvement suggestions based on analysis using Claude."""
        logger.info("Generating improvement suggestions")

        try:
            prompt = f"""Based on the following analysis of a research paper, generate specific improvement suggestions.
            
Analysis:
Strengths:
{chr(10).join(f"- {s}" for s in analysis.get("strengths", []))}

Weaknesses:
{chr(10).join(f"- {w}" for w in analysis.get("weaknesses", []))}

Provide suggestions in JSON format as a list of objects with 'recommendation' and 'rationale' fields."""

            responses = self.pdf_processor.process_pdf(custom_prompts=[prompt])
            
            try:
                suggestions = eval(responses[0])
                return suggestions
            except Exception as e:
                logger.error(f"Error parsing suggestions response: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            raise

    def rewrite_paper_with_improvements(self, pdf_path: str, suggestions: List) -> str:
        """Rewrite paper content with suggested improvements."""
        logger.info(f"Rewriting paper with improvements from: {pdf_path}")

        rewritten_content = "# Improved Paper\n\n"
        rewritten_content += (
            "This is a placeholder for the rewritten paper content.\n\n"
        )

        for suggestion in suggestions:
            rewritten_content += f"## Implementing: {suggestion['recommendation']}\n"
            rewritten_content += f"{suggestion['rationale']}\n\n"

        return rewritten_content

    def generate_improvement_rationale(self, suggestions: List) -> str:
        """Generate detailed rationale for improvements."""
        logger.info("Generating improvement rationale")

        rationale = "# Improvement Rationale\n\n"
        for suggestion in suggestions:
            rationale += f"## {suggestion['recommendation']}\n"
            rationale += f"{suggestion['rationale']}\n\n"

        return rationale

    def save_analysis_outputs(
        self,
        output_dir: str,
        analysis: Dict,
        suggestions: List,
        rewritten_content: str,
        rationale: str,
    ) -> bool:
        """Save all analysis outputs to files."""
        logger.info(f"Saving analysis outputs to: {output_dir}")

        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Save analysis
            with open(Path(output_dir) / "analysis.md", "w") as f:
                f.write("# Analysis\n\n## Strengths\n")
                for strength in analysis["strengths"]:
                    f.write(f"- {strength}\n")
                f.write("\n## Weaknesses\n")
                for weakness in analysis["weaknesses"]:
                    f.write(f"- {weakness}\n")

            # Save suggestions
            with open(Path(output_dir) / "suggestions.md", "w") as f:
                f.write("# Improvement Suggestions\n\n")
                for suggestion in suggestions:
                    f.write(f"## {suggestion['recommendation']}\n")
                    f.write(f"{suggestion['rationale']}\n\n")

            # Save rewritten paper
            with open(Path(output_dir) / "rewritten_paper.md", "w") as f:
                f.write(rewritten_content)

            # Save rationale
            with open(Path(output_dir) / "improvement_rationale.md", "w") as f:
                f.write(rationale)

            return True
        except Exception as e:
            logger.error(f"Error saving outputs: {str(e)}")
            return False

    def analyze_paper(self, pdf_path: str, output_dir: str) -> Dict:
        """Run the complete paper analysis pipeline."""
        logger.info(f"Starting paper analysis for: {pdf_path}")

        try:
            # Initialize PDF processor
            self.pdf_processor = PdfAnthropic(self.anthropic_service, pdf_path)
            
            # Run analysis pipeline
            analysis = self.extract_strengths_and_weaknesses(pdf_path)
            suggestions = self.generate_improvement_suggestions(analysis)
            rewritten_content = self.rewrite_paper_with_improvements(
                pdf_path, suggestions
            )
            rationale = self.generate_improvement_rationale(suggestions)

            if self.save_analysis_outputs(
                output_dir, analysis, suggestions, rewritten_content, rationale
            ):
                return {
                    "analysis": str(Path(output_dir) / "analysis.md"),
                    "suggestions": str(Path(output_dir) / "suggestions.md"),
                    "rewritten_paper": str(Path(output_dir) / "rewritten_paper.md"),
                    "rationale": str(Path(output_dir) / "improvement_rationale.md"),
                }

            return {}  # Return empty dict instead of None

        except Exception as e:
            logger.error(f"Error in analyze_paper: {str(e)}")
            return {}  # Return empty dict instead of None


if __name__ == "__main__":
    # Import required service
    import os
    from dhg.services.anthropic_service import AnthropicService

    # Get API key from environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        exit(1)

    # Initialize services
    anthropic_service = AnthropicService(api_key=api_key)
    paper_analysis = PaperAnalysisService(anthropic_service)

    # Define paths
    pdf_path = "backend/tests/test_files/pdfs/long_covid_frontiers_2024_v1.pdf"
    output_dir = "backend/tests/services/paper_analysis"

    # Run analysis
    print(f"Analyzing paper: {pdf_path}")
    results = paper_analysis.analyze_paper(pdf_path, output_dir)

    if results:
        print("\nAnalysis completed successfully!")
        print("Output files:")
        for key, path in results.items():
            print(f"- {key}: {path}")
    else:
        print("\nAnalysis failed!")
