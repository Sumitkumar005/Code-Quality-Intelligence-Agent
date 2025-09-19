"""
LLM service for interacting with Large Language Models.
"""

import aiohttp
import json
from typing import Dict, List, Any, Optional
import asyncio

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class LLMService:
    """
    Service for interacting with Large Language Models.
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

    async def analyze_code(
        self,
        code: str,
        language: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze code using LLM.
        """
        prompt = self._create_code_analysis_prompt(code, language, analysis_type)
        response = await self.generate_response(prompt)

        try:
            # Try to parse as JSON if the response is structured
            return json.loads(response)
        except json.JSONDecodeError:
            # Return as plain text if not JSON
            return {"analysis": response, "language": language, "type": analysis_type}

    async def generate_explanation(
        self,
        code: str,
        language: str,
        detail_level: str = "intermediate"
    ) -> str:
        """
        Generate a natural language explanation of code.
        """
        prompt = f"""
        Explain the following {language} code in {detail_level} detail:

        ```{language}
        {code}
        ```

        Provide a clear explanation that covers:
        1. What the code does
        2. How it works
        3. Key concepts involved
        4. Any important considerations
        """

        return await self.generate_response(prompt)

    async def suggest_improvements(
        self,
        code: str,
        language: str,
        issues: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest code improvements.
        """
        issues_text = "\n".join(issues) if issues else "General code quality"

        prompt = f"""
        Suggest specific improvements for this {language} code:

        ```{language}
        {code}
        ```

        Known issues: {issues_text}

        Provide 3-5 concrete improvement suggestions, each with:
        - Description of the change
        - Why it's beneficial
        - Code example (if applicable)
        """

        response = await self.generate_response(prompt)

        # Parse suggestions (simplified parsing)
        suggestions = []
        lines = response.split('\n')
        current_suggestion = {}

        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {"title": line[2:].strip()}
            elif current_suggestion and line:
                current_suggestion["description"] = current_suggestion.get("description", "") + line + " "

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions

    def _create_code_analysis_prompt(self, code: str, language: str, analysis_type: str) -> str:
        """
        Create a structured prompt for code analysis.
        """
        base_prompt = f"""
        Analyze this {language} code and provide a JSON response:

        ```{language}
        {code}
        ```

        Return a JSON object with these fields:
        - summary: Brief summary of the code
        - complexity: Code complexity assessment (low/medium/high)
        - issues: Array of potential issues found
        - strengths: Array of code strengths
        - recommendations: Array of improvement suggestions
        """

        if analysis_type == "security":
            base_prompt += """
        Focus particularly on security aspects:
        - Input validation
        - Authentication/authorization
        - Data exposure
        - Injection vulnerabilities
        - Secure coding practices
            """
        elif analysis_type == "performance":
            base_prompt += """
        Focus on performance aspects:
        - Algorithm efficiency
        - Memory usage
        - I/O operations
        - Bottlenecks
        - Optimization opportunities
            """

        base_prompt += "\nEnsure the response is valid JSON."

        return base_prompt

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
