import pytest
from dhg.services.anthropic_service import AnthropicService
from dhg.services.pdf_anthropic import PdfAnthropic
from dhg.services.prompts.paper_analysis_prompts import SOURCE_QUERY_PROMPT


def test_source_query():
    """Test function to query source information from a specific PDF."""
    pdf_path = "backend/tests/test_files/pdfs/long_covid_frontiers_2024_v1.pdf"
    anthropic_service = AnthropicService()
    pdf_processor = PdfAnthropic(anthropic_service, pdf_path)

    responses = pdf_processor.process_pdf(custom_prompts=[SOURCE_QUERY_PROMPT])
    assert responses is not None
    assert len(responses) > 0
    return responses[0]


if __name__ == "__main__":
    response = test_source_query()
    print("Source Information:")
    print(response)
