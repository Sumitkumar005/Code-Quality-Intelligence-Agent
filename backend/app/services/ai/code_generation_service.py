"""
Code generation service using AI models.
"""

from typing import Dict, List, Any, Optional
import re

from app.core.logging import get_logger
from app.core.config import settings
from .llm_service import LLMService

logger = get_logger(__name__)


class CodeGenerationService:
    """
    Service for AI-powered code generation and suggestions.
    """

    def __init__(self):
        self.llm_service = LLMService()

    async def generate_suggestions(
        self,
        context: str,
        language: str,
        suggestion_type: str = "completion"
    ) -> List[Dict[str, Any]]:
        """
        Generate code suggestions based on context.
        """
        try:
            if suggestion_type == "completion":
                return await self._generate_completion_suggestions(context, language)
            elif suggestion_type == "refactor":
                return await self._generate_refactor_suggestions(context, language)
            elif suggestion_type == "test":
                return await self._generate_test_suggestions(context, language)
            else:
                return await self._generate_general_suggestions(context, language)

        except Exception as e:
            logger.error(f"Code suggestion generation failed: {e}")
            return []

    async def generate_function(
        self,
        description: str,
        language: str,
        parameters: List[Dict[str, str]] = None,
        return_type: str = None
    ) -> Dict[str, Any]:
        """
        Generate a complete function based on description.
        """
        try:
            prompt = self._create_function_prompt(description, language, parameters, return_type)
            generated_code = await self.llm_service.generate_response(prompt)

            # Clean up the generated code
            cleaned_code = self._clean_generated_code(generated_code, language)

            return {
                'success': True,
                'code': cleaned_code,
                'language': language,
                'description': description
            }

        except Exception as e:
            logger.error(f"Function generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'language': language,
                'description': description
            }

    async def generate_class(
        self,
        description: str,
        language: str,
        methods: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete class based on description.
        """
        try:
            prompt = self._create_class_prompt(description, language, methods)
            generated_code = await self.llm_service.generate_response(prompt)

            cleaned_code = self._clean_generated_code(generated_code, language)

            return {
                'success': True,
                'code': cleaned_code,
                'language': language,
                'description': description
            }

        except Exception as e:
            logger.error(f"Class generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'language': language,
                'description': description
            }

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

        response = await self.llm_service.generate_response(prompt)

        # Parse suggestions from response
        suggestions = self._parse_code_suggestions(response, language)
        return suggestions

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

        response = await self.llm_service.generate_response(prompt)
        suggestions = self._parse_refactor_suggestions(response, language)
        return suggestions

    async def _generate_test_suggestions(
        self,
        context: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Generate test code suggestions.
        """
        prompt = f"""
        Generate unit tests for this {language} code:

        ```{language}
        {context}
        ```

        Provide test code that covers:
        1. Normal functionality
        2. Edge cases
        3. Error conditions

        Use the appropriate testing framework for {language}.
        """

        response = await self.llm_service.generate_response(prompt)

        return [{
            'type': 'test_generation',
            'title': 'Generated Unit Tests',
            'code': response,
            'language': language,
            'confidence': 0.8
        }]

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

        response = await self.llm_service.generate_response(prompt)

        return [{
            'type': 'general_improvement',
            'title': 'Code Improvement Suggestions',
            'description': response,
            'language': language,
            'confidence': 0.7
        }]

    def _create_function_prompt(
        self,
        description: str,
        language: str,
        parameters: List[Dict[str, str]] = None,
        return_type: str = None
    ) -> str:
        """
        Create a prompt for function generation.
        """
        param_str = ""
        if parameters:
            param_list = []
            for param in parameters:
                name = param.get('name', 'param')
                type_hint = param.get('type', '')
                if language == 'python' and type_hint:
                    param_list.append(f"{name}: {type_hint}")
                else:
                    param_list.append(name)
            param_str = ", ".join(param_list)

        return_type_str = ""
        if return_type:
            if language == 'python':
                return_type_str = f" -> {return_type}"
            elif language in ['typescript', 'java']:
                return_type_str = f": {return_type}"

        prompt = f"""
        Generate a {language} function that {description}

        Function signature: function_name({param_str}){return_type_str}

        Requirements:
        1. Use proper {language} syntax and conventions
        2. Include appropriate error handling
        3. Add docstring/comments explaining the function
        4. Follow {language} best practices
        5. Make the function reusable and well-structured

        Provide only the function code without additional explanation.
        """

        return prompt

    def _create_class_prompt(
        self,
        description: str,
        language: str,
        methods: List[str] = None
    ) -> str:
        """
        Create a prompt for class generation.
        """
        methods_str = ""
        if methods:
            methods_str = "\n".join(f"- {method}" for method in methods)

        prompt = f"""
        Generate a {language} class that {description}

        Required methods:
        {methods_str}

        Requirements:
        1. Use proper {language} class conventions
        2. Include constructor/initializer
        3. Add docstring/comments for the class and methods
        4. Follow {language} best practices
        5. Make the class well-structured and extensible

        Provide only the class code without additional explanation.
        """

        return prompt

    def _clean_generated_code(self, code: str, language: str) -> str:
        """
        Clean up generated code by removing markdown formatting.
        """
        # Remove code block markers
        code = re.sub(r'```\w*\n?', '', code)
        code = re.sub(r'```', '', code)

        # Remove leading/trailing whitespace
        code = code.strip()

        return code

    def _parse_code_suggestions(self, response: str, language: str) -> List[Dict[str, Any]]:
        """
        Parse code suggestions from LLM response.
        """
        suggestions = []

        # Split by numbered suggestions or code blocks
        parts = re.split(r'\n\s*\d+\.|\n\s*Suggestion|\n\s*```', response)

        for i, part in enumerate(parts[1:], 1):  # Skip first empty part
            if part.strip():
                code = self._extract_code_from_text(part, language)
                if code:
                    suggestions.append({
                        'type': 'completion',
                        'title': f'Completion Suggestion {i}',
                        'code': code,
                        'language': language,
                        'confidence': 0.8
                    })

        return suggestions[:3]  # Limit to 3 suggestions

    def _parse_refactor_suggestions(self, response: str, language: str) -> List[Dict[str, Any]]:
        """
        Parse refactoring suggestions from LLM response.
        """
        suggestions = []

        # Split response into individual suggestions
        parts = re.split(r'\n\s*\d+\.|\n\s*Suggestion\s*\d+', response)

        for i, part in enumerate(parts[1:], 1):
            if part.strip():
                code = self._extract_code_from_text(part, language)
                description = self._extract_description_from_text(part)

                suggestions.append({
                    'type': 'refactoring',
                    'title': f'Refactoring Suggestion {i}',
                    'description': description,
                    'code': code,
                    'language': language,
                    'confidence': 0.8
                })

        return suggestions[:3]

    def _extract_code_from_text(self, text: str, language: str) -> str:
        """
        Extract code from mixed text response.
        """
        # Look for code blocks
        code_blocks = re.findall(r'```.*?\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()

        # Fallback: look for indented code
        lines = text.split('\n')
        code_lines = []
        in_code = False

        for line in lines:
            if line.startswith(('def ', 'class ', 'function ', 'const ', 'let ', 'var ')):
                in_code = True
            if in_code:
                code_lines.append(line)
                if line.strip() == '' and len(code_lines) > 3:  # End of code block
                    break

        return '\n'.join(code_lines).strip()

    def _extract_description_from_text(self, text: str) -> str:
        """
        Extract description from mixed text response.
        """
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

        # Get first few lines as description
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        description = ' '.join(lines[:3])  # First 3 non-empty lines

        return description
