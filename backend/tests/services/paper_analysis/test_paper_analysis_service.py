import unittest
from pathlib import Path
import os
from typing import List, Dict
import logging
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from backend.src.dhg.services.paper_analysis_service import PaperAnalysisService
from backend.src.dhg.services.anthropic_service import AnthropicService

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestPaperAnalysisService(unittest.TestCase):
    def setUp(self):
        """Initialize the service and test data."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_service = AnthropicService(api_key)
        self.paper_service = PaperAnalysisService(self.anthropic_service)

        # Set up test paths using Path for cross-platform compatibility
        self.test_dir = Path(
            __file__
        ).parent.parent.parent  # Navigate to backend/tests/
        self.test_pdf_path = (
            self.test_dir / "test_files" / "pdfs" / "long_covid_frontiers_2024_v1.pdf"
        )
        self.output_dir = self.test_dir / "output" / "paper_analysis"

        logger.info(f"Test directory: {self.test_dir}")
        logger.info(f"Test PDF path: {self.test_pdf_path}")
        logger.info(f"Output directory: {self.output_dir}")

        # Create test directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.test_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a test PDF if it doesn't exist
        if not self.test_pdf_path.exists():
            with open(self.test_pdf_path, "w") as f:
                f.write("Test PDF content")

    def tearDown(self):
        """Clean up test files after each test."""
        # Remove test output files
        if self.output_dir.exists():
            for file in self.output_dir.glob("*.md"):
                file.unlink(missing_ok=True)

    def test_extract_strengths_and_weaknesses(self):
        """Test extraction of paper strengths and weaknesses."""
        try:
            result = self.paper_service.extract_strengths_and_weaknesses(
                str(self.test_pdf_path)
            )

            # Verify structure of returned data
            self.assertIsInstance(result, dict)
            self.assertIn("strengths", result)
            self.assertIn("weaknesses", result)
            self.assertIsInstance(result["strengths"], list)
            self.assertIsInstance(result["weaknesses"], list)

            # Verify content
            self.assertTrue(len(result["strengths"]) > 0)
            self.assertTrue(len(result["weaknesses"]) > 0)
        except Exception as e:
            self.fail(f"extract_strengths_and_weaknesses failed with error: {str(e)}")

    def test_generate_improvement_suggestions(self):
        """Test generation of improvement suggestions based on analysis."""
        try:
            analysis = {
                "strengths": ["Clear methodology", "Well-structured"],
                "weaknesses": ["Limited sample size", "Lack of statistical analysis"],
            }

            suggestions = self.paper_service.generate_improvement_suggestions(analysis)

            self.assertIsInstance(suggestions, list)
            self.assertTrue(len(suggestions) > 0)
            for suggestion in suggestions:
                self.assertIsInstance(suggestion, dict)
                self.assertIn("recommendation", suggestion)
                self.assertIn("rationale", suggestion)
        except Exception as e:
            self.fail(f"generate_improvement_suggestions failed with error: {str(e)}")

    def test_rewrite_paper_with_improvements(self):
        """Test paper rewriting with improvements."""
        try:
            suggestions = [
                {
                    "recommendation": "Expand sample size",
                    "rationale": "Increase statistical significance",
                }
            ]

            rewritten_content = self.paper_service.rewrite_paper_with_improvements(
                str(self.test_pdf_path), suggestions
            )

            self.assertIsInstance(rewritten_content, str)
            self.assertTrue(len(rewritten_content) > 0)
        except Exception as e:
            self.fail(f"rewrite_paper_with_improvements failed with error: {str(e)}")

    def test_generate_improvement_rationale(self):
        """Test generation of improvement rationale document."""
        try:
            suggestions = [
                {
                    "recommendation": "Expand sample size",
                    "rationale": "Increase statistical significance",
                }
            ]

            rationale = self.paper_service.generate_improvement_rationale(suggestions)

            self.assertIsInstance(rationale, str)
            self.assertTrue(len(rationale) > 0)
        except Exception as e:
            self.fail(f"generate_improvement_rationale failed with error: {str(e)}")

    def test_save_analysis_outputs(self):
        """Test saving all analysis outputs to files."""
        try:
            analysis = {
                "strengths": ["Clear methodology"],
                "weaknesses": ["Limited sample size"],
            }
            suggestions = [
                {
                    "recommendation": "Expand sample size",
                    "rationale": "Increase statistical significance",
                }
            ]
            rewritten_content = "Rewritten paper content..."
            rationale = "Improvement rationale..."

            success = self.paper_service.save_analysis_outputs(
                str(self.output_dir),
                analysis,
                suggestions,
                rewritten_content,
                rationale,
            )

            self.assertTrue(success, "save_analysis_outputs should return True")

            # Verify files were created
            expected_files = [
                "analysis.md",
                "suggestions.md",
                "rewritten_paper.md",
                "improvement_rationale.md",
            ]

            for file in expected_files:
                file_path = self.output_dir / file
                self.assertTrue(
                    file_path.exists(), f"Expected file {file} was not created"
                )
                self.assertTrue(file_path.stat().st_size > 0, f"File {file} is empty")
        except Exception as e:
            self.fail(f"save_analysis_outputs failed with error: {str(e)}")

    def test_full_paper_analysis_pipeline(self):
        """Test the complete paper analysis pipeline."""
        try:
            output_files = self.paper_service.analyze_paper(
                str(self.test_pdf_path), str(self.output_dir)
            )

            self.assertIsInstance(output_files, dict)
            self.assertIn("analysis", output_files)
            self.assertIn("suggestions", output_files)
            self.assertIn("rewritten_paper", output_files)
            self.assertIn("rationale", output_files)

            for file_path in output_files.values():
                self.assertTrue(Path(file_path).exists())
                self.assertTrue(Path(file_path).stat().st_size > 0)
        except Exception as e:
            self.fail(f"analyze_paper failed with error: {str(e)}")


if __name__ == "__main__":
    try:
        # Run tests without exit
        unittest.main(exit=False)
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise
