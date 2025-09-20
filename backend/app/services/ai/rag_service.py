"""
RAG (Retrieval-Augmented Generation) service for context-aware AI responses.
"""

import asyncio
from typing import Dict, List, Any, Optional
import numpy as np

from app.core.logging import get_logger
from app.core.config import settings
from .embeddings import EmbeddingsService

logger = get_logger(__name__)


class RAGService:
    """
    RAG service for retrieving relevant context and generating responses.
    """

    def __init__(self):
        self.embeddings_service = EmbeddingsService()
        self.vector_store = {}  # In production, this would be ChromaDB
        self.documents = []

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Add documents to the vector store.
        """
        try:
            if not documents:
                return False

            # Generate embeddings for documents
            texts = [doc.get('content', doc) if isinstance(doc, dict) else str(doc) for doc in documents]
            embeddings = await self.embeddings_service.generate_embeddings(texts)

            # Store documents with embeddings
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                doc_id = f"doc_{len(self.documents) + i}"
                self.vector_store[doc_id] = {
                    'id': doc_id,
                    'content': doc.get('content', doc) if isinstance(doc, dict) else str(doc),
                    'embedding': embedding,
                    'metadata': metadata[i] if metadata and i < len(metadata) else {}
                }
                self.documents.append(doc_id)

            logger.info(f"Added {len(documents)} documents to vector store")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    async def retrieve_relevant_context(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.
        """
        try:
            if not self.vector_store:
                return []

            # Generate embedding for query
            query_embedding = await self.embeddings_service.generate_embeddings([query])
            if not query_embedding:
                return []

            query_embedding = query_embedding[0]

            # Calculate similarities
            similarities = []
            for doc_id, doc_data in self.vector_store.items():
                similarity = await self.embeddings_service.calculate_similarity(
                    query_embedding, doc_data['embedding']
                )
                similarities.append((doc_id, similarity, doc_data))

            # Sort by similarity and filter by threshold
            similarities.sort(key=lambda x: x[1], reverse=True)
            relevant_docs = [
                {
                    'id': doc_id,
                    'content': doc_data['content'],
                    'similarity': similarity,
                    'metadata': doc_data['metadata']
                }
                for doc_id, similarity, doc_data in similarities[:top_k]
                if similarity >= threshold
            ]

            return relevant_docs

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []

    async def generate_response_with_context(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response using retrieved context.
        """
        try:
            if not context_docs:
                return "No relevant context found for the query."

            # Build context string
            context_str = "\n\n".join([
                f"Context {i+1}:\n{doc['content']}"
                for i, doc in enumerate(context_docs)
            ])

            # Create enhanced prompt
            enhanced_prompt = f"""
            {system_prompt or "You are a helpful AI assistant. Use the provided context to answer the user's question."}

            Relevant Context:
            {context_str}

            User Question: {query}

            Please provide a comprehensive answer based on the context provided above.
            If the context doesn't contain enough information to fully answer the question,
            please state that clearly.
            """

            # Use LLM to generate response (this would be integrated with LLMClient)
            # For now, return a placeholder response
            return f"Based on the provided context, here's my analysis of your query: '{query}'"

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"Error generating response: {e}"

    async def search_similar_code(
        self,
        code_query: str,
        language: str = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar code snippets.
        """
        try:
            # Add language context if provided
            search_text = code_query
            if language:
                search_text = f"```{language}\n{code_query}\n```"

            return await self.retrieve_relevant_context(search_text, top_k)

        except Exception as e:
            logger.error(f"Similar code search failed: {e}")
            return []

    async def get_code_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 10
    ) -> Dict[str, Any]:
        """
        Get context around a specific line in code.
        """
        try:
            # Find documents related to this file
            relevant_docs = [
                doc for doc in self.vector_store.values()
                if doc['metadata'].get('file_path') == file_path
            ]

            if not relevant_docs:
                return {'context': '', 'line_number': line_number}

            # Find the most relevant context
            target_doc = relevant_docs[0]  # Simplified - would need better logic

            return {
                'context': target_doc['content'],
                'line_number': line_number,
                'file_path': file_path
            }

        except Exception as e:
            logger.error(f"Code context retrieval failed: {e}")
            return {'context': '', 'line_number': line_number}

    async def clear_documents(self) -> bool:
        """
        Clear all documents from the vector store.
        """
        try:
            self.vector_store.clear()
            self.documents.clear()
            logger.info("Cleared all documents from vector store")
            return True
        except Exception as e:
            logger.error(f"Failed to clear documents: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        """
        try:
            return {
                'total_documents': len(self.documents),
                'vector_store_size': len(self.vector_store),
                'embedding_dimension': len(next(iter(self.vector_store.values()))['embedding']) if self.vector_store else 0
            }
        except Exception:
            return {
                'total_documents': 0,
                'vector_store_size': 0,
                'embedding_dimension': 0
            }

    async def check_health(self) -> bool:
        """
        Check if the RAG service is healthy.
        """
        try:
            # Test basic functionality
            test_docs = [{"content": "test document", "metadata": {}}]
            await self.add_documents(test_docs)
            await self.retrieve_relevant_context("test")
            await self.clear_documents()
            return True
        except Exception:
            return False
