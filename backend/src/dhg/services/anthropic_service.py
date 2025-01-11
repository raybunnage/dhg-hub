import os
from anthropic import Anthropic
import dotenv
import base64
import httpx
from typing import Optional, List, Dict, Union

dotenv.load_dotenv()

""" INSTRUCTIONS

This module provides helper functions for interacting with the Anthropic Claude API.

if __name__ == "__main__":
    get_file_and_questions(file_name, naviaux_questions)

MAIN FUNCTIONS:
1. * get_file_and_questions():
   - Gets a file and asks questions about it

2. ** call_claude_basic():
   - Simple text processing with system prompt
   - Called by many many modules
   - Usage: Call for basic Claude interactions

3. ** call_claude_messages():
   - Processes complex prompts with custom messages
   - Called by citations.py, master_categories.py, transcription_processing.py
   - Usage: Call for complex Claude interactions requiring specific message formats

4. ** call_claude_follow_up():
   - Processes follow up prompts with custom messages
   - Called by concepts_pdfs.py and concepts_txts.py
   - Usage: Call for follow up Claude interactions requiring specific message formats

5. ** call_claude_pdf_with_messages():
   - Processes complex PDF-related prompts with custom messages
   - not yet called externally
   - Usage: Call for PDF analysis requiring specific message formats

4. ** call_claude_pdf_basic():
   - Simple PDF processing with basic prompt
   - not yet called externally
   - Usage: Call for straightforward PDF analysis tasks


INTNERAL HELPER FUNCTIONS:
1. get_pdf_client_and_model():
   - internal helper to Returns configured PDF-enabled Claude client and model name
   - Called by get_file_and_questions()
   - Usage: Call when needing to process PDFs with Claude

2. get_std_client_and_model(): 
   - internal helper to Returns standard Claude client and model name
   - Called by call_claude_basic() and call_claude_messages
   - Usage: Call for non-PDF Claude interactions

3. get_completion():
   - internal helper to get completions
   - Called by call_claude_basic() and call_claude_messages

4. prompt_questions():
   - internal helper to prompt questions about a pdf file
   - Called by get_file_and_questions()

USAGE:
- Import needed client/model getters and processing functions
- Use PDF-specific functions (call_claude_pdf_*) when working with PDFs
- Use call_claude_basic() for text-only processing
- Configure system prompts and messages as needed for specific tasks

STATUS:
The module provides core Claude API interaction functionality, including both standard and PDF-enabled operations. It serves as a central point for Claude API interactions across the project.

FEEDBACK:
1. Consider separating PDF-specific functionality into a dedicated module (e.g., claude_pdf_utils.py)
2. Implement a ClaudeClient class to encapsulate client creation and basic operations
3. Add comprehensive error handling and logging
4. Improve type hints and docstrings for all functions
5. Implement a configuration management system for API keys and model names
6. Add unit tests for each function to ensure reliability

UNUSED/DUPLICATE FUNCTIONS:
This module does not contain unused or duplicate functions. All listed functions serve specific purposes and are likely called from other parts of the project.

"""


class AnthropicService:
    def __init__(self, api_key: str):
        """Initialize Anthropic clients and model name."""
        self.std_client = Anthropic(api_key=api_key)
        self.pdf_client = Anthropic(
            default_headers={"anthropic-beta": "pdfs-2024-09-25"}
        )
        self.model_name = "claude-3-5-sonnet-20241022"

    # def _get_completion(self, client, messages):
    #     """Internal helper to get completions from Claude API."""
    #     return (
    #         client.messages.create(
    #             model=self.model_name, max_tokens=4096, messages=messages
    #         )
    #         .content[0]
    #         .text
    #     )

    def call_claude_basic(
        self, max_tokens: int, input_string: str, system_string: str = None
    ) -> str:
        """Basic Claude call with system prompt and single user message."""
        messages = [
            {"role": "user", "content": [{"type": "text", "text": input_string}]}
        ]

        response = self.std_client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=messages,
            system=system_string,
        )
        return response.content[0].text

    def call_claude_messages(
        self, max_tokens: int, messages, system_string: str
    ) -> str:
        """Complex Claude call supporting multiple messages and system prompt."""
        response = self.std_client.messages.create(
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
            response = self.std_client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                system=system_string,
                temperature=temperature,
                messages=messages,
            )
            return response.content[0].text if response.content else None
        except Exception as e:
            raise Exception(f"Error in follow-up conversation: {str(e)}")

    def test_anthropic(self):
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

            response = self.std_client.messages.create(
                model=self.model_name, max_tokens=1000, messages=messages
            )
            return response.content[0].text

        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")


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

    # Run all tests
    def run_all_tests():
        print("\n=== Starting Comprehensive Test Suite ===")
        try:
            basic_responses = test_basic_calls()
            message_chain_response = test_message_chains()
            test_image_analysis()
            test_follow_up_conversations()
            print("\n=== All tests completed successfully ===")
        except Exception as e:
            print(f"\nTest suite failed with error: {str(e)}")

    # Execute all tests
    run_all_tests()
