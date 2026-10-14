"""
ingestion_service.py
--------------------
Service for chunking, embedding, and ingesting documents into Qdrant.
This is meant to be called by an admin endpoint or CLI, not during standard app startup.
"""

import os
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.services.embedding_service import embedding_service
from backend.infrastructure.qdrant.client import get_qdrant
from backend.core.logging import get_logger
from qdrant_client.models import PointStruct, VectorParams, Distance

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

logger = get_logger(__name__)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Basic text chunking."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


async def _ingest_points(points: List[PointStruct], collection_name: str, source: str) -> int:
    qdrant = get_qdrant()
    if not qdrant or not points:
        return 0
        
    try:
        collections = qdrant.get_collections().collections
        if not any(c.name == collection_name for c in collections):
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
            
        qdrant.upsert(
            collection_name=collection_name,
            points=points
        )
        logger.info(f"Ingested {len(points)} chunks from {source}")
        return len(points)
    except Exception as e:
        logger.error(f"Error upserting to Qdrant: {e}")
        return 0


async def ingest_document_text(content: str, metadata: Dict[str, Any], collection_name: str) -> int:
    """Ingest raw text content with provided metadata."""
    chunks = chunk_text(content)
    if not chunks:
        return 0

    points = []
    batch_size = 32  # local embeddings are fast, no need for tiny batches or sleeps
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        try:
            vectors = embedding_service.embed_documents(batch)

            for j, vector in enumerate(vectors):
                chunk_idx = i + j
                point_id = str(uuid.uuid4())
                chunk_meta = metadata.copy()
                chunk_meta["content"] = batch[j]
                chunk_meta["chunk_index"] = chunk_idx

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=chunk_meta
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to embed batch: {e}")

    return await _ingest_points(points, collection_name, metadata.get("source", "unknown"))


async def ingest_pdf(file_path: str, collection_name: str) -> int:
    """Ingest a PDF file using pypdf."""
    if not PdfReader:
        logger.error("pypdf not installed. Cannot process PDF.")
        return 0
        
    path = Path(file_path)
    stat = path.stat()
    
    all_chunks = []
    metadata_list = []
    
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                metadata = {
                    "source": path.name,
                    "collection": collection_name,
                    "page": i + 1,
                    "timestamp": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "file_type": "pdf"
                }
                
                # Chunk text here
                chunks = chunk_text(text)
                for chunk in chunks:
                    all_chunks.append(chunk)
                    metadata_list.append(metadata)
                    
        # Now batch process all chunks at once
        if not all_chunks:
            return 0

        points = []
        batch_size = 32  # local embeddings -- no rate limit, bigger batches are fine
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            batch_meta = metadata_list[i:i+batch_size]
            try:
                vectors = embedding_service.embed_documents(batch)

                for j, vector in enumerate(vectors):
                    chunk_idx = i + j
                    point_id = str(uuid.uuid4())
                    chunk_meta = batch_meta[j].copy()
                    chunk_meta["content"] = batch[j]
                    chunk_meta["chunk_index"] = chunk_idx

                    points.append(
                        PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=chunk_meta
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to embed batch: {e}")

        return await _ingest_points(points, collection_name, path.name)
        
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return 0


async def ingest_file(file_path: str, collection_name: str) -> int:
    """Detect file type and ingest appropriately."""
    path = Path(file_path)
    if not path.is_file():
        return 0
        
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        return await ingest_pdf(file_path, collection_name)
    elif ext in (".txt", ".md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            stat = path.stat()
            metadata = {
                "source": path.name,
                "collection": collection_name,
                "timestamp": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_type": ext[1:]
            }
            return await ingest_document_text(content, metadata, collection_name)
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return 0
            
    logger.info(f"Skipping unsupported file: {file_path}")
    return 0


async def ingest_directory(dir_path: str, collection_name: Optional[str] = None) -> int:
    """
    Recursively ingest all supported files in a directory.
    If collection_name is not provided, it uses the direct parent folder name.
    """
    total = 0
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        logger.error(f"Directory not found: {dir_path}")
        return 0
        
    for file_path in path.rglob("*"):
        if file_path.is_file():
            # Skip READMEs and hidden files
            if file_path.name.lower() == "readme.md" or file_path.name.startswith("."):
                continue
                
            coll = collection_name or file_path.parent.name
            logger.info(f"Ingesting {file_path.name} into collection {coll}...")
            total += await ingest_file(str(file_path), coll)
            
    return total


async def ingest_document(content: str, source: str, collection_name: str = "medical_guidelines") -> int:
    """Legacy wrapper for raw string ingest."""
    metadata = {
        "source": source,
        "collection": collection_name,
        "timestamp": datetime.datetime.now().isoformat()
    }
    return await ingest_document_text(content, metadata, collection_name)
