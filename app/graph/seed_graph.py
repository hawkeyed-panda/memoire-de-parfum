"""
Auto-seeds the Neo4j knowledge graph at startup if empty.
Mirrors the data in graph_schema.cypher but runs programmatically.
"""
from app.graph.neo4j_client import run_query


SEED_STATEMENTS = [
    "MERGE (:ScentFamily {name: 'floral'})",
    "MERGE (:ScentFamily {name: 'woody'})",
    "MERGE (:ScentFamily {name: 'citrus'})",
    "MERGE (:ScentFamily {name: 'oriental'})",
    "MERGE (:ScentFamily {name: 'spicy'})",
    "MERGE (:ScentFamily {name: 'aromatic'})",

    "MERGE (:Note {name: 'rose', layer: 'heart', family: 'floral'})",
    "MERGE (:Note {name: 'bergamot', layer: 'top', family: 'citrus'})",
    "MERGE (:Note {name: 'sandalwood', layer: 'base', family: 'woody'})",
    "MERGE (:Note {name: 'vetiver', layer: 'base', family: 'woody'})",
    "MERGE (:Note {name: 'vanilla', layer: 'base', family: 'oriental'})",
    "MERGE (:Note {name: 'jasmine', layer: 'heart', family: 'floral'})",
    "MERGE (:Note {name: 'neroli', layer: 'top', family: 'citrus'})",
    "MERGE (:Note {name: 'geranium', layer: 'heart', family: 'floral'})",
    "MERGE (:Note {name: 'patchouli', layer: 'base', family: 'oriental'})",
    "MERGE (:Note {name: 'cedarwood', layer: 'base', family: 'woody'})",
    "MERGE (:Note {name: 'lavender', layer: 'heart', family: 'aromatic'})",
    "MERGE (:Note {name: 'amber', layer: 'base', family: 'oriental'})",
    "MERGE (:Note {name: 'pink pepper', layer: 'top', family: 'spicy'})",
    "MERGE (:Note {name: 'black pepper', layer: 'top', family: 'spicy'})",

    "MERGE (:Emotion {name: 'nostalgia'})",
    "MERGE (:Emotion {name: 'love'})",
    "MERGE (:Emotion {name: 'peace'})",
    "MERGE (:Emotion {name: 'joy'})",
    "MERGE (:Emotion {name: 'comfort'})",
    "MERGE (:Emotion {name: 'excitement'})",
    "MERGE (:Emotion {name: 'confident'})",
    "MERGE (:Emotion {name: 'calm'})",
    "MERGE (:Emotion {name: 'energized'})",
    "MERGE (:Emotion {name: 'elegant'})",
    "MERGE (:Emotion {name: 'powerful'})",
    "MERGE (:Emotion {name: 'radiant'})",
    "MERGE (:Emotion {name: 'empowered'})",
    "MERGE (:Emotion {name: 'grounded'})",

    "MATCH (e:Emotion {name: 'nostalgia'}), (n:Note {name: 'rose'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'nostalgia'}), (n:Note {name: 'vanilla'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'nostalgia'}), (n:Note {name: 'sandalwood'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'love'}), (n:Note {name: 'rose'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'love'}), (n:Note {name: 'jasmine'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'love'}), (n:Note {name: 'vanilla'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'peace'}), (n:Note {name: 'lavender'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'peace'}), (n:Note {name: 'sandalwood'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'peace'}), (n:Note {name: 'neroli'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'joy'}), (n:Note {name: 'bergamot'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'joy'}), (n:Note {name: 'neroli'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'joy'}), (n:Note {name: 'rose'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'comfort'}), (n:Note {name: 'vanilla'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'comfort'}), (n:Note {name: 'sandalwood'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'comfort'}), (n:Note {name: 'amber'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'excitement'}), (n:Note {name: 'pink pepper'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'excitement'}), (n:Note {name: 'bergamot'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'confident'}), (n:Note {name: 'cedarwood'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'confident'}), (n:Note {name: 'vetiver'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'calm'}), (n:Note {name: 'lavender'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'calm'}), (n:Note {name: 'sandalwood'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'energized'}), (n:Note {name: 'bergamot'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'energized'}), (n:Note {name: 'pink pepper'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'elegant'}), (n:Note {name: 'rose'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'elegant'}), (n:Note {name: 'jasmine'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'powerful'}), (n:Note {name: 'vetiver'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'powerful'}), (n:Note {name: 'patchouli'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'radiant'}), (n:Note {name: 'neroli'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'radiant'}), (n:Note {name: 'bergamot'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'empowered'}), (n:Note {name: 'cedarwood'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'empowered'}), (n:Note {name: 'black pepper'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'grounded'}), (n:Note {name: 'vetiver'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'grounded'}), (n:Note {name: 'patchouli'}) MERGE (e)-[:EVOKES]->(n)",
    "MATCH (e:Emotion {name: 'grounded'}), (n:Note {name: 'cedarwood'}) MERGE (e)-[:EVOKES]->(n)",

    "MATCH (a:Note {name: 'rose'}), (b:Note {name: 'sandalwood'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'rose'}), (b:Note {name: 'bergamot'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'bergamot'}), (b:Note {name: 'vetiver'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'bergamot'}), (b:Note {name: 'jasmine'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'sandalwood'}), (b:Note {name: 'vanilla'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'jasmine'}), (b:Note {name: 'cedarwood'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'patchouli'}), (b:Note {name: 'vanilla'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'neroli'}), (b:Note {name: 'sandalwood'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'lavender'}), (b:Note {name: 'cedarwood'}) MERGE (a)-[:PAIRS_WITH]->(b)",
    "MATCH (a:Note {name: 'vetiver'}), (b:Note {name: 'sandalwood'}) MERGE (a)-[:PAIRS_WITH]->(b)",

    "MERGE (:SafetyFlag {name: 'oakmoss', reason: 'known sensitizer', severity: 'high'})",
    "MERGE (:SafetyFlag {name: 'peru balsam', reason: 'known sensitizer', severity: 'high'})",
    "MERGE (:SafetyFlag {name: 'cinnamon bark', reason: 'skin irritant', severity: 'medium'})",
    "MERGE (:SafetyFlag {name: 'clove', reason: 'skin irritant', severity: 'medium'})",
    "MERGE (:SafetyFlag {name: 'lemongrass', reason: 'sensitizer for gentle skin', severity: 'low'})",
    "MERGE (:SafetyFlag {name: 'ylang ylang', reason: 'sensitizer for gentle skin', severity: 'low'})",
]


async def seed_graph_if_empty() -> None:
    """Seeds the Neo4j knowledge graph if no Emotion nodes exist."""
    try:
        result = await run_query("MATCH (e:Emotion) RETURN count(e) AS cnt")
        if result and result[0]["cnt"] > 0:
            print("[Neo4j] Knowledge graph already seeded — skipping.")
            return

        print("[Neo4j] Knowledge graph is empty — seeding...")
        for stmt in SEED_STATEMENTS:
            await run_query(stmt)

        result = await run_query("MATCH (e:Emotion) RETURN count(e) AS cnt")
        count = result[0]["cnt"] if result else 0
        print(f"[Neo4j] Seeded {count} emotions + notes + relationships.")

    except Exception as e:
        print(f"[WARNING] Neo4j seeding failed: {e}. Graph queries will use fallbacks.")
