from langsmith import traceable
from app.models.blueprint import FragranceBlueprintJSON
from app.rag.weaviate_client import search_collection
from app.errors.exceptions import DocRAGError


COLLECTION_NAME = "FragranceKnowledge"


@traceable(name="doc_rag")
async def retrieve_references(
    blueprint: FragranceBlueprintJSON,
) -> list[str]:
    """
    Retrieves grounding references from Weaviate for selected notes.
    Queries each selected note and returns relevant content snippets.
    Used by llm_synthesis to ground the final fragrance story.
    """
    try:
        all_notes = (
            blueprint.top_notes +
            blueprint.heart_notes +
            blueprint.base_notes
        )

        references = []
        seen_notes = set()

        for note in all_notes:
            if note.name.lower() in seen_notes:
                continue
            seen_notes.add(note.name.lower())

            # Search Weaviate for this note
            results = await search_collection(
                collection_name=COLLECTION_NAME,
                query=note.name,
                limit=2,
            )

            for result in results:
                content = result.get("content", "")
                safety = result.get("safety", "")

                if content:
                    references.append(content)
                if safety:
                    references.append(f"Safety note for {note.name}: {safety}")

        # Fallback if nothing retrieved
        if not references:
            references = [
                f"{note.name} is a {note.family} note that {note.description}"
                for note in all_notes
            ]

        return references

    except Exception as e:
        raise DocRAGError(
            message=f"Document retrieval failed: {str(e)}"
        )

