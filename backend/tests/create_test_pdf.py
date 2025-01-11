import os
import logging
from fpdf import FPDF

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_test_pdf(
    output_path: str = "backend/tests/test_files/pdfs/test_document.pdf",
) -> None:
    """Create a simple PDF file for testing."""
    try:
        logger.debug(f"Starting PDF creation process...")
        logger.debug(f"Target output path: {output_path}")

        # Check if directory exists, create if it doesn't
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.debug(f"Directory verified/created: {os.path.dirname(output_path)}")

        # Initialize PDF
        logger.debug("Initializing FPDF...")
        pdf = FPDF()

        # Add page
        logger.debug("Adding page...")
        pdf.add_page()

        # Set font
        logger.debug("Setting font...")
        pdf.set_font("Arial", size=12)

        # Add content with logging
        logger.debug("Adding content...")
        pdf.cell(200, 10, txt="Test Document for Claude API", ln=1, align="C")
        logger.debug("Added title...")

        pdf.cell(200, 10, txt="", ln=1, align="L")

        pdf.multi_cell(
            0,
            10,
            txt="This is a test document created for testing Claude's PDF processing capabilities. It contains various types of content to test different aspects of the API.",
            align="L",
        )
        logger.debug("Added main text...")

        pdf.cell(200, 10, txt="", ln=1, align="L")

        pdf.multi_cell(
            0,
            10,
            txt="Key Points:\n1. PDF Processing\n2. Text Extraction\n3. Content Analysis\n4. Document Understanding",
            align="L",
        )
        logger.debug("Added key points...")

        # Save the PDF
        logger.debug(f"Attempting to save PDF to: {output_path}")
        pdf.output(output_path)

        # Verify file was created
        if os.path.exists(output_path):
            logger.debug(f"PDF successfully created at {output_path}")
            logger.debug(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            logger.error(f"PDF file not found after creation attempt!")

    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        logger.info("Starting test PDF creation...")
        create_test_pdf()
        logger.info("PDF creation completed successfully!")
    except Exception as e:
        logger.error(f"Failed to create test PDF: {str(e)}")
