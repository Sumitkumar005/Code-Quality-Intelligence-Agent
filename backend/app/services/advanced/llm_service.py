"""
Simple LLM Service with Ollama integration and RAG
"""
import ollama
import json
from typing import Dict, Any, Optional
from .rag_service import rag_service

class LLMService:
    """Simple LLM service for Q&A"""
    
    def __init__(self):
        self.model = "gemma3:4b"  # Your working Gemma3:4b model
        self.ollama_available = False
        self._check_ollama()
    
    def _check_ollama(self):
        """Check if Ollama is available"""
        try:
            # Try to list models
            models = ollama.list()
            self.ollama_available = True
            print(f"✅ Ollama available with {len(models.get('models', []))} models")
            
            # Check if our model is available
            model_names = [m.model for m in models.models] if hasattr(models, 'models') else []
            if not any(self.model in name for name in model_names):
                print(f"📥 Downloading {self.model} model...")
                ollama.pull(self.model)
                print(f"✅ Model {self.model} ready!")
            else:
                print(f"✅ Model {self.model} found and ready!")
                
        except Exception as e:
            print(f"⚠️  Ollama not available: {e}")
            self.ollama_available = False
    
    def ask_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Ask a question with context and RAG"""
        
        if not self.ollama_available:
            return self._fallback_response(question, context)
        
        try:
            # Prepare basic context
            context_str = ""
            if context and "summary" in context:
                summary = context["summary"]
                context_str = f"""
Code Analysis Summary:
- Total Files: {summary.get('total_files', 0)}
- Lines of Code: {summary.get('total_lines', 0)}
- Languages: {', '.join(summary.get('languages', []))}
- Quality Score: {summary.get('quality_score', 0)}/100
- Issues Found: {len(context.get('issues', []))}
"""
            
            # Get RAG context (relevant code chunks)
            rag_context = rag_service.get_context_for_llm(question)
            
            # Create enhanced prompt with RAG
            prompt = f"""You are a code quality expert analyzing a codebase. 

{context_str}

Relevant Code Context:
{rag_context}

Question: {question}

Based on the specific code shown above and the analysis summary, provide a detailed, actionable answer. Reference specific files, line numbers, and code patterns when possible."""

            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            return response['message']['content']
            
        except Exception as e:
            print(f"LLM error: {e}")
            return self._fallback_response(question, context)
    
    def _fallback_response(self, question: str, context: Optional[Dict] = None) -> str:
        """Fallback responses when LLM is not available"""
        question_lower = question.lower()
        
        responses = {
            "security": "Based on your analysis, focus on addressing high-severity security issues first. Look for hardcoded credentials, input validation gaps, and unsafe function usage. These pose the highest risk to your application.",
            
            "performance": "The main performance issues identified include inefficient loops, string concatenation in loops, and potential memory leaks. Consider optimizing algorithms, using appropriate data structures, and implementing caching where beneficial.",
            
            "quality": "Code quality can be improved by reducing function complexity, adding proper documentation, following consistent naming conventions, and breaking large files into smaller, focused modules.",
            
            "test": "Improve test coverage by adding unit tests for critical functions, integration tests for key workflows, and edge case testing. Focus on testing business logic and error handling paths.",
            
            "complexity": "High complexity areas should be refactored into smaller, more manageable functions. Consider using design patterns, extracting common functionality, and improving code organization.",
            
            "documentation": "Add docstrings to functions and classes, create README files for modules, and include inline comments for complex logic. Good documentation improves maintainability and team collaboration."
        }
        
        # Find matching response
        for keyword, response in responses.items():
            if keyword in question_lower:
                return response
        
        # Default response with context
        if context and "summary" in context:
            summary = context["summary"]
            return f"""Based on your codebase analysis:
            
- You have {summary.get('total_files', 0)} files with {summary.get('total_lines', 0):,} lines of code
- Quality score: {summary.get('quality_score', 0)}/100
- Languages: {', '.join(summary.get('languages', []))}

I can help you understand specific aspects of your code quality. Try asking about security, performance, testing, or code complexity issues."""
        
        return "I can help you understand your code analysis results. Try asking about security issues, performance problems, code quality improvements, or testing recommendations."

# Global LLM service instance
llm_service = LLMService()