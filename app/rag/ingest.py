import weaviate
import weaviate.classes as wvc
from app.rag.weaviate_client import get_weaviate_client, collection_exists
from app.errors.exceptions import WeaviateConnectionError


COLLECTION_NAME = "FragranceKnowledge"

# --- Curated fragrance knowledge base ---
# In production: load these from data/safety_docs/ PDFs
FRAGRANCE_DOCUMENTS = [
    # Top notes
    {
        "note": "bergamot",
        "layer": "top",
        "family": "citrus",
        "content": "Bergamot is a citrus top note that evokes fresh, sunlit brightness. It opens a fragrance with an uplifting, luminous quality and typically lasts 15-30 minutes.",
        "safety": "Generally safe. Avoid high concentrations in leave-on products due to photosensitivity risk.",
    },
    {
        "note": "neroli",
        "layer": "top",
        "family": "citrus",
        "content": "Neroli is a delicate citrus floral top note distilled from bitter orange blossoms. It evokes a fresh, luminous, and slightly honeyed quality.",
        "safety": "Safe for all skin types. One of the most skin-friendly citrus notes.",
    },
    {
        "note": "pink pepper",
        "layer": "top",
        "family": "spicy",
        "content": "Pink pepper adds a sparkling, slightly spicy brightness to the opening of a fragrance. It evokes excitement and energy without being overpowering.",
        "safety": "Use at moderate concentrations. Safe substitute for cinnamon bark.",
    },
    # Heart notes
    {
        "note": "rose",
        "layer": "heart",
        "family": "floral",
        "content": "Rose absolute is the quintessential floral heart note. Rich, warm, and deeply romantic, it evokes tenderness, love, and timeless elegance. Lasts 2-4 hours.",
        "safety": "Rose absolute is safe for all skin types. Rose otto (steam distilled) is preferred for sensitive skin.",
    },
    {
        "note": "jasmine",
        "layer": "heart",
        "family": "floral",
        "content": "Jasmine is an intensely floral, slightly sweet heart note. It evokes sensuality, warmth, and confidence. Pairs beautifully with citrus top notes and woody bases.",
        "safety": "Safe at standard concentrations. Avoid in very high doses for sensitive skin.",
    },
    {
        "note": "geranium",
        "layer": "heart",
        "family": "floral",
        "content": "Geranium is a green, rosy heart note with a fresh and slightly minty character. It bridges floral and green accords and evokes balance and calm.",
        "safety": "Generally safe. Good alternative to rose for sensitive formulations.",
    },
    {
        "note": "lavender",
        "layer": "heart",
        "family": "aromatic",
        "content": "Lavender is a classic aromatic heart note that evokes calm, peace, and clarity. It adds a clean, soothing quality and pairs well with woody and citrus notes.",
        "safety": "One of the safest fragrance ingredients. Suitable for all skin types.",
    },
    # Base notes
    {
        "note": "sandalwood",
        "layer": "base",
        "family": "woody",
        "content": "Sandalwood is a creamy, warm woody base note with exceptional longevity. It evokes depth, comfort, and grounded elegance. Lasts 6-8 hours on skin.",
        "safety": "Safe for all skin types. Australian sandalwood is a sustainable alternative to Indian sandalwood.",
    },
    {
        "note": "vetiver",
        "layer": "base",
        "family": "woody",
        "content": "Vetiver is an earthy, smoky, deeply grounded base note. It evokes strength, sophistication, and connection to the earth. Long-lasting and distinctive.",
        "safety": "Safe for all skin types. No known sensitization issues.",
    },
    {
        "note": "vanilla",
        "layer": "base",
        "family": "oriental",
        "content": "Vanilla is a warm, sweet, comforting base note. It evokes softness, intimacy, and warmth. It rounds off sharp notes and adds approachable depth.",
        "safety": "Safe for all skin types. Natural vanilla extract preferred over synthetic vanillin for sensitive skin.",
    },
    {
        "note": "patchouli",
        "layer": "base",
        "family": "oriental",
        "content": "Patchouli is a rich, earthy, oriental base note. It evokes depth, mystery, and sensuality. Aged patchouli is smoother and more refined.",
        "safety": "Safe at standard concentrations. Use lower concentrations for sensitive skin.",
    },
    {
        "note": "cedarwood",
        "layer": "base",
        "family": "woody",
        "content": "Cedarwood is a clean, dry, woody base note. It evokes stability, confidence, and quiet strength. Pairs well with floral and citrus notes.",
        "safety": "Safe for all skin types. Virginia cedarwood and Atlas cedarwood are both safe options.",
    },
    {
        "note": "amber",
        "layer": "base",
        "family": "oriental",
        "content": "Amber accord is a warm, resinous base that evokes luxury, warmth, and timeless comfort. It is typically a blend rather than a single ingredient.",
        "safety": "Safe. Modern amber accords avoid problematic labdanum derivatives.",
    },
]


async def setup_collection() -> None:
    """
    Creates the FragranceKnowledge collection in Weaviate if it doesn't exist.
    """
    client = await get_weaviate_client()

    if await collection_exists(COLLECTION_NAME):
        print(f"[Ingest] Collection '{COLLECTION_NAME}' already exists — skipping creation.")
        return

    try:
        client.collections.create(
            name=COLLECTION_NAME,
            properties=[
                wvc.config.Property(name="note", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="layer", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="family", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="safety", data_type=wvc.config.DataType.TEXT),
            ],
        )
        print(f"[Ingest] Collection '{COLLECTION_NAME}' created.")
    except Exception as e:
        raise WeaviateConnectionError(
            message=f"Failed to create Weaviate collection: {str(e)}"
        )


async def ingest_documents() -> None:
    """
    Ingests all fragrance knowledge documents into Weaviate.
    Safe to run multiple times — checks existence first.
    """
    await setup_collection()

    client = await get_weaviate_client()
    collection = client.collections.get(COLLECTION_NAME)

    # Check if already ingested
    count = collection.aggregate.over_all(total_count=True).total_count
    if count and count >= len(FRAGRANCE_DOCUMENTS):
        print(f"[Ingest] {count} documents already ingested — skipping.")
        return

    try:
        with collection.batch.dynamic() as batch:
            for doc in FRAGRANCE_DOCUMENTS:
                batch.add_object(properties=doc)

        print(f"[Ingest] Successfully ingested {len(FRAGRANCE_DOCUMENTS)} documents.")

    except Exception as e:
        raise WeaviateConnectionError(
            message=f"Document ingestion failed: {str(e)}"
        )
