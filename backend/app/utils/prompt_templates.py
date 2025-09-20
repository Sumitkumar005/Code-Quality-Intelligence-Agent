"""
AI Prompt Templates for Code Quality Intelligence Agent

This module contains all the prompt templates used by the AI agent
for code analysis, Q&A, and code generation tasks.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class PromptTemplates:
    """Collection of prompt templates for different AI tasks."""

    # Code Analysis Prompts
    CODE_ANALYSIS_PROMPT = """
You are a senior software engineer and code quality expert. Analyze the following code and provide detailed feedback.

Code to analyze:
{code}

Language: {language}
File path: {file_path}

Please provide analysis in the following format:
1. **Overall Assessment**: Brief summary of code quality
2. **Issues Found**: List of specific issues with severity levels
3. **Suggestions**: Concrete improvement recommendations
4. **Best Practices**: Any best practices being followed or violated
5. **Security Concerns**: Any potential security issues
6. **Performance Issues**: Any performance bottlenecks or inefficiencies

Be specific, actionable, and professional in your feedback.
"""

    SECURITY_ANALYSIS_PROMPT = """
You are a cybersecurity expert. Analyze the following code for security vulnerabilities.

Code to analyze:
{code}

Language: {language}
File path: {file_path}

Focus on:
- OWASP Top 10 vulnerabilities
- Input validation issues
- Authentication/authorization problems
- Data exposure risks
- Injection vulnerabilities
- Cryptographic weaknesses
- Configuration issues

Provide specific examples from the code and suggest secure alternatives.
"""

    PERFORMANCE_ANALYSIS_PROMPT = """
You are a performance optimization expert. Analyze the following code for performance issues.

Code to analyze:
{code}

Language: {language}
File path: {file_path}

Look for:
- Algorithmic inefficiencies
- Memory leaks
- Unnecessary computations
- I/O bottlenecks
- Database query optimization
- Caching opportunities
- Resource management issues

Suggest specific optimizations with performance impact estimates.
"""

    COMPLEXITY_ANALYSIS_PROMPT = """
You are a software architecture expert. Analyze the following code for complexity and maintainability issues.

Code to analyze:
{code}

Language: {language}
File path: {file_path}

Analyze:
- Cyclomatic complexity
- Code duplication
- Function/method length
- Class/interface design
- Coupling and cohesion
- Technical debt indicators
- Maintainability index

Provide refactoring suggestions to improve code quality.
"""

    # Q&A Prompts
    CODE_QUESTION_PROMPT = """
You are a senior software engineer helping a developer understand their codebase.

Context:
- Project: {project_name}
- Language: {language}
- User's question: {question}

Relevant code context:
{code_context}

Please provide a clear, detailed answer that:
1. Directly addresses the question
2. Provides relevant code examples
3. Explains the reasoning behind the answer
4. Suggests best practices when applicable
5. Mentions any potential pitfalls or edge cases

Be educational and help the developer understand both the 'what' and the 'why'.
"""

    DEBUGGING_PROMPT = """
You are a debugging expert helping a developer troubleshoot an issue.

Issue description: {issue_description}
Error message: {error_message}
Relevant code: {code}

Please help debug this issue by:
1. Analyzing the error message and symptoms
2. Identifying potential root causes
3. Suggesting debugging steps
4. Providing a solution or workaround
5. Explaining how to prevent similar issues in the future

Be systematic and thorough in your debugging approach.
"""

    # Code Generation Prompts
    REFACTORING_PROMPT = """
You are a code refactoring expert. Help improve the following code while maintaining its functionality.

Original code:
{original_code}

Language: {language}
Refactoring goals: {refactoring_goals}

Please provide:
1. Refactored code that improves the original
2. Explanation of improvements made
3. Any trade-offs or considerations
4. Tests to verify the refactoring works correctly

Ensure the refactored code is:
- More readable and maintainable
- Following language best practices
- Properly documented
- Efficient and performant
"""

    TEST_GENERATION_PROMPT = """
You are a testing expert. Generate comprehensive tests for the following code.

Code to test:
{code}

Language: {language}
Testing framework: {test_framework}

Please generate:
1. Unit tests covering all public methods/functions
2. Edge case tests
3. Error condition tests
4. Integration tests if applicable
5. Mock objects and test data setup

Include both positive and negative test cases.
"""

    DOCUMENTATION_PROMPT = """
You are a technical documentation expert. Generate comprehensive documentation for the following code.

Code to document:
{code}

Language: {language}
Documentation style: {doc_style}

Please provide:
1. Module/class/function overview
2. Parameter descriptions
3. Return value documentation
4. Usage examples
5. Exception/error documentation
6. Notes and warnings

Follow the documentation standards for the specified language and style.
"""

    # Context Management Prompts
    CONTEXT_AWARE_PROMPT = """
You are an AI assistant with access to the codebase context. Use the provided context to give more accurate and relevant answers.

Current context:
- Project: {project_name}
- Current file: {current_file}
- Related files: {related_files}
- Recent changes: {recent_changes}
- User role: {user_role}

User question: {question}

Additional context from codebase:
{codebase_context}

Please use this context to provide a more informed and specific answer.
"""

    # Specialized Analysis Prompts
    DEPENDENCY_ANALYSIS_PROMPT = """
Analyze the dependencies in the following code and identify potential issues.

Code: {code}
Language: {language}

Focus on:
- Outdated dependencies
- Security vulnerabilities in dependencies
- License compatibility issues
- Unused dependencies
- Circular dependencies
- Version conflicts

Provide specific recommendations for dependency management.
"""

    DOCUMENTATION_ANALYSIS_PROMPT = """
Analyze the documentation quality of the following code.

Code: {code}
Language: {language}

Evaluate:
- Inline documentation coverage
- API documentation completeness
- Code comment quality
- README and external documentation
- Examples and tutorials

Suggest improvements to documentation practices.
"""

    # Multi-language Support
    MULTI_LANGUAGE_PROMPT = """
You are a polyglot programmer. The following code is in {language}.

Code:
{code}

Please analyze this code according to {language} best practices and conventions.
"""

    # Report Generation Prompts
    EXECUTIVE_SUMMARY_PROMPT = """
Generate an executive summary for a code quality report.

Analysis Results:
{analysis_results}

Key Metrics:
{key_metrics}

Please provide:
1. Overall quality assessment
2. Key findings and issues
3. Priority recommendations
4. Risk assessment
5. Next steps

Keep the summary concise but comprehensive for management review.
"""

    TECHNICAL_REPORT_PROMPT = """
Generate a detailed technical report for developers.

Analysis Details:
{analysis_details}

Technical Findings:
{technical_findings}

Please provide:
1. Detailed issue descriptions
2. Code examples and explanations
3. Technical recommendations
4. Implementation guidance
5. Testing considerations

Focus on technical depth and actionable insights.
"""


def get_prompt_template(template_name: str, **kwargs) -> str:
    """
    Get a formatted prompt template by name.

    Args:
        template_name: Name of the template to retrieve
        **kwargs: Variables to format into the template

    Returns:
        Formatted prompt string
    """
    templates = PromptTemplates()

    template_map = {
        'code_analysis': templates.CODE_ANALYSIS_PROMPT,
        'security_analysis': templates.SECURITY_ANALYSIS_PROMPT,
        'performance_analysis': templates.PERFORMANCE_ANALYSIS_PROMPT,
        'complexity_analysis': templates.COMPLEXITY_ANALYSIS_PROMPT,
        'code_question': templates.CODE_QUESTION_PROMPT,
        'debugging': templates.DEBUGGING_PROMPT,
        'refactoring': templates.REFACTORING_PROMPT,
        'test_generation': templates.TEST_GENERATION_PROMPT,
        'documentation': templates.DOCUMENTATION_PROMPT,
        'context_aware': templates.CONTEXT_AWARE_PROMPT,
        'dependency_analysis': templates.DEPENDENCY_ANALYSIS_PROMPT,
        'documentation_analysis': templates.DOCUMENTATION_ANALYSIS_PROMPT,
        'multi_language': templates.MULTI_LANGUAGE_PROMPT,
        'executive_summary': templates.EXECUTIVE_SUMMARY_PROMPT,
        'technical_report': templates.TECHNICAL_REPORT_PROMPT,
    }

    if template_name not in template_map:
        raise ValueError(f"Unknown template: {template_name}")

    template = template_map[template_name]

    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required parameter for template {template_name}: {e}")


def list_available_templates() -> List[str]:
    """
    List all available prompt template names.

    Returns:
        List of template names
    """
    return [
        'code_analysis', 'security_analysis', 'performance_analysis',
        'complexity_analysis', 'code_question', 'debugging', 'refactoring',
        'test_generation', 'documentation', 'context_aware',
        'dependency_analysis', 'documentation_analysis', 'multi_language',
        'executive_summary', 'technical_report'
    ]


def validate_template_variables(template_name: str, variables: Dict[str, Any]) -> List[str]:
    """
    Validate that all required variables are provided for a template.

    Args:
        template_name: Name of the template
        variables: Dictionary of variables to check

    Returns:
        List of missing variable names
    """
    templates = PromptTemplates()
    template_map = {
        'code_analysis': templates.CODE_ANALYSIS_PROMPT,
        'security_analysis': templates.SECURITY_ANALYSIS_PROMPT,
        'performance_analysis': templates.PERFORMANCE_ANALYSIS_PROMPT,
        'complexity_analysis': templates.COMPLEXITY_ANALYSIS_PROMPT,
        'code_question': templates.CODE_QUESTION_PROMPT,
        'debugging': templates.DEBUGGING_PROMPT,
        'refactoring': templates.REFACTORING_PROMPT,
        'test_generation': templates.TEST_GENERATION_PROMPT,
        'documentation': templates.DOCUMENTATION_PROMPT,
        'context_aware': templates.CONTEXT_AWARE_PROMPT,
        'dependency_analysis': templates.DEPENDENCY_ANALYSIS_PROMPT,
        'documentation_analysis': templates.DOCUMENTATION_ANALYSIS_PROMPT,
        'multi_language': templates.MULTI_LANGUAGE_PROMPT,
        'executive_summary': templates.EXECUTIVE_SUMMARY_PROMPT,
        'technical_report': templates.TECHNICAL_REPORT_PROMPT,
    }

    if template_name not in template_map:
        return [f"Unknown template: {template_name}"]

    template = template_map[template_name]
    import string

    # Extract variable names from template
    formatter = string.Formatter()
    required_vars = [field_name for _, field_name, _, _ in formatter.parse(template) if field_name]

    missing_vars = []
    for var in required_vars:
        if var and var not in variables:
            missing_vars.append(var)

    return missing_vars
