"""
Knowledge & RAG Agent
======================
Retrieves relevant medical guidelines and historical precedents for the current case.
Uses Qdrant vector database for semantic search.

Owner: Backend Dev
"""

from typing import Optional, List
from pydantic import BaseModel
from backend.services.llm_service import llm_service
from backend.services.prompt_manager import prompt_manager
from backend.core.logging import get_logger
from backend.infrastructure.qdrant.client import get_qdrant
from backend.services.embedding_service import embedding_service
import numpy as np

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class KnowledgeInput(BaseModel):
    """Input for RAG retrieval."""
    query: str
    symptoms: List[str] = []
    urgency: str = "routine"
    top_k: int = 3


class RetrievedDocument(BaseModel):
    """A single retrieved medical guideline or protocol."""
    id: str
    content: str
    source: str
    relevance_score: float


class KnowledgeOutput(BaseModel):
    """Retrieved knowledge and synthesized insights."""
    retrieved_documents: List[RetrievedDocument] = []
    synthesized_insight: Optional[str] = None
    confidence: float = 0.0
    status: str = "success"  # "success", "no_results", "error"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class KnowledgeAgent:
    """
    Knowledge & RAG Agent — retrieves relevant medical context.
    """

    def __init__(self, collections: List[str] = None):
        self.collections = collections or ["medical_guidelines", "hospital_protocols", "disaster_response", "government_schemes"]
        self.llm = llm_service
        self.qdrant = get_qdrant()

    async def process(self, input_data: KnowledgeInput) -> KnowledgeOutput:
        """
        Process the query and retrieve relevant guidelines.
        """
        if not self.qdrant:
            return KnowledgeOutput(
                status="error",
                synthesized_insight="Vector search is currently offline. Relying on baseline triage rules."
            )

        try:
            # 1. Generate embedding for the query (local model -- no API, no rate limit)
            query_text = f"{input_data.query}. Symptoms: {', '.join(input_data.symptoms)}. Urgency: {input_data.urgency}"
            query_vector = embedding_service.embed_query(query_text)

            # 2. Search Qdrant across multiple collections (over-fetch so MMR has
            # candidates to pick a diverse subset from, not just the top-K by raw score)
            fetch_k = max(input_data.top_k * 4, 10)
            all_hits = []
            for coll in self.collections:
                try:
                    search_result = self.qdrant.search(
                        collection_name=coll,
                        query_vector=query_vector,
                        limit=fetch_k,
                        with_vectors=True,  # needed for MMR diversity scoring
                    )
                    all_hits.extend(search_result)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Could not search collection {coll}: {e}")

            if not all_hits:
                return KnowledgeOutput(status="no_results", synthesized_insight="No specific guidelines found for this query.")

            # 3. MMR (Maximal Marginal Relevance) re-ranking -- picks results that
            # are relevant to the query AND diverse from each other, instead of
            # just the top-K most similar (which are often near-duplicates of
            # each other from the same source document).
            top_hits = self._mmr_select(
                query_vector=query_vector,
                hits=all_hits,
                k=input_data.top_k,
                lambda_mult=0.5,  # 0.5 = balanced relevance/diversity; 1.0 = pure relevance
            )

            docs = []
            for hit in top_hits:
                docs.append(RetrievedDocument(
                    id=str(hit.id),
                    content=hit.payload.get("content", ""),
                    source=hit.payload.get("source", "Unknown"),
                    relevance_score=hit.score
                ))

            # 3. Synthesize the findings
            docs_text = "\n\n".join([f"Source: {d.source}\n{d.content}" for d in docs])
            
            from backend.services.prompt_manager import prompt_manager
            synthesis_prompt = prompt_manager.get_knowledge_synthesis_prompt(query_text, docs_text)
            
            insight = await self.llm.generate_text(synthesis_prompt)

            return KnowledgeOutput(
                retrieved_documents=docs,
                synthesized_insight=insight,
                confidence=round(docs[0].relevance_score, 2),
                status="success"
            )

        except Exception as e:
            return KnowledgeOutput(
                status="error", 
                synthesized_insight=f"Error retrieving knowledge: {str(e)}"
            )

    @staticmethod
    def _mmr_select(query_vector: List[float], hits: list, k: int, lambda_mult: float = 0.5) -> list:
        """
        Maximal Marginal Relevance selection: iteratively picks the hit that
        maximizes (lambda * relevance_to_query - (1-lambda) * max_similarity_to_already_selected),
        so the final top-k avoid being near-duplicates of each other.
        """
        if len(hits) <= k:
            return sorted(hits, key=lambda h: h.score, reverse=True)

        query_vec = np.array(query_vector)
        doc_vecs = np.array([h.vector for h in hits])

        def cos_sim(a, b):
            denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
            return float(np.dot(a, b) / denom)

        sim_to_query = [cos_sim(doc_vecs[i], query_vec) for i in range(len(hits))]

        selected_idx: list = []
        candidates = list(range(len(hits)))

        while candidates and len(selected_idx) < k:
            if not selected_idx:
                best = max(candidates, key=lambda i: sim_to_query[i])
            else:
                def mmr_score(i):
                    diversity_penalty = max(cos_sim(doc_vecs[i], doc_vecs[j]) for j in selected_idx)
                    return lambda_mult * sim_to_query[i] - (1 - lambda_mult) * diversity_penalty
                best = max(candidates, key=mmr_score)

            selected_idx.append(best)
            candidates.remove(best)

        return [hits[i] for i in selected_idx]
