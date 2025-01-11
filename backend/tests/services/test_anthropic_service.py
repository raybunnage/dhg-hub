import os
import base64
import unittest
from anthropic import Anthropic
from dhg.services.anthropic_service import AnthropicService


class TestAnthropicService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.service = AnthropicService(api_key)

    def get_pdf_client_and_model(self):
        """Helper method to get client and model from service."""
        return self.service.client, self.service.get_model()

    def call_claude_basic(self, max_tokens, input_string, system_string):
        """Helper method for basic Claude calls."""
        return self.service.call_claude_basic(max_tokens, input_string, system_string)

    def call_claude_pdf_basic(
        self, max_tokens, input_string, pdf_path, temperature, timeout
    ):
        """Helper method for basic PDF processing."""
        return self.service.call_claude_pdf_basic(
            max_tokens, input_string, pdf_path, temperature, timeout
        )

    def call_claude_pdf_with_messages(self, max_tokens, messages, temperature):
        """Helper method for PDF processing with messages."""
        return self.service.call_claude_pdf_with_messages(
            max_tokens, messages, temperature
        )

    def call_claude_follow_up(
        self, initial_message, follow_up_message, system_string, max_tokens, temperature
    ):
        """Helper method for follow-up conversations."""
        return self.service.call_claude_follow_up(
            initial_message, follow_up_message, system_string, max_tokens, temperature
        )

    def call_claude_with_image(self, image_source, prompt, is_url):
        """Helper method for image analysis."""
        return self.service.call_claude_with_image(image_source, prompt, is_url)

    def test_client_and_model(self) -> None:
        """Test client initialization and model configuration."""
        print("\n=== Testing Client and Model Configuration ===")
        try:
            # Test getting client and model
            client, model = self.get_pdf_client_and_model()

            # Verify client is properly initialized
            if not isinstance(client, Anthropic):
                raise ValueError("Client is not an instance of Anthropic")

            # Verify model name matches expected format
            expected_model = "claude-3-5-sonnet-20241022"
            if model != expected_model:
                raise ValueError(
                    f"Unexpected model name. Expected {expected_model}, got {model}"
                )

            # Test making a simple API call with returned client/model
            response = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Hello, are you working?"}
                        ],
                    }
                ],
            )

            if not response.content[0].text:
                raise ValueError("No response received from API call")

            print("\n✓ Client verification: Passed")
            print(f"✓ Model verification: Passed (using {model})")
            print("✓ API call test: Passed")
            print(f"Response: {response.content[0].text[:100]}...")

        except Exception as e:
            print(f"\n✗ Client/Model test failed with error: {str(e)}")
            raise

    def run_all_tests(self) -> None:
        """Run all tests for the Anthropic service."""
        print("\n=== Starting Comprehensive Test Suite ===")
        try:
            # Initialize the service first
            self.setUp()

            # Run tests
            self.test_client_and_model()
            self.test_basic_calls()
            self.test_claude_pdf_basic()
            self.test_claude_pdf_with_messages()
            self.test_follow_up_conversations()
            self.test_image_analysis()
            print("\n=== All tests completed successfully ===")
        except Exception as e:
            print(f"\nTest suite failed with error: {str(e)}")

    def test_basic_calls(self) -> None:
        """Test basic API calls."""
        print("\n=== Testing Basic API Calls ===")
        try:
            # Test 1: Simple greeting
            response = self.call_claude_basic(
                max_tokens=100,
                input_string="Hello! Please respond with a simple greeting.",
                system_string="You are a helpful assistant.",
            )
            print("\n✓ Basic greeting test passed")
            print(f"Response: {response[:100]}...")

            # Test 2: System prompt influence
            response = self.call_claude_basic(
                max_tokens=100,
                input_string="What is your role?",
                system_string="You are a snarky technical expert.",
            )
            print("\n✓ System prompt test passed")
            print(f"Response: {response[:100]}...")

            # Test 3: Longer response
            response = self.call_claude_basic(
                max_tokens=500,
                input_string="Explain what a REST API is in a few sentences.",
                system_string="You are a technical instructor.",
            )
            print("\n✓ Longer response test passed")
            print(f"Response: {response[:100]}...")

            print("\n=== Basic API Tests Completed Successfully ===")

        except Exception as e:
            print(f"\n✗ Basic API test failed with error: {str(e)}")
            raise

    def test_claude_pdf_basic(self) -> None:
        """Test the basic PDF processing functionality."""
        print("\n=== Testing Basic PDF Processing ===")

        # Define the correct path to test PDF
        test_pdf_path = "backend/tests/test_files/pdfs/test_document.pdf"

        try:
            # First verify the PDF exists
            if not os.path.exists(test_pdf_path):
                print(f"\n✗ Test PDF not found at: {test_pdf_path}")
                print(
                    "Please run 'python backend/tests/create_test_pdf.py' to generate the test file"
                )
                return

            print(f"\n✓ Found test PDF at: {test_pdf_path}")
            print(f"PDF size: {os.path.getsize(test_pdf_path)} bytes")

            # Test 1: Basic PDF analysis
            basic_query = "Please analyze this PDF and list the key points mentioned."
            response = self.call_claude_pdf_basic(
                max_tokens=1000,
                input_string=basic_query,
                pdf_path=test_pdf_path,
                temperature=0.0,
                timeout=30.0,
            )
            print("\n✓ Basic PDF analysis test passed")
            print(f"Response preview: {response[:200]}...")

            # Test 2: Specific content query
            specific_query = "What are the four key points listed in the document?"
            response = self.call_claude_pdf_basic(
                max_tokens=1000,
                input_string=specific_query,
                pdf_path=test_pdf_path,
                temperature=0.0,
                timeout=30.0,
            )
            print("\n✓ Specific content query test passed")
            print(f"Response preview: {response[:200]}...")

            # Test 3: Query about case studies
            case_study_query = (
                "What were the performance improvements mentioned in the case studies?"
            )
            response = self.call_claude_pdf_basic(
                max_tokens=1000,
                input_string=case_study_query,
                pdf_path=test_pdf_path,
                temperature=0.0,
                timeout=30.0,
            )
            print("\n✓ Case studies query test passed")
            print(f"Response preview: {response[:200]}...")

            print("\n=== PDF Basic Tests Completed Successfully ===")

        except FileNotFoundError as e:
            print(f"\n✗ Error accessing PDF file: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Please ensure the PDF exists at: {os.path.abspath(test_pdf_path)}")
            raise
        except Exception as e:
            print(f"\n✗ PDF basic test suite failed with error: {str(e)}")
            raise

    def test_claude_pdf_with_messages(self) -> None:
        """Test PDF processing with follow-up questions."""
        print("\n=== Testing PDF Processing with Follow-up Questions ===")

        test_pdf_path = "backend/tests/test_files/pdfs/test_document.pdf"

        try:
            # First verify the PDF exists
            if not os.path.exists(test_pdf_path):
                print(f"\n✗ Test PDF not found at: {test_pdf_path}")
                print(
                    "Please run 'python backend/tests/create_test_pdf.py' to generate the test file"
                )
                return

            print(f"\n✓ Found test PDF at: {test_pdf_path}")

            # Read the PDF content once
            with open(test_pdf_path, "rb") as f:
                pdf_content = f.read()
                pdf_base64 = base64.b64encode(pdf_content).decode()

            # Initial question about the document
            initial_messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What are the three types of machine learning algorithms discussed in the introduction?",
                        },
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64,
                            },
                        },
                    ],
                }
            ]

            print("\nAsking initial question about ML algorithms...")
            response1 = self.call_claude_pdf_with_messages(
                max_tokens=1000, messages=initial_messages, temperature=0
            )
            print(f"Initial Response: {response1[:200]}...")

            # Follow-up about supervised learning
            follow_up_messages = initial_messages + [
                {"role": "assistant", "content": [{"type": "text", "text": response1}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What are the specific examples of supervised learning algorithms mentioned?",
                        }
                    ],
                },
            ]

            print("\nAsking follow-up about supervised learning...")
            response2 = self.call_claude_pdf_with_messages(
                max_tokens=1000, messages=follow_up_messages, temperature=0
            )
            print(f"Follow-up Response: {response2[:200]}...")

            # Follow-up about case studies
            case_study_messages = follow_up_messages + [
                {"role": "assistant", "content": [{"type": "text", "text": response2}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What were the specific performance improvements mentioned in the case studies section?",
                        }
                    ],
                },
            ]

            print("\nAsking about case study results...")
            response3 = self.call_claude_pdf_with_messages(
                max_tokens=1000, messages=case_study_messages, temperature=0
            )
            print(f"Case Studies Response: {response3[:200]}...")

            # Final follow-up about conclusions
            conclusion_messages = case_study_messages + [
                {"role": "assistant", "content": [{"type": "text", "text": response3}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Based on all the information discussed, what were the main conclusions of the report?",
                        }
                    ],
                },
            ]

            print("\nAsking about conclusions...")
            response4 = self.call_claude_pdf_with_messages(
                max_tokens=1000, messages=conclusion_messages, temperature=0
            )
            print(f"Conclusions Response: {response4[:200]}...")

            # Verify responses
            if not all([response1, response2, response3, response4]):
                raise ValueError("One or more responses were empty")

            print("\n✓ All follow-up questions successfully processed")
            print("\nTest Summary:")
            print(f"- Initial question about ML algorithms")
            print(f"- Follow-up about supervised learning")
            print(f"- Questions about case studies")
            print(f"- Final questions about conclusions")

        except FileNotFoundError as e:
            print(f"\n✗ Error accessing PDF file: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            raise
        except Exception as e:
            print(f"\n✗ PDF follow-up test failed with error: {str(e)}")
            raise

    def test_follow_up_conversations(self) -> None:
        """Test follow-up conversation capabilities."""
        print("\n=== Testing Follow-up Conversations ===")

        try:
            # Test 1: Simple follow-up
            initial_msg = "What is machine learning?"
            follow_up_msg = "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."

            response = self.call_claude_follow_up(
                initial_message=initial_msg,
                follow_up_message=follow_up_msg,
                system_string="You are a helpful AI teacher.",
                max_tokens=1000,
                temperature=0,
            )
            print("\n✓ Simple follow-up test passed")
            print(f"Response: {response[:200]}...")

            # Test 2: Technical follow-up
            initial_msg = "What is a neural network?"
            follow_up_msg = "A neural network is a computational model inspired by the human brain, consisting of interconnected nodes (neurons) organized in layers."

            response = self.call_claude_follow_up(
                initial_message=initial_msg,
                follow_up_message=follow_up_msg,
                system_string="You are a technical expert.",
                max_tokens=1000,
                temperature=0,
            )
            print("\n✓ Technical follow-up test passed")
            print(f"Response: {response[:200]}...")

            # Test 3: Multi-turn conversation
            initial_msg = "What are the benefits of cloud computing?"
            follow_up_msg = "Cloud computing offers scalability, cost-effectiveness, and accessibility. It allows businesses to scale resources up or down based on demand."

            response = self.call_claude_follow_up(
                initial_message=initial_msg,
                follow_up_message=follow_up_msg,
                system_string="You are a cloud computing specialist.",
                max_tokens=1000,
                temperature=0,
            )
            print("\n✓ Multi-turn conversation test passed")
            print(f"Response: {response[:200]}...")

            print("\n=== Follow-up Conversation Tests Completed Successfully ===")

        except Exception as e:
            print(f"\n✗ Follow-up conversation test failed with error: {str(e)}")
            raise

    def test_image_analysis(self) -> None:
        """Test image analysis capabilities."""
        print("\n=== Testing Image Analysis ===")

        # Define test image paths with correct directory
        test_image_path = "backend/tests/test_images/test1.jpg"
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Hubble_Ultra_Deep_Field_part_d.jpg/1024px-Hubble_Ultra_Deep_Field_part_d.jpg"

        try:
            # Test 1: Local image analysis
            if os.path.exists(test_image_path):
                print("\nTesting local image analysis...")
                response = self.call_claude_with_image(
                    image_source=test_image_path,
                    prompt="What do you see in this image? Please describe it in detail.",
                    is_url=False,
                )
                print("✓ Local image analysis test passed")
                print(f"Response: {response[:200]}...")
            else:
                print(f"\n⚠ Warning: Local test image not found at {test_image_path}")
                print("Skipping local image test")

            # Test 2: URL image analysis
            print("\nTesting URL image analysis...")
            response = self.call_claude_with_image(
                image_source=test_image_url,
                prompt="Describe this astronomical image. What notable features do you see?",
                is_url=True,
            )
            print("✓ URL image analysis test passed")
            print(f"Response: {response[:200]}...")

            # Test 3: Technical analysis
            if os.path.exists(test_image_path):
                print("\nTesting technical image analysis...")
                response = self.call_claude_with_image(
                    image_source=test_image_path,
                    prompt="Analyze the technical aspects of this image (lighting, composition, color balance).",
                    is_url=False,
                )
                print("✓ Technical analysis test passed")
                print(f"Response: {response[:200]}...")

            print("\n=== Image Analysis Tests Completed Successfully ===")

        except Exception as e:
            print(f"\n✗ Image analysis test failed with error: {str(e)}")
            raise


if __name__ == "__main__":
    # Use the unittest runner instead of direct instantiation
    unittest.main()
