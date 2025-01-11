import os
from anthropic import Anthropic
import dotenv
import base64
import httpx
from typing import Optional, List, Dict, Union, Tuple, Any

dotenv.load_dotenv()


class AnthropicService:
    def __init__(self, api_key: str) -> None:
        """Initialize Anthropic client and model name."""
        self.client = Anthropic(api_key=api_key)
        self.model_name = "claude-3-5-sonnet-20241022"

    def call_claude_basic(
        self, max_tokens: int, input_string: str, system_string: Optional[str] = None
    ) -> str:
        """Basic Claude call with system prompt and single user message."""
        messages = [
            {"role": "user", "content": [{"type": "text", "text": input_string}]}
        ]

        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=messages,
            system=system_string,
        )
        return response.content[0].text

    def call_claude_messages(
        self,
        max_tokens: int,
        messages: List[Dict[str, Union[str, List[Dict[str, str]]]]],
        system_string: str,
    ) -> str:
        """Complex Claude call supporting multiple messages and system prompt."""
        response = self.client.messages.create(
            model=self.model_name,
            system=system_string,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.content[0].text

    def call_claude_follow_up(
        self,
        initial_message: str,
        follow_up_message: str,
        system_string: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0,
    ) -> str:
        """
        Process a follow-up conversation with Claude.

        Args:
            initial_message: The user's initial message
            follow_up_message: Claude's previous response to follow up on
            system_string: Optional system prompt to guide Claude's behavior
            max_tokens: Maximum tokens in response (default: 2048)
            temperature: Randomness in response (0 = deterministic, 1 = creative)

        Returns:
            str: Claude's response text

        Example:
            initial = "What's the capital of France?"
            follow_up = "It's Paris, the City of Light."
            response = call_claude_follow_up(initial, follow_up, "Tell me more about...")
        """
        messages = [
            {"role": "user", "content": [{"type": "text", "text": initial_message}]},
            {
                "role": "assistant",
                "content": [{"type": "text", "text": follow_up_message}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Tell me more about what you just said."}
                ],
            },
        ]

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                system=system_string,
                temperature=temperature,
                messages=messages,
            )
            return response.content[0].text if response.content else None
        except Exception as e:
            raise Exception(f"Error in follow-up conversation: {str(e)}")

    def test_anthropic(self) -> Tuple[str, str, str]:
        # Test basic call
        response_basic = self.call_claude_basic(
            max_tokens=1000,
            input_string="Hello!",
            system_string="You are a helpful assistant",
        )
        print("Basic Call Response:", response_basic)

        # Test complex call with multiple messages
        messages = [
            {"role": "user", "content": "Tell me a joke."},
            {"role": "assistant", "content": "Why did the chicken cross the road?"},
            {"role": "user", "content": "I don't know, why?"},
        ]
        response_complex = self.call_claude_messages(
            max_tokens=1000,
            messages=messages,
            system_string="You are a helpful assistant",
        )
        print("Complex Call Response:", response_complex)

        # Test follow-up call
        response_follow_up = self.call_claude_follow_up(
            max_tokens=1000,
            input_string="Tell me a joke.",
            follow_up_message="Why did the chicken cross the road?",
            system_string="You are a snarky know it all assistant",
        )
        print("Follow-up Call Response:", response_follow_up)

        return response_basic, response_complex, response_follow_up

    def _encode_image_file(self, image_path: str) -> str:
        """Convert image file to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _encode_image_url(self, image_url: str) -> str:
        """Convert image from URL to base64 string."""
        return base64.b64encode(httpx.get(image_url).content).decode("utf-8")

    def call_claude_with_image(
        self, image_source: str, prompt: str, is_url: bool = False
    ) -> str:
        """Call Claude with an image and get a response."""
        try:
            if is_url:
                media = [
                    {"type": "image", "source": {"type": "url", "url": image_source}}
                ]
            else:
                with open(image_source, "rb") as img:
                    media = [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64.b64encode(img.read()).decode(),
                            },
                        }
                    ]

            messages = [
                {"role": "user", "content": [{"type": "text", "text": prompt}, *media]}
            ]

            response = self.client.messages.create(
                model=self.model_name, max_tokens=1000, messages=messages
            )
            return response.content[0].text

        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    # internal helper to get the client and model
    def get_pdf_client_and_model(self) -> Tuple[Anthropic, str]:
        """Return the client and model name."""
        return self.client, self.model_name

    # internal helper to get the client and model
    def get_std_client_and_model(self) -> Tuple[Anthropic, str]:
        """Return the client and model name."""
        return self.client, self.model_name

    # internal helper from anthropic example
    def get_completion(
        self,
        client: Anthropic,
        messages: List[Dict[str, Union[str, List[Dict[str, str]]]]],
    ) -> str:
        """Get completion from Claude API.

        Args:
            client: Anthropic client instance
            messages: List of message dictionaries
        Returns:
            str: Claude's response text
        """
        return (
            client.messages.create(
                model=self.model_name,  # Changed from MODEL_NAME to self.model_name
                max_tokens=4096,
                messages=messages,
            )
            .content[0]
            .text
        )

    # ** external high level function or a complex helper call with messages from anthropic example - no system prompt
    def call_claude_pdf_with_messages(
        self,
        max_tokens: int,
        messages: List[Dict[str, Union[str, List[Dict[str, str]]]]],
        temperature: float = 0.0,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Makes a call to Claude's PDF-enabled API with custom message formatting.

        This function allows for more complex interactions with Claude's PDF capabilities
        by accepting pre-formatted messages. This enables multi-turn conversations and
        custom message structures needed for PDF processing.

        Args:
            max_tokens (int): Maximum number of tokens allowed in the response
            messages (List[Dict]): List of message dictionaries in Claude's format.
                Each message should have 'role' and 'content' keys. For PDFs,
                content should include document source information.
            temperature (float, optional): Controls randomness in responses. Defaults to 0.0.
            timeout (float, optional): Timeout for API call in seconds. Defaults to None.

        Returns:
            str: Claude's response text

        Raises:
            ValueError: If messages are not properly formatted
            Exception: If API call fails
        """
        try:
            # Validate message format
            for msg in messages:
                if (
                    not isinstance(msg, dict)
                    or "role" not in msg
                    or "content" not in msg
                ):
                    raise ValueError("Invalid message format")

            client, model_name = self.get_pdf_client_and_model()
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                messages=messages,
                temperature=temperature,
                timeout=timeout,
            )
            return response.content[0].text

        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

    # external helper for a simple call makes user messages - no system prompt
    def call_claude_pdf_basic(
        self,
        max_tokens: int,
        input_string: str,
        pdf_path: str,
        temperature: float = 0.0,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Makes a basic call to Claude's API with a single user message and PDF.

        Args:
            max_tokens (int): Maximum number of tokens allowed in the response
            input_string (str): The user message/prompt to send to Claude
            pdf_path (str): Path to the PDF file to analyze
            temperature (float, optional): Controls randomness in responses. Defaults to 0.0.
            timeout (float, optional): Timeout for API call in seconds. Defaults to None.

        Returns:
            str: Claude's response text
        """
        if not input_string.strip():
            raise ValueError("Input string cannot be empty")

        try:
            # Read the PDF file
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()

            # Create message with both text and PDF using correct type
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": input_string},
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base64.b64encode(pdf_content).decode(),
                            },
                        },
                    ],
                }
            ]

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                messages=messages,
                temperature=temperature,
                timeout=timeout,
            )
            return response.content[0].text

        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")


if __name__ == "__main__":
    # Initialize the service
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    anthropic = AnthropicService(api_key)

    def test_basic_calls():
        print("\n=== Testing Basic Calls ===")
        try:
            # Test with different max_tokens and system strings
            responses = []

            # Simple greeting test
            response1 = anthropic.call_claude_basic(
                max_tokens=100,
                input_string="Hi! How are you?",
                system_string="You are a friendly assistant.",
            )
            responses.append(response1)
            print("\nBasic greeting test:", response1)

            # Technical explanation test
            response2 = anthropic.call_claude_basic(
                max_tokens=500,
                input_string="What is Python?",
                system_string="You are a technical instructor. Keep responses under 100 words.",
            )
            responses.append(response2)
            print("\nTechnical explanation test:", response2)

            return responses
        except Exception as e:
            print(f"\nTest failed with error: {str(e)}")
            raise

    def test_message_chains():
        print("\n=== Testing Message Chains ===")
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": "What is machine learning?"}],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Machine learning is a branch of AI that enables systems to learn from data.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": "Can you give an example?"}],
            },
        ]

        response = anthropic.call_claude_messages(
            max_tokens=1000,
            messages=messages,
            system_string="You are an AI expert giving simple explanations.",
        )
        print("\nMessage Chain Response:", response)
        return response

    def test_image_analysis():
        print("\n=== Testing Image Analysis ===")
        # Test with a local image
        try:
            local_response = anthropic.call_claude_with_image(
                image_source="backend/tests/test_images/test1.jpg",
                prompt="What do you see in this image?",
                is_url=False,
            )
            print("\nLocal Image Analysis:", local_response)
        except Exception as e:
            print("\nLocal image test failed:", str(e))

        # Test with an image URL
        try:
            url_response = anthropic.call_claude_with_image(
                image_source="https://upload.wikimedia.org/wikipedia/commons/e/eb/Ash_Tree_-_geograph.org.uk_-_590710.jpg",
                prompt="Describe this image in detail.",
                is_url=True,
            )
            print("\nURL Image Analysis:", url_response)
        except Exception as e:
            print("\nURL image test failed:", str(e))

    def test_follow_up_conversations():
        print("\n=== Testing Follow-up Conversations ===")
        # Test different types of conversations
        conversations = [
            {
                "initial": "What is quantum computing?",
                "first_response": "Quantum computing uses quantum mechanics principles like superposition and entanglement to perform computations.",
                "system": "You are a quantum physics professor.",
            },
            {
                "initial": "How do you make chocolate chip cookies?",
                "first_response": "The basic ingredients are flour, butter, sugar, eggs, and chocolate chips.",
                "system": "You are a professional baker.",
            },
        ]

        for i, conv in enumerate(conversations, 1):
            print(f"\nConversation Test {i}:")
            response = anthropic.call_claude_follow_up(
                initial_message=conv["initial"],
                follow_up_message=conv["first_response"],
                system_string=conv["system"],
            )
            print(f"Initial: {conv['initial']}")
            print(f"First Response: {conv['first_response']}")
            print(f"Follow-up Response: {response}")

    def test_claude_pdf_basic() -> None:
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
            response = anthropic.call_claude_pdf_basic(
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
            response = anthropic.call_claude_pdf_basic(
                max_tokens=1000,
                input_string=specific_query,
                pdf_path=test_pdf_path,
                temperature=0.0,
                timeout=30.0,
            )
            print("\n✓ Specific content query test passed")
            print(f"Response preview: {response[:200]}...")

        except FileNotFoundError as e:
            print(f"\n✗ Error accessing PDF file: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Please ensure the PDF exists at: {os.path.abspath(test_pdf_path)}")
            raise
        except Exception as e:
            print(f"\n✗ PDF basic test suite failed with error: {str(e)}")
            raise

    # Run all tests
    def run_all_tests():
        print("\n=== Starting Comprehensive Test Suite ===")
        try:
            # basic_responses = test_basic_calls()
            # message_chain_response = test_message_chains()
            # test_image_analysis()
            # test_follow_up_conversations()
            # print("\n=== All tests completed successfully ===")
            test_claude_pdf_basic()
        except Exception as e:
            print(f"\nTest suite failed with error: {str(e)}")

    # Execute all tests
    run_all_tests()
