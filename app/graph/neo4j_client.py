from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import settings
from app.errors.exceptions import Neo4jConnectionError


_driver: AsyncDriver = None


async def get_neo4j_driver() -> AsyncDriver:
    """Returns a singleton Neo4j async driver."""
    global _driver

    if _driver is None:
        try:
            _driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
            await _driver.verify_connectivity()
        except Exception as e:
            raise Neo4jConnectionError(
                message=f"Could not connect to Neo4j: {str(e)}"
            )

    return _driver


async def close_neo4j():
    """Close Neo4j driver on app shutdown."""
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


async def run_query(query: str, parameters: dict = None) -> list[dict]:
    """
    Execute a Cypher query and return results as a list of dicts.
    Used by graph_rag.py for all knowledge graph queries.
    """
    driver = await get_neo4j_driver()

    try:
        async with driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records
    except Exception as e:
        raise Neo4jConnectionError(
            message=f"Neo4j query failed: {str(e)}"
        )


async def run_write_query(query: str, parameters: dict = None) -> None:
    """
    Execute a write Cypher query (CREATE, MERGE, SET).
    Used for seeding the knowledge graph.
    """
    driver = await get_neo4j_driver()

    try:
        async with driver.session() as session:
            await session.execute_write(
                lambda tx: tx.run(query, parameters or {})
            )
    except Exception as e:
        raise Neo4jConnectionError(
            message=f"Neo4j write query failed: {str(e)}"
        )
