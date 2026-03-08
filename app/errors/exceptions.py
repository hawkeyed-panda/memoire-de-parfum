from fastapi import HTTPException, status


# --- Base ---
class MemoireBaseException(Exception):
    """Base exception for all Mémoire de Parfum errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


# --- Pipeline exceptions ---
class SignalExtractionError(MemoireBaseException):
    def __init__(self, message: str = "Failed to extract scent signals from questionnaire"):
        super().__init__(message, code="SIGNAL_EXTRACTION_FAILED")

class GraphRAGError(MemoireBaseException):
    def __init__(self, message: str = "Failed to retrieve candidates from knowledge graph"):
        super().__init__(message, code="GRAPH_RAG_FAILED")

class ConstraintSelectorError(MemoireBaseException):
    def __init__(self, message: str = "Failed to select fragrance blueprint"):
        super().__init__(message, code="CONSTRAINT_SELECTOR_FAILED")

class DocRAGError(MemoireBaseException):
    def __init__(self, message: str = "Failed to retrieve grounding documents"):
        super().__init__(message, code="DOC_RAG_FAILED")

class LLMSynthesisError(MemoireBaseException):
    def __init__(self, message: str = "Failed to synthesize fragrance output"):
        super().__init__(message, code="LLM_SYNTHESIS_FAILED")


# --- Guardrail exceptions ---
class SafetyRuleViolation(MemoireBaseException):
    def __init__(self, message: str = "Fragrance blueprint violates safety rules"):
        super().__init__(message, code="SAFETY_VIOLATION")

class GroundingRuleViolation(MemoireBaseException):
    def __init__(self, message: str = "Output is not grounded in retrieved facts"):
        super().__init__(message, code="GROUNDING_VIOLATION")

class PolicyRuleViolation(MemoireBaseException):
    def __init__(self, message: str = "Output contains disallowed medical or therapeutic claims"):
        super().__init__(message, code="POLICY_VIOLATION")

class SchemaValidationError(MemoireBaseException):
    def __init__(self, message: str = "Output missing required fields"):
        super().__init__(message, code="SCHEMA_VALIDATION_FAILED")


# --- Infrastructure exceptions ---
class Neo4jConnectionError(MemoireBaseException):
    def __init__(self, message: str = "Failed to connect to Neo4j"):
        super().__init__(message, code="NEO4J_CONNECTION_FAILED")

class WeaviateConnectionError(MemoireBaseException):
    def __init__(self, message: str = "Failed to connect to Weaviate"):
        super().__init__(message, code="WEAVIATE_CONNECTION_FAILED")

class RedisConnectionError(MemoireBaseException):
    def __init__(self, message: str = "Failed to connect to Redis"):
        super().__init__(message, code="REDIS_CONNECTION_FAILED")


# --- Auth exceptions ---
class InvalidTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

class RateLimitExceededError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before retrying."
        )


# --- Fallback responses ---
FALLBACK_RESPONSES = {
    "SIGNAL_EXTRACTION_FAILED": "We couldn't process your memory right now. Please try again.",
    "GRAPH_RAG_FAILED": "Our fragrance knowledge base is temporarily unavailable.",
    "CONSTRAINT_SELECTOR_FAILED": "We couldn't build your fragrance blueprint. Please try again.",
    "LLM_SYNTHESIS_FAILED": "We couldn't generate your fragrance description. Please try again.",
    "SAFETY_VIOLATION": "This combination doesn't meet our safety standards. Adjusting your blend.",
    "POLICY_VIOLATION": "We can only describe fragrances experientially, not medically.",
}


def get_fallback_message(code: str) -> str:
    return FALLBACK_RESPONSES.get(code, "Something went wrong. Please try again.")
