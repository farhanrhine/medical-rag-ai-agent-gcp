from typing import Any, Dict, List

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from app.components.vector_store import load_vector_store
from app.common.logger import get_logger
from app.common.custom_exception import CustomException


logger = get_logger(__name__)


SYSTEM_PROMPT = """You are a helpful and concise medical question-answering assistant.

You have access to one tool:

- medical_retriever: use this to look up relevant medical context from the user's documents.

Guidelines:
- Always call the medical_retriever tool before answering a medical question.
- Use only the information returned by the tool as your source of truth.
- If the tool does not return enough information, say you do not know instead of guessing.
- Answer the user's medical question in at most 2–3 sentences.
- Use clear, simple language appropriate for patients, not doctors.
"""


@tool
def medical_retriever(question: str) -> str:
    """Retrieve relevant medical context from the vector store for a given question."""
    db = load_vector_store()
    if db is None:
        logger.warning("medical_retriever called but no vector store is available")
        return "No medical documents are available to answer this question."

    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)

    if not docs:
        return "No relevant context was found for this question."

    return "\n\n".join(doc.page_content for doc in docs)


def _build_agent():
    try:
        model = init_chat_model(
            "claude-sonnet-4-5-20250929",
            temperature=0,
        )
    except Exception as e:
        error = CustomException("Failed to initialize chat model for agent", e)
        logger.error(str(error))
        raise

    return create_agent(
        model=model,
        tools=[medical_retriever],
        system_prompt=SYSTEM_PROMPT,
    )


_agent = _build_agent()


def get_agent_response(user_message: str) -> str:
    """Invoke the LangChain agent and return the final assistant message as plain text."""
    try:
        result: Dict[str, Any] = _agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )
    except Exception as e:
        error = CustomException("Agent invocation failed", e)
        logger.error(str(error))
        raise

    messages: List[Dict[str, Any]] = result.get("messages", [])
    if not messages:
        logger.warning("Agent returned no messages")
        return "Sorry, I could not generate a response."

    last_message = messages[-1]
    content = last_message.get("content", "")

    # Content may be a simple string or a list of content blocks.
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # Join any text parts; ignore non-text blocks for now.
        text_parts = [
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        ]
        joined = "\n".join(p for p in text_parts if p)
        if joined:
            return joined

    logger.warning("Agent response content was in an unexpected format")
    return "Sorry, I could not understand the response from the model."

