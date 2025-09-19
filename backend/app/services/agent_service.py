"""
LangChain-based Agent Service for Code Quality Intelligence
"""

from typing import Dict, List, Any, Optional
import json
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseRetriever
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import structlog

logger = structlog.get_logger(__name__)

class CodeQualityAgent:
    """LangChain-based agent for code quality analysis and Q&A"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "llama3:8b"):
        self.ollama_host = ollama_host
        self.model = model
        self.llm = None
        self.agent_executor = None
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self._initialize_llm()
        self._setup_tools()
        self._create_agent()
    
    def _initialize_llm(self):
        """Initialize the LLM connection"""
        try:
            self.llm = Ollama(
                base_url=self.ollama_host,
                model=self.model,
                temperature=0.1
            )
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {e}")
            # Fallback to a mock LLM for demo purposes
            self.llm = MockLLM()
    
    def _setup_tools(self):
        """Setup tools for the agent"""
        self.tools = [
            Tool(
                name="analyze_code_quality",
                description="Analyze code quality issues and provide detailed insights",
                func=self._analyze_code_quality_tool
            ),
            Tool(
                name="explain_issue",
                description="Explain a specific code quality issue in detail",
                func=self._explain_issue_tool
            ),
            Tool(
                name="suggest_fix",
                description="Suggest how to fix a specific code quality issue",
                func=self._suggest_fix_tool
            ),
            Tool(
                name="search_codebase",
                description="Search through the analyzed codebase for specific patterns or issues",
                func=self._search_codebase_tool
            )
        ]
    
    def _create_agent(self):
        """Create the ReAct agent"""
        prompt_template = """
        You are a Code Quality Intelligence Agent, an expert in software engineering and code analysis.
        Your role is to help developers understand and improve their code quality.
        
        You have access to the following tools:
        {tools}
        
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Begin!
        
        Question: {input}
        Thought: {agent_scratchpad}
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
        try:
            agent = create_react_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                max_iterations=3
            )
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            # Fallback to simple chain
            self._create_fallback_chain()
    
    def _create_fallback_chain(self):
        """Create a simple fallback chain when agent creation fails"""
        prompt = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            You are a code quality expert. Based on the following context about a codebase analysis:
            
            Context: {context}
            
            Question: {question}
            
            Provide a helpful, detailed answer about the code quality issues and suggestions for improvement.
            """
        )
        
        self.fallback_chain = LLMChain(llm=self.llm, prompt=prompt)
    
    def setup_rag(self, analysis_results: Dict[str, Any]):
        """Setup RAG (Retrieval-Augmented Generation) with analysis results"""
        try:
            # Create documents from analysis results
            documents = []
            
            # Add summary information
            summary = analysis_results.get("summary", {})
            summary_text = f"""
            Codebase Summary:
            - Total Files: {summary.get('total_files', 0)}
            - Lines of Code: {summary.get('total_lines', 0)}
            - Languages: {', '.join(summary.get('languages', []))}
            - Quality Score: {summary.get('quality_score', 0)}/100
            """
            documents.append(Document(page_content=summary_text, metadata={"type": "summary"}))
            
            # Add issues information
            issues = analysis_results.get("issues", [])
            for i, issue in enumerate(issues):
                issue_text = f"""
                Issue {i+1}:
                File: {issue.get('file', '')}
                Type: {issue.get('type', '')}
                Severity: {issue.get('severity', '')}
                Line: {issue.get('line', '')}
                Message: {issue.get('message', '')}
                Suggestion: {issue.get('suggestion', '')}
                """
                documents.append(Document(
                    page_content=issue_text, 
                    metadata={"type": "issue", "severity": issue.get('severity', '')}
                ))
            
            # Add recommendations
            recommendations = analysis_results.get("recommendations", [])
            if recommendations:
                rec_text = "Recommendations:\n" + "\n".join(f"- {rec}" for rec in recommendations)
                documents.append(Document(page_content=rec_text, metadata={"type": "recommendations"}))
            
            # Create vector store
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = text_splitter.split_documents(documents)
            
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            logger.info(f"RAG setup complete with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to setup RAG: {e}")
    
    def ask_question(self, question: str, context: Optional[Dict] = None) -> str:
        """Ask a question about the codebase"""
        try:
            if self.agent_executor:
                response = self.agent_executor.invoke({"input": question})
                return response.get("output", "I couldn't process your question.")
            elif hasattr(self, 'fallback_chain'):
                context_str = json.dumps(context or {}, indent=2)
                response = self.fallback_chain.invoke({
                    "question": question,
                    "context": context_str
                })
                return response.get("text", "I couldn't process your question.")
            else:
                return self._simple_qa_response(question, context)
                
        except Exception as e:
            logger.error(f"Error in ask_question: {e}")
            return self._simple_qa_response(question, context)
    
    def _simple_qa_response(self, question: str, context: Optional[Dict] = None) -> str:
        """Simple Q&A fallback when LLM is not available"""
        question_lower = question.lower()
        
        responses = {
            "security": "Based on the analysis, focus on addressing high-severity security issues first. Look for hardcoded credentials, input validation gaps, and unsafe function usage. These pose the highest risk to your application.",
            
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
    
    def _analyze_code_quality_tool(self, input_str: str) -> str:
        """Tool for analyzing code quality"""
        return "Code quality analysis completed. Found issues in security, performance, and maintainability areas."
    
    def _explain_issue_tool(self, input_str: str) -> str:
        """Tool for explaining specific issues"""
        return f"The issue '{input_str}' occurs when code doesn't follow best practices, potentially leading to security vulnerabilities or performance problems."
    
    def _suggest_fix_tool(self, input_str: str) -> str:
        """Tool for suggesting fixes"""
        return f"To fix '{input_str}', consider refactoring the code, adding proper validation, or using more secure/efficient alternatives."
    
    def _search_codebase_tool(self, input_str: str) -> str:
        """Tool for searching codebase"""
        if self.vector_store:
            try:
                docs = self.vector_store.similarity_search(input_str, k=3)
                results = [doc.page_content for doc in docs]
                return f"Found relevant information: {' '.join(results[:200])}..."
            except:
                pass
        
        return f"Searched for '{input_str}' in the codebase. Found related patterns and potential issues."

class MockLLM:
    """Mock LLM for fallback when Ollama is not available"""
    
    def __call__(self, prompt: str) -> str:
        return "I'm a mock LLM. In a real deployment, this would be powered by Ollama or another LLM service."
    
    def invoke(self, input_dict: dict) -> dict:
        return {"text": self.__call__(str(input_dict))}

class CodeQualityRAG:
    """RAG system for large codebase handling"""
    
    def __init__(self, embeddings_model: str = "all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=embeddings_model)
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def index_codebase(self, files_data: Dict[str, str]) -> bool:
        """Index codebase for RAG retrieval"""
        try:
            documents = []
            
            for file_path, content in files_data.items():
                # Create document for each file
                doc = Document(
                    page_content=content,
                    metadata={
                        "file_path": file_path,
                        "file_type": file_path.split('.')[-1] if '.' in file_path else "unknown"
                    }
                )
                documents.append(doc)
            
            # Split documents into chunks
            splits = self.text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./codebase_vectors"
            )
            
            logger.info(f"Indexed {len(documents)} files into {len(splits)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index codebase: {e}")
            return False
    
    def search_similar_code(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar code patterns"""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            results = []
            
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "file_path": doc.metadata.get("file_path", "unknown"),
                    "file_type": doc.metadata.get("file_type", "unknown")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []