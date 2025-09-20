"""
LLM client for interacting with Large Language Models.
"""

import aiohttp
import json
from typing import Dict, List, Any, Optional
import asyncio

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class LLMClient:
    """
    Client for interacting with Large Language Models.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = settings.LLM_MODEL or "gpt-4"
        self.max_tokens = settings.LLM_MAX_TOKENS or 2000
        self.temperature = settings.LLM_TEMPERATURE or 0.7

    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from the LLM.
        """
        try:
            model = model or self.model
            temperature = temperature or self.temperature
            max_tokens = max_tokens or self.max_tokens

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_data = await response.json()
                        raise Exception(f"LLM API error: {error_data}")

        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            raise

    async def generate_suggestions(
        self,
        context: str,
        language: str,
        suggestion_type: str = "completion"
    ) -> List[Dict[str, Any]]:
        """
        Generate code suggestions.
        """
        try:
            if suggestion_type == "completion":
                return await self._generate_completion_suggestions(context, language)
            elif suggestion_type == "refactor":
                return await self._generate_refactor_suggestions(context, language)
            else:
                return await self._generate_general_suggestions(context, language)

        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []

    async def _generate_completion_suggestions(
        self,
        context: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Generate code completion suggestions.
        """
        prompt = f"""
        Complete the following {language} code:

        ```{language}
        {context}
        ```

        Provide 3 different completion suggestions. Each suggestion should be:
        1. Syntactically correct
        2. Follow {language} best practices
        3. Complete the logical flow of the code

        Format each suggestion as a separate code block.
        """

        response = await self.generate_response(prompt)

        # Parse suggestions from response
        suggestions = []
        parts = response.split('\n\n')

        for i, part in enumerate(parts, 1):
            if part.strip():
                suggestions.append({
                    'type': 'completion',
                    'title': f'Completion Suggestion {i}',
                    'code': part.strip(),
                    'language': language,
                    'confidence': 0.8
                })

        return suggestions[:3]

    async def _generate_refactor_suggestions(
        self,
        context: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Generate refactoring suggestions.
        """
        prompt = f"""
        Suggest improvements for this {language} code:

        ```{language}
        {context}
        ```

        Provide 3 refactoring suggestions that:
        1. Improve code readability
        2. Follow {language} best practices
        3. Make the code more maintainable

        For each suggestion, include the refactored code.
        """

        response = await self.generate_response(prompt)

        suggestions = []
        parts = response.split('\n\n')

        for i, part in enumerate(parts, 1):
            if part.strip():
                suggestions.append({
                    'type': 'refactoring',
                    'title': f'Refactoring Suggestion {i}',
                    'description': part.strip(),
                    'language': language,
                    'confidence': 0.8
                })

        return suggestions[:3]

    async def _generate_general_suggestions(
        self,
        context: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Generate general code suggestions.
        """
        prompt = f"""
        Provide suggestions to improve this {language} code:

        ```{language}
        {context}
        ```

        Focus on:
        1. Code quality improvements
        2. Best practices
        3. Performance optimizations
        4. Error handling
        """

        response = await self.generate_response(prompt)

        return [{
            'type': 'general_improvement',
            'title': 'Code Improvement Suggestions',
            'description': response,
            'language': language,
            'confidence': 0.7
        }]

    async def check_health(self) -> bool:
        """
        Check if the LLM service is healthy.
        """
        try:
            test_prompt = "Say 'OK' if you can understand this message."
            response = await self.generate_response(test_prompt, max_tokens=10)
            return "OK" in response.upper()
        except Exception:
            return False
