"""
OpenAI API client wrapper with retry/backoff functionality.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    A wrapper for the OpenAI API client with retry and error handling.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client with the provided API key or from environment.
        
        Args:
            api_key: Optional API key. If not provided, will use OPENAI_API_KEY from environment.
        """
        # Try both OPENAI_API_KEY and OPEN_API_KEY
        api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)
        if not api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPEN_API_KEY or OPENAI_API_KEY environment variable or pass api_key parameter."
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.APIConnectionError,
                openai.InternalServerError,
            )
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = 90.0,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the OpenAI API with retry logic.
        
        Args:
            model: The model to use (e.g., "gpt-4o-mini")
            messages: List of message dictionaries with role and content
            temperature: Sampling temperature (default: 0.2)
            max_tokens: Maximum tokens to generate (default: None)
            timeout: Request timeout in seconds (default: 90.0)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict containing the response and metadata
        """
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                **kwargs,
            )
            
            elapsed_time = time.time() - start_time
            
            # Extract the content from the response
            content = response.choices[0].message.content
            
            # Calculate token usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            return {
                "content": content,
                "usage": usage,
                "elapsed_time": elapsed_time,
                "model": model,
                "finish_reason": response.choices[0].finish_reason,
            }
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise


def sanitize_prompt(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sanitize prompt messages to remove any sensitive information before logging.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Sanitized list of message dictionaries
    """
    sanitized = []
    for msg in messages:
        # Create a copy to avoid modifying the original
        sanitized_msg = msg.copy()
        
        # For system and user messages, keep as is
        # For assistant messages, truncate if too long
        if msg["role"] == "assistant" and len(msg["content"]) > 100:
            sanitized_msg["content"] = msg["content"][:100] + "... [truncated]"
            
        sanitized.append(sanitized_msg)
    
    return sanitized
