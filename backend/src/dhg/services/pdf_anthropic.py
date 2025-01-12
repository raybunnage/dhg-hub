import os
from anthropic import Anthropic
from anthropic.types import Message
import dotenv
import base64
import httpx
from typing import Optional, List, Dict, Union, Tuple, Any
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from datetime import datetime
import asyncio
import time

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

    def create_pdf_batch(self, prompts: List[str]) -> str:
        """
        Create a batch request for processing the current PDF with multiple prompts.

        Args:
            prompts: List of prompts to process

        Returns:
            str: Batch ID for tracking
        """
        try:
            batch_requests = []

            for i, prompt in enumerate(prompts):
                # Generate unique ID for this request
                custom_id = f"pdf_{os.path.basename(self.pdf_path)}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Create request with PDF content
                request = Request(
                    custom_id=custom_id,
                    params=MessageCreateParamsNonStreaming(
                        model=self.anthropic_service.model_name,
                        max_tokens=4096,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
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
                        ],
                    ),
                )
                batch_requests.append(request)

            # Create batch using the AnthropicService client
            batch = self.anthropic_service.client.messages.batches.create(
                requests=batch_requests
            )
            return batch.id

        except Exception as e:
            raise PdfProcessingError(f"Error creating batch: {str(e)}")

    async def check_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Check the status of a batch request.

        Args:
            batch_id: The ID of the batch to check

        Returns:
            Dict containing status information
        """
        try:
            batch = await self.anthropic_service.client.messages.batches.retrieve(
                batch_id
            )
            return {
                "status": batch.processing_status,
                "processed": batch.request_counts.succeeded,
                "errors": batch.request_counts.errored,
            }
        except Exception as e:
            raise PdfProcessingError(f"Error checking batch status: {str(e)}")

    async def get_batch_results(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Get results from a completed batch.

        Args:
            batch_id: The ID of the batch to get results from

        Returns:
            List of dictionaries containing results for each prompt
        """
        results = []

        try:
            async for result in self.anthropic_service.client.messages.batches.results(
                batch_id
            ):
                if result.result.type == "succeeded":
                    results.append(
                        {
                            "prompt_id": result.custom_id,
                            "status": "success",
                            "result": result.result.message.content[0].text,
                        }
                    )
                else:
                    results.append(
                        {
                            "prompt_id": result.custom_id,
                            "status": result.result.type,
                            "error": str(
                                getattr(result.result, "error", "Unknown error")
                            ),
                        }
                    )
            return results
        except Exception as e:
            raise PdfProcessingError(f"Error getting batch results: {str(e)}")

    async def process_pdf_batch(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple prompts for the current PDF in a batch.

        Args:
            prompts: List of prompts to process

        Returns:
            List of dictionaries containing results
        """
        try:
            # Create batch
            batch_id = self.create_pdf_batch(prompts)
            print(f"Created batch with ID: {batch_id}")

            # Wait for processing to complete
            while True:
                status = await self.check_batch_status(batch_id)
                print(f"Batch status: {status}")

                if status["status"] == "ended":
                    break

                await asyncio.sleep(30)

            # Get results
            return await self.get_batch_results(batch_id)

        except Exception as e:
            raise PdfProcessingError(f"Error in batch processing: {str(e)}")

    async def test_batch_processing():
        """Test function to demonstrate batch processing with multiple PDFs."""
        try:
            # Initialize service
            anthropic_service = AnthropicService()

            # Test PDFs (adjust paths as needed)
            pdf_paths = [
                "backend/tests/test_files/pdfs/long_covid_frontiers_2024_v1.pdf",
                "backend/tests/test_files/pdfs/test_doc1.pdf",
                "backend/tests/test_files/pdfs/test_doc2.pdf",
                "backend/tests/test_files/pdfs/test_doc3.pdf",
                "backend/tests/test_files/pdfs/test_doc4.pdf",
            ]

            # Test prompts - using paper analysis prompts for meaningful results
            prompts = [
                PAPER_ANALYSIS_PROMPT,
                STRENGTH_WEAKNESS_PROMPT,
                SOURCE_QUERY_PROMPT,
            ]

            all_results = {}

            for pdf_path in pdf_paths:
                try:
                    print(f"\nProcessing {os.path.basename(pdf_path)}...")
                    print("=" * 80)

                    # Create processor for this PDF
                    pdf_processor = PdfAnthropic(anthropic_service, pdf_path)

                    # Process batch and await results
                    results = await pdf_processor.process_pdf_batch(prompts)

                    # Print results for this PDF
                    print(f"\nResults for {os.path.basename(pdf_path)}:")
                    print("-" * 40)

                    for result in results:
                        print(f"\nPrompt ID: {result['prompt_id']}")
                        print(f"Status: {result['status']}")

                        if result["status"] == "success":
                            # Truncate long responses for readability
                            response_preview = (
                                result["result"][:200] + "..."
                                if len(result["result"]) > 200
                                else result["result"]
                            )
                            print(f"Response Preview: {response_preview}")
                        else:
                            print(f"Error: {result.get('error', 'Unknown error')}")

                        print("-" * 40)

                    all_results[pdf_path] = results

                except Exception as e:
                    print(f"Error processing {pdf_path}: {str(e)}")
                    all_results[pdf_path] = None
                    continue  # Continue with next PDF even if one fails

            # Print summary
            print("\nProcessing Summary:")
            print("=" * 80)
            for pdf_path, results in all_results.items():
                status = "Success" if results is not None else "Failed"
                print(f"{os.path.basename(pdf_path)}: {status}")

            return all_results

        except Exception as e:
            print(f"Fatal error in batch processing test: {str(e)}")
            raise


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
    # Import prompts at runtime to avoid circular imports
    from dhg.services.prompts.paper_analysis_prompts import (
        PAPER_ANALYSIS_PROMPT,
        STRENGTH_WEAKNESS_PROMPT,
        SOURCE_QUERY_PROMPT,
    )

    # Run the batch processing test
    asyncio.run(test_batch_processing())
