import asyncio
from backend.infrastructure.qdrant.client import initialize_qdrant, get_qdrant, close_qdrant
from backend.services.ingestion_service import ingest_directory

COLLECTIONS = ["medical_guidelines", "hospital_protocols", "disaster_response", "government_schemes"]

async def main():
    initialize_qdrant()
    client = get_qdrant()
    for name in COLLECTIONS:
        try:
            client.delete_collection(name)
            print(f"Deleted old collection: {name}")
        except Exception as e:
            print(f"Skip {name}: {e}")

    # Re-ingest each collection's source folder
    for name in COLLECTIONS:
        folder = f"backend/data/{name}"
        count = await ingest_directory(folder, name)
        print(f"Re-ingested {count} chunks into {name}")

    close_qdrant()

if __name__ == "__main__":
    asyncio.run(main())
