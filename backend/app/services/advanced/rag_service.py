"""
RAG (Retrieval-Augmented Generation) Service for Code Analysis
"""
import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path

class SimpleRAG:
    """Simple RAG implementation without heavy dependencies"""
    
    def __init__(self):
        self.code_chunks = {}  # file_path -> {content, metadata}
        self.indexed_files = set()
        
    def index_codebase(self, files_data: Dict[str, str], analysis_results: Dict[str, Any]):
        """Index codebase for retrieval"""
        print(f"🔍 Indexing {len(files_data)} files for RAG...")
        
        # Clear previous index
        self.code_chunks.clear()
        self.indexed_files.clear()
        
        # Index each file
        for file_path, content in files_data.items():
            self._index_file(file_path, content, analysis_results)
        
        print(f"✅ RAG index ready with {len(self.code_chunks)} chunks")
    
    def _index_file(self, file_path: str, content: str, analysis_results: Dict[str, Any]):
        """Index a single file"""
        lines = content.splitlines()
        
        # Find issues in this file
        file_issues = [
            issue for issue in analysis_results.get("issues", [])
            if issue.get("file", "").endswith(Path(file_path).name)
        ]
        
        # Create chunks (simple line-based chunking)
        chunk_size = 50  # lines per chunk
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = "\n".join(chunk_lines)
            
            # Create chunk metadata
            chunk_id = f"{file_path}:{i}-{i+len(chunk_lines)}"
            
            self.code_chunks[chunk_id] = {
                "file_path": file_path,
                "content": chunk_content,
                "start_line": i + 1,
                "end_line": i + len(chunk_lines),
                "issues": [
                    issue for issue in file_issues
                    if i + 1 <= issue.get("line", 0) <= i + len(chunk_lines)
                ],
                "language": self._detect_language(file_path),
                "keywords": self._extract_keywords(chunk_content)
            }
        
        self.indexed_files.add(file_path)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cs': 'csharp'
        }
        return lang_map.get(ext, 'unknown')
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from code content"""
        # Simple keyword extraction
        keywords = []
        
        # Security-related keywords
        security_keywords = ['password', 'secret', 'key', 'token', 'auth', 'login', 'credential']
        for keyword in security_keywords:
            if keyword in content.lower():
                keywords.append(f"security:{keyword}")
        
        # Performance-related keywords  
        perf_keywords = ['loop', 'for', 'while', 'query', 'database', 'cache']
        for keyword in perf_keywords:
            if keyword in content.lower():
                keywords.append(f"performance:{keyword}")
        
        # Function/class names (simple extraction)
        import re
        functions = re.findall(r'def\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        
        keywords.extend([f"function:{func}" for func in functions[:5]])  # Limit to 5
        keywords.extend([f"class:{cls}" for cls in classes[:5]])
        
        return keywords
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant code chunks"""
        if not self.code_chunks:
            return []
        
        query_lower = query.lower()
        scored_chunks = []
        
        for chunk_id, chunk_data in self.code_chunks.items():
            score = self._calculate_relevance_score(query_lower, chunk_data)
            if score > 0:
                scored_chunks.append({
                    "chunk_id": chunk_id,
                    "score": score,
                    "data": chunk_data
                })
        
        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
    
    def _calculate_relevance_score(self, query: str, chunk_data: Dict[str, Any]) -> float:
        """Calculate relevance score for a chunk"""
        score = 0.0
        
        # File name match
        if any(word in chunk_data["file_path"].lower() for word in query.split()):
            score += 2.0
        
        # Content match
        content_lower = chunk_data["content"].lower()
        query_words = query.split()
        
        for word in query_words:
            if word in content_lower:
                score += 1.0
        
        # Keyword match
        for keyword in chunk_data["keywords"]:
            if any(word in keyword.lower() for word in query_words):
                score += 1.5
        
        # Issues match (higher priority for chunks with issues)
        if chunk_data["issues"]:
            for issue in chunk_data["issues"]:
                issue_text = f"{issue.get('type', '')} {issue.get('message', '')}".lower()
                if any(word in issue_text for word in query_words):
                    score += 3.0  # High priority for issue matches
        
        # Language match
        if chunk_data["language"] in query:
            score += 1.0
        
        return score
    
    def get_context_for_llm(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for LLM prompt"""
        relevant_chunks = self.search(query, top_k=5)
        
        if not relevant_chunks:
            return "No specific code context found for this query."
        
        context_parts = []
        current_length = 0
        
        for chunk in relevant_chunks:
            chunk_data = chunk["data"]
            
            # Format chunk for LLM
            chunk_text = f"""
File: {chunk_data['file_path']} (lines {chunk_data['start_line']}-{chunk_data['end_line']})
Language: {chunk_data['language']}
"""
            
            # Add issues if present
            if chunk_data['issues']:
                chunk_text += "Issues found:\n"
                for issue in chunk_data['issues']:
                    chunk_text += f"- {issue.get('severity', 'Unknown')} {issue.get('type', '')}: {issue.get('message', '')}\n"
            
            chunk_text += f"\nCode:\n```{chunk_data['language']}\n{chunk_data['content'][:500]}...\n```\n"
            
            # Check if adding this chunk exceeds limit
            if current_length + len(chunk_text) > max_context_length:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)

# Global RAG service
rag_service = SimpleRAG()