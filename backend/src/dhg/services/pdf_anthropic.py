import os
from anthropic import Anthropic
from anthropic.types import Message
import dotenv
import base64
import httpx
from typing import Optional, List, Dict, Union, Tuple, Any

from dhg.services.anthropic_service import AnthropicService


class PdfProcessingError(Exception):
    """Custom exception for PDF processing errors."""

    pass


class PdfAnthropic:
    def __init__(self, anthropic_service: "AnthropicService", pdf_path: str):
        self.anthropic_service = anthropic_service
        if not os.path.exists(pdf_path):
            raise PdfProcessingError("PDF file not found")
        self.pdf_path = pdf_path

        # Read and encode PDF once during initialization
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()
            self.pdf_base64 = base64.b64encode(pdf_content).decode()

    def process_pdf(self, custom_prompts: Optional[List[str]] = None) -> List[str]:
        """
        Process a PDF file with a series of prompts

        Args:
            custom_prompts: List of prompts to use. Cannot be None.

        Returns:
            List of responses from Claude
        """
        if custom_prompts is None:
            raise PdfProcessingError("custom_prompts cannot be None")

        responses = []
        messages = []

        # Initial message with PDF
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": custom_prompts[0]},
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": self.pdf_base64,
                        },
                    },
                ],
            }
        )

        # Process each prompt in sequence
        for i, prompt in enumerate(custom_prompts):
            if i > 0:  # Skip first prompt as it's already added
                messages.append(
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": responses[-1]}],
                    }
                )
                messages.append(
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                )

            response = self.anthropic_service.call_claude_pdf_with_messages(
                max_tokens=4096, messages=messages, temperature=0.0
            )
            responses.append(response)

        return responses


def test_source_query():
    """Test function to query source information from a specific PDF."""
    from dhg.services.anthropic_service import AnthropicService
    from dhg.services.prompts.paper_analysis_prompts import PAPER_ANALYSIS_PROMPT

    pdf_path = "backend/tests/test_files/pdfs/long_covid_frontiers_2024_v1.pdf"
    anthropic_service = AnthropicService()
    pdf_processor = PdfAnthropic(anthropic_service, pdf_path)

    # Pass the prompt directly to process_pdf
    responses = pdf_processor.process_pdf(custom_prompts=[PAPER_ANALYSIS_PROMPT])
    print("Source Information:")
    print(responses[0])
    return responses[0]


if __name__ == "__main__":
    test_source_query()
