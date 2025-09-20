"""
Main AI agent service for coordinating AI-powered features.
"""

from typing import Dict, List, Any, Optional
import asyncio

from app.core.logging import get_logger
from app.core.config import settings
from .llm_client import LLMClient
from .rag_service import RAGService
from .embeddings import EmbeddingsService

logger = get_logger(__name__)


class AgentService:
    """
    Main AI agent that coordinates various AI-powered features.
    """

    def __init__(self):
        self.llm_client = LLMClient()
        self.rag_service = RAGService()
        self.embeddings_service = EmbeddingsService()

    async def analyze_code_with_ai(
        self,
        code: str,
        language: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze code using AI models.
        """
        try:
            logger.info(f"Starting AI code analysis for {language} code")

            # Generate embeddings for code understanding
            embeddings = await self.embeddings_service.generate_embeddings([code])

            # Use LLM for analysis
            analysis_prompt = self._create_analysis_prompt(code, language, analysis_type)
            analysis_result = await self.llm_client.generate_response(analysis_prompt)

            # Generate improvement suggestions
            improvement_prompt = self._create_improvement_prompt(code, language, analysis_result)
            improvements = await self.llm_client.generate_response(improvement_prompt)

            return {
                'success': True,
                'analysis': analysis_result,
                'improvements': improvements,
                'embeddings': embeddings,
                'language': language,
                'analysis_type': analysis_type
            }

        except Exception as e:
            logger.error(f"AI code analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'language': language,
                'analysis_type': analysis_type
            }

    async def generate_code_suggestions(
        self,
        context: str,
        language: str,
        suggestion_type: str = "completion"
    ) -> Dict[str, Any]:
        """
        Generate code suggestions using AI.
        """
        try:
            suggestions = await self.llm_client.generate_suggestions(
                context, language, suggestion_type
            )

            return {
                'success': True,
                'suggestions': suggestions,
                'language': language,
                'type': suggestion_type
            }

        except Exception as e:
            logger.error(f"Code suggestion generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'language': language,
                'type': suggestion_type
            }

    async def explain_code(
        self,
        code: str,
        language: str,
        detail_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Generate natural language explanation of code.
        """
        try:
            explanation_prompt = f"""
            Explain the following {language} code in {detail_level} detail.
            Provide a clear, step-by-step explanation of what the code does:

            ```{language}
            {code}
            ```

            Focus on:
            1. Overall purpose
            2. Key components and logic flow
            3. Important concepts or patterns used
            4. Potential improvements or considerations
            """

            explanation = await self.llm_client.generate_response(explanation_prompt)

            return {
                'success': True,
                'explanation': explanation,
                'language': language,
                'detail_level': detail_level
            }

        except Exception as e:
            logger.error(f"Code explanation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'language': language,
                'detail_level': detail_level
            }

    async def detect_code_smells(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Use AI to detect code smells and anti-patterns.
        """
        try:
            smell_prompt = f"""
            Analyze the following {language} code for code smells, anti-patterns, and potential issues:

            ```{language}
            {code}
            ```

            Identify:
            1. Code smells (long methods, duplicated code, etc.)
            2. Anti-patterns (singleton abuse, tight coupling, etc.)
            3. Maintainability issues
            4. Performance concerns
            5. Security vulnerabilities

            For each issue found, provide:
            - Issue type and severity
            - Location in code
            - Description of the problem
            - Suggested fix or improvement
            """

            analysis = await self.llm_client.generate_response(smell_prompt)

            return {
                'success': True,
                'code_smells': analysis,
                'language': language
            }

        except Exception as e:
            logger.error(f"Code smell detection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'language': language
            }

    def _create_analysis_prompt(self, code: str, language: str, analysis_type: str) -> str:
        """
        Create a prompt for code analysis.
        """
        base_prompt = f"""
        Analyze the following {language} code:

        ```{language}
        {code}
        ```

        Provide a comprehensive analysis including:
        """

        if analysis_type == "security":
            base_prompt += """
            - Security vulnerabilities
            - Input validation issues
            - Authentication/authorization problems
            - Data exposure risks
            - Injection vulnerabilities
            """
        elif analysis_type == "performance":
            base_prompt += """
            - Performance bottlenecks
            - Inefficient algorithms
            - Memory usage issues
            - I/O optimization opportunities
            - Scalability concerns
            """
        elif analysis_type == "maintainability":
            base_prompt += """
            - Code complexity
            - Readability issues
            - Documentation gaps
            - Coupling and cohesion
            - Testability concerns
            """
        else:
            base_prompt += """
            - Overall code quality
            - Best practices compliance
            - Potential improvements
            - Strengths and weaknesses
            - Recommendations
            """

        return base_prompt

    def _create_improvement_prompt(self, code: str, language: str, analysis: str) -> str:
        """
        Create a prompt for generating improvement suggestions.
        """
        return f"""
        Based on the following code analysis, suggest specific improvements:

        Code:
        ```{language}
        {code}
        ```

        Analysis:
        {analysis}

        Provide concrete suggestions for:
        1. Code refactoring opportunities
        2. Best practices to implement
        3. Performance optimizations
        4. Security enhancements
        5. Maintainability improvements

        For each suggestion, include:
        - What to change
        - Why it's beneficial
        - How to implement it
        """
