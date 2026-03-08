import weaviate
from weaviate.classes.init import Auth
from app.config import settings
from app.errors.exceptions import WeaviateConnectionError


_client: weaviate.WeaviateClient = None


async def get_weaviate_client() -> weaviate.WeaviateClient:
    """Returns a singleton Weaviate client."""
    global _client

    if _client is None:
        try:
            _client = weaviate.connect_to_local(
                host=settings.WEAVIATE_HOST,
                port=settings.WEAVIATE_PORT,
                grpc_port=50051,
                skip_init_checks=False,
            )
        except Exception as e:
            raise WeaviateConnectionError(
                message=f"Could not connect to Weaviate: {str(e)}"
            )

    return _client


async def close_weaviate():
    """Close Weaviate client on app shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None


async def search_collection(
    collection_name: str,
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Perform a BM25 keyword search on a Weaviate collection.
    Returns a list of matching objects with their properties.
    """
    try:
        client = await get_weaviate_client()
        collection = client.collections.get(collection_name)

        results = collection.query.bm25(
            query=query,
            limit=limit,
        )

        return [obj.properties for obj in results.objects]

    except Exception as e:
        raise WeaviateConnectionError(
            message=f"Weaviate search failed: {str(e)}"
        )


async def insert_document(
    collection_name: str,
    properties: dict,
) -> None:
    """
    Insert a single document into a Weaviate collection.
    Used by ingest.py to load safety docs.
    """
    try:
        client = await get_weaviate_client()
        collection = client.collections.get(collection_name)
        collection.data.insert(properties)

    except Exception as e:
        raise WeaviateConnectionError(
            message=f"Weaviate insert failed: {str(e)}"
        )


async def collection_exists(collection_name: str) -> bool:
    """Check if a collection already exists."""
    try:
        client = await get_weaviate_client()
        return client.collections.exists(collection_name)
    except Exception:
        return False
