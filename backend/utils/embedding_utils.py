import logging
import numpy as np
from typing import Optional
from config import settings

logger = logging.getLogger("hiresmart.embeddings")

_model = None


def get_embedding_model():
    """Lazy load SentenceTransformer model singleton."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading Sentence Transformer model: {settings.EMBEDDING_MODEL_NAME}")
            _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        except Exception as exc:
            logger.warning(f"Failed to load sentence_transformers: {exc}. Falling back to TF-IDF cosine similarity.")
            _model = False
    return _model


def compute_vector_embedding(text: str) -> Optional[np.ndarray]:
    """Compute dense vector embedding for input text."""
    model = get_embedding_model()
    if model:
        try:
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as exc:
            logger.error(f"Error computing vector embedding: {exc}")
    return None


def compute_similarity_score(text1: str, text2: str) -> float:
    """Compute cosine similarity score (0.0 to 100.0) between two text strings."""
    if not text1.strip() or not text2.strip():
        return 0.0

    model = get_embedding_model()
    if model:
        try:
            emb1 = model.encode(text1, convert_to_numpy=True)
            emb2 = model.encode(text2, convert_to_numpy=True)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            cosine_sim = np.dot(emb1, emb2) / (norm1 * norm2)
            # Bound between 0 and 100
            score = float(np.clip(cosine_sim * 100.0, 0.0, 100.0))
            return score
        except Exception as exc:
            logger.error(f"SentenceTransformer similarity error: {exc}")

    # Fallback: Count Vectorizer / Jaccard / Keyword similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    if not union:
        return 0.0
    jaccard_score = (len(intersection) / len(union)) * 100.0
    return round(jaccard_score, 2)
