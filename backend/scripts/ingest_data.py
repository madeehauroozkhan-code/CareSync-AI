"""
ingest_data.py
--------------
CLI script to ingest documents (PDF/Markdown/Text) or entire directories into the Qdrant vector database.

Usage:
    python -m backend.scripts.ingest_data <path_to_file_or_dir> [collection_name]
"""

import sys
import asyncio
from pathlib import Path

# Need to configure logging and environment before importing services
from backend.core.config import settings
from backend.core.logging import configure_logging, get_logger
from backend.infrastructure.qdrant.client import initialize_qdrant, close_qdrant
from backend.services.ingestion_service import ingest_file, ingest_directory

logger = get_logger(__name__)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend.scripts.ingest_data <path_to_file_or_dir> [collection_name]")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    collection_name = sys.argv[2] if len(sys.argv) > 2 else None

    if not target_path.exists():
        print(f"Error: Path not found -> {target_path}")
        sys.exit(1)

    configure_logging()
    
    # Initialize infrastructure needed for ingestion
    initialize_qdrant()

    logger.info(f"Starting ingestion of {target_path}")

    try:
        if target_path.is_dir():
            chunks = await ingest_directory(str(target_path), collection_name)
        else:
            coll = collection_name or target_path.parent.name
            chunks = await ingest_file(str(target_path), coll)
            
        logger.info(f"Successfully ingested {chunks} chunks.")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
    finally:
        close_qdrant()


if __name__ == "__main__":
    asyncio.run(main())
