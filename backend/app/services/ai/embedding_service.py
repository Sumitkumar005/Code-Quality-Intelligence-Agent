"""
Embedding service for generating vector embeddings.
"""

import aiohttp
import numpy as np
from typing import List, Dict, Any, Optional
import asyncio

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using AI models.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = settings.EMBEDDING_MODEL or "text-embedding-ada-002"
        self.dimension = 1536  # Dimension for text-embedding-ada-002

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        """
        try:
            if not texts:
                return []

            # Prepare payload
            payload = {
                "input": texts,
                "model": self.model
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        embeddings = [item["embedding"] for item in data["data"]]
                        return embeddings
                    else:
                        error_data = await response.json()
                        raise Exception(f"Embedding API error: {error_data}")

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def generate_code_embedding(self, code: str, language: str) -> List[float]:
        """
        Generate embedding specifically for code snippets.
        """
        # Enhance code with language context for better embeddings
        enhanced_code = f"```{language}\n{code}\n```"
        embeddings = await self.generate_embeddings([enhanced_code])
        return embeddings[0] if embeddings else []

    async def calculate_similarity(
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

            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    async def find_similar_code(
        self,
        query_embedding: List[float],
        code_embeddings: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar code snippets based on embeddings.
        """
        try:
            similarities = []

            for item in code_embeddings:
                embedding = item.get("embedding", [])
                if embedding:
                    similarity = await self.calculate_similarity(query_embedding, embedding)
                    similarities.append({
                        "item": item,
                        "similarity": similarity
                    })

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)

            # Return top-k results
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Similar code search failed: {e}")
            return []

    async def cluster_embeddings(
        self,
        embeddings: List[List[float]],
        n_clusters: int = 5
    ) -> List[int]:
        """
        Cluster embeddings using K-means.
        """
        try:
            from sklearn.cluster import KMeans

            if len(embeddings) < n_clusters:
                # Return all items in cluster 0 if not enough data
                return [0] * len(embeddings)

            # Convert to numpy array
            X = np.array(embeddings)

            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X)

            return clusters.tolist()

        except ImportError:
            logger.warning("scikit-learn not available for clustering")
            return [0] * len(embeddings)
        except Exception as e:
            logger.error(f"Embedding clustering failed: {e}")
            return [0] * len(embeddings)

    async def batch_generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for large lists in batches.
        """
        try:
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = await self.generate_embeddings(batch)
                all_embeddings.extend(batch_embeddings)

                # Small delay to avoid rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)

            return all_embeddings

        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise

    async def check_health(self) -> bool:
        """
        Check if the embedding service is healthy.
        """
        try:
            test_texts = ["Hello world"]
            embeddings = await self.generate_embeddings(test_texts)
            return len(embeddings) > 0 and len(embeddings[0]) == self.dimension
        except Exception:
            return False
