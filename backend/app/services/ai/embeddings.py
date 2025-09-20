"""
Text embeddings service for semantic search and similarity calculations.
"""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
import hashlib

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class EmbeddingsService:
    """
    Service for generating and managing text embeddings.
    """

    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Default model
        self.embedding_dimension = 384  # Dimension for the default model
        self.cache = {}  # Simple in-memory cache

    async def generate_embeddings(
        self,
        texts: List[str],
        model_name: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        """
        try:
            if not texts:
                return []

            model_name = model_name or self.model_name
            embeddings = []

            for text in texts:
                # Check cache first
                cache_key = self._get_cache_key(text, model_name)
                if cache_key in self.cache:
                    embeddings.append(self.cache[cache_key])
                    continue

                # Generate embedding (in production, this would use actual ML model)
                embedding = await self._generate_single_embedding(text, model_name)

                # Cache the result
                self.cache[cache_key] = embedding
                embeddings.append(embedding)

            return embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    async def _generate_single_embedding(
        self,
        text: str,
        model_name: str
    ) -> List[float]:
        """
        Generate embedding for a single text.
        In production, this would use a real embedding model.
        """
        try:
            # Simple hash-based embedding for demonstration
            # In production, this would use sentence-transformers or OpenAI embeddings
            text_hash = hashlib.md5(text.encode()).hexdigest()

            # Generate pseudo-random but deterministic embedding
            np.random.seed(int(text_hash[:8], 16))

            # Normalize to unit length
            embedding = np.random.randn(self.embedding_dimension)
            embedding = embedding / np.linalg.norm(embedding)

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Single embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension

    async def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
        method: str = "cosine"
    ) -> float:
        """
        Calculate similarity between two embeddings.
        """
        try:
            if method == "cosine":
                return await self._cosine_similarity(embedding1, embedding2)
            elif method == "euclidean":
                return await self._euclidean_similarity(embedding1, embedding2)
            else:
                return await self._cosine_similarity(embedding1, embedding2)

        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    async def _cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))

        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0

    async def _euclidean_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate Euclidean similarity (inverse distance) between two embeddings.
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            distance = np.linalg.norm(vec1 - vec2)

            # Convert distance to similarity (inverse relationship)
            # Normalize to 0-1 range
            max_distance = np.sqrt(2 * len(vec1))  # Maximum possible distance
            similarity = 1.0 - (distance / max_distance)

            return float(max(0.0, similarity))

        except Exception as e:
            logger.error(f"Euclidean similarity calculation failed: {e}")
            return 0.0

    async def find_similar_texts(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        texts: List[str],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Find texts most similar to the query embedding.
        """
        try:
            if not embeddings or not texts:
                return []

            similarities = []
            for i, embedding in enumerate(embeddings):
                similarity = await self.calculate_similarity(query_embedding, embedding)
                similarities.append((i, similarity, texts[i]))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Filter by threshold and limit to top_k
            results = []
            for i, similarity, text in similarities[:top_k]:
                if similarity >= threshold:
                    results.append({
                        'index': i,
                        'text': text,
                        'similarity': similarity
                    })

            return results

        except Exception as e:
            logger.error(f"Similar text search failed: {e}")
            return []

    async def cluster_embeddings(
        self,
        embeddings: List[List[float]],
        n_clusters: int = 5
    ) -> List[List[int]]:
        """
        Cluster embeddings using simple k-means.
        """
        try:
            if not embeddings or n_clusters <= 0:
                return []

            # Simple k-means implementation for demonstration
            # In production, would use scikit-learn or similar
            vectors = np.array(embeddings)

            # Initialize centroids randomly
            np.random.seed(42)
            centroid_indices = np.random.choice(len(vectors), n_clusters, replace=False)
            centroids = vectors[centroid_indices]

            # Simple k-means iteration
            for _ in range(10):  # Max iterations
                # Assign points to clusters
                distances = np.array([
                    [np.linalg.norm(vec - centroid) for centroid in centroids]
                    for vec in vectors
                ])
                cluster_assignments = np.argmin(distances, axis=1)

                # Update centroids
                new_centroids = []
                for i in range(n_clusters):
                    cluster_points = vectors[cluster_assignments == i]
                    if len(cluster_points) > 0:
                        new_centroids.append(np.mean(cluster_points, axis=0))
                    else:
                        new_centroids.append(centroids[i])  # Keep old centroid

                centroids = np.array(new_centroids)

            # Group indices by cluster
            clusters = [[] for _ in range(n_clusters)]
            for i, cluster_id in enumerate(cluster_assignments):
                clusters[cluster_id].append(i)

            return clusters

        except Exception as e:
            logger.error(f"Embedding clustering failed: {e}")
            return []

    def _get_cache_key(self, text: str, model_name: str) -> str:
        """
        Generate a cache key for text and model combination.
        """
        content_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{model_name}:{content_hash}"

    async def clear_cache(self) -> bool:
        """
        Clear the embedding cache.
        """
        try:
            self.cache.clear()
            logger.info("Cleared embedding cache")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        """
        try:
            return {
                'cache_size': len(self.cache),
                'embedding_dimension': self.embedding_dimension,
                'model_name': self.model_name
            }
        except Exception:
            return {
                'cache_size': 0,
                'embedding_dimension': 0,
                'model_name': self.model_name
            }

    async def check_health(self) -> bool:
        """
        Check if the embeddings service is healthy.
        """
        try:
            # Test embedding generation
            test_texts = ["test text"]
            embeddings = await self.generate_embeddings(test_texts)
            return len(embeddings) == 1 and len(embeddings[0]) == self.embedding_dimension
        except Exception:
            return False
