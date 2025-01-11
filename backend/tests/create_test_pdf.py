import os
import logging
from fpdf import FPDF

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_test_pdf(
    output_path: str = "backend/tests/test_files/pdfs/test_document.pdf",
) -> None:
    """Create a sophisticated PDF file for testing complex queries and follow-ups."""
    try:
        logger.debug(f"Starting PDF creation process...")
        logger.debug(f"Target output path: {output_path}")

        # Check if directory exists, create if it doesn't
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.debug(f"Directory verified/created: {os.path.dirname(output_path)}")

        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(200, 10, txt="Advanced Machine Learning Techniques", ln=1, align="C")

        # Author and Date
        pdf.set_font("Arial", "I", size=12)
        pdf.cell(200, 10, txt="By Dr. Sarah Johnson", ln=1, align="C")
        pdf.cell(200, 10, txt="Technical Report - March 2024", ln=1, align="C")

        # Introduction
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="1. Introduction", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="This report examines three fundamental machine learning algorithms and their applications in real-world scenarios. We'll explore supervised learning, unsupervised learning, and reinforcement learning, with specific focus on their implementation challenges and performance metrics.",
            align="L",
        )

        # Algorithms Section
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="2. Core Algorithms", ln=1, align="L")

        # Supervised Learning
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(200, 10, txt="2.1 Supervised Learning", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="Supervised learning algorithms require labeled training data. Key examples include:\n- Random Forests: Ensemble method using multiple decision trees\n- Support Vector Machines: Effective for high-dimensional spaces\n- Neural Networks: Deep learning approach for complex patterns",
            align="L",
        )

        # Unsupervised Learning
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(200, 10, txt="2.2 Unsupervised Learning", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="Unsupervised learning works with unlabeled data. Primary techniques include:\n- K-means Clustering: Groups similar data points\n- Principal Component Analysis: Reduces dimensionality\n- Autoencoders: Self-supervised neural networks",
            align="L",
        )

        # Performance Metrics
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="3. Performance Metrics", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="Key performance indicators for machine learning models:\n\n1. Accuracy: Overall correctness of predictions\n2. Precision: Positive predictive value\n3. Recall: True positive rate\n4. F1 Score: Harmonic mean of precision and recall",
            align="L",
        )

        # Case Studies
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="4. Case Studies", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="4.1 Healthcare Application\nImplemented random forests for disease prediction with 89% accuracy.\n\n4.2 Financial Services\nUsed neural networks for fraud detection, improving detection rates by 34%.\n\n4.3 Manufacturing\nApplied unsupervised learning for quality control, reducing defects by 45%.",
            align="L",
        )

        # Conclusions
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="5. Conclusions", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="Our analysis demonstrates that:\n1. Algorithm selection heavily depends on data characteristics\n2. Hybrid approaches often yield better results\n3. Regular model retraining is crucial\n4. Performance metrics should align with business objectives",
            align="L",
        )

        # References
        pdf.add_page()
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="References", ln=1, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(
            0,
            10,
            txt="1. Smith, J. (2023). 'Advanced Machine Learning Algorithms'\n2. Brown, R. (2023). 'Performance Metrics in ML'\n3. Johnson, S. (2024). 'Case Studies in Applied ML'\n4. Davis, M. (2023). 'Healthcare Applications of ML'",
            align="L",
        )

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
