import os
from anthropic import Anthropic
from anthropic.types import Message
import dotenv
import base64
import httpx
from typing import Optional, List, Dict, Union, Tuple, Any

dotenv.load_dotenv()


class AnthropicService:
    def __init__(self):
        """Initialize the Anthropic service with API key from environment."""
        dotenv.load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = Anthropic(api_key=api_key)
        self.model_name = "claude-3-5-sonnet-20241022"

    @property
    def model(self) -> str:
        """Property to maintain backward compatibility with tests.

        Returns:
            str: Current model name
        """
        return self.model_name

    def call_claude_basic(
        self, max_tokens: int, input_string: str, system_string: Optional[str] = None
    ) -> str:
        """Basic Claude call with system prompt and single user message.

        Args:
            max_tokens (int): Maximum tokens in response
            input_string (str): User's input message
            system_string (Optional[str]): System prompt to guide Claude's behavior

        Returns:
            str: Claude's response text
        """
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
        """Complex Claude call supporting multiple messages and system prompt.

        Args:
            max_tokens (int): Maximum tokens in response
            messages (List[Dict]): List of message dictionaries in Claude's format
            system_string (str): System prompt to guide Claude's behavior

        Returns:
            str: Claude's response text
        """
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
        """Call Claude with an image and get a response.

        Args:
            image_source (str): Path to local image file or URL
            prompt (str): Text prompt to accompany the image
            is_url (bool): Whether image_source is a URL (True) or local path (False)

        Returns:
            str: Claude's response text

        Raises:
            Exception: If image processing fails
        """
        try:
            # Convert both URLs and local files to base64
            if is_url:
                base64_data = self._encode_image_url(image_source)
            else:
                base64_data = self._encode_image_file(image_source)

            # Create message with base64-encoded image
            media = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_data,
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
        messages: List[Message],
    ) -> str:
        """Get completion from Claude API.

        Args:
            client (Anthropic): Anthropic client instance
            messages (List[Message]): List of properly formatted message objects

        Returns:
            str: Claude's response text
        """
        return (
            client.messages.create(
                model=self.model_name,
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

    def get_model(self):
        """Get the current model being used."""
        return "claude-3-5-sonnet-20241022"  # Or whatever model version you're using
