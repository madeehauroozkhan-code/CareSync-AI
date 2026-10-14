import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.infrastructure.qdrant.client import get_qdrant
from backend.services.ingestion_service import ingest_pdf
from backend.agents.knowledge.agent import KnowledgeInput, KnowledgeAgent
from qdrant_client.models import Filter

async def main():
    qdrant = get_qdrant()
    if not qdrant:
        print("Could not connect to Qdrant.")
        return

    data_dir = Path(__file__).resolve().parent.parent / "data"
    collections = ["medical_guidelines", "hospital_protocols", "government_schemes", "disaster_response"]

    total_pdfs_processed = 0
    total_chunks_created = 0
    total_vectors_stored = 0

    print("\n--- Starting Smart Ingestion ---")
    for collection in collections:
        print(f"\nProcessing collection: {collection}")
        
        # Check if collection exists
        existing_collections = [c.name for c in qdrant.get_collections().collections]
        existing_sources = set()
        
        if collection in existing_collections:
            # Get existing sources (paginated scroll)
            offset = None
            while True:
                records, offset = qdrant.scroll(
                    collection_name=collection,
                    limit=100,
                    with_payload=True,
                    with_vectors=False,
                    offset=offset
                )
                for record in records:
                    if record.payload and "source" in record.payload:
                        existing_sources.add(record.payload["source"])
                if offset is None:
                    break
            if "cfar-pocketguide.pdf" in existing_sources:
                existing_sources.remove("cfar-pocketguide.pdf")
            print(f"  Found {len(existing_sources)} existing documents in Qdrant for {collection}.")
        else:
            print(f"  Collection {collection} does not exist yet (will be created).")

        # Process directory
        coll_dir = data_dir / collection
        if not coll_dir.exists():
            print(f"  Directory {coll_dir} does not exist, skipping.")
            continue
            
        for file_path in coll_dir.rglob("*.pdf"):
            filename = file_path.name
            if filename in existing_sources:
                print(f"  Skipping existing: {filename}")
                continue
                
            print(f"  Ingesting NEW document: {filename}")
            chunks = await ingest_pdf(str(file_path), collection)
            if chunks > 0:
                print(f"    -> Successfully ingested {chunks} chunks.")
                total_pdfs_processed += 1
                total_chunks_created += chunks
                total_vectors_stored += chunks
            else:
                print(f"    -> Failed or 0 chunks ingested.")

    print("\n==================================================")
    print("INGESTION SUMMARY")
    print("==================================================")
    print(f"Total PDFs processed: {total_pdfs_processed}")
    print(f"Total chunks created: {total_chunks_created}")
    print(f"Total vectors stored: {total_vectors_stored}")
    print("\nQdrant Collection Status:")
    
    existing_collections = [c.name for c in qdrant.get_collections().collections]
    for collection in collections:
        if collection in existing_collections:
            info = qdrant.get_collection(collection)
            print(f"- {collection}: {info.points_count} points")
        else:
            print(f"- {collection}: Not Found (0 points)")

    print("\n==================================================")
    print("RETRIEVAL TESTS")
    print("==================================================")
    
    # Initialize the Knowledge Agent
    agent = KnowledgeAgent(collections=collections)
    
    test_queries = [
        "What are the symptoms of dengue?",
        "How is malaria treated?",
        "How to perform CPR?",
        "What is the management of an acute stroke?",
        "First aid for snakebite",
        "What is PM-JAY?",
        "What to do during a flood?",
        "What to do in case of fire?",
        "Triage protocol in emergencies"
    ]
    
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        input_data = KnowledgeInput(query=q, urgency="routine", top_k=1)
        result = await agent.process(input_data)
        
        if result.status == "success" and result.retrieved_documents:
            doc = result.retrieved_documents[0]
            print(f"  Retrieved Document: {doc.source}")
            print(f"  Similarity Score:   {doc.relevance_score:.4f}")
            print(f"  Status:             {result.status}")
        else:
            print(f"  Status:             {result.status}")
            print(f"  Message:            {result.synthesized_insight}")

if __name__ == "__main__":
    asyncio.run(main())
