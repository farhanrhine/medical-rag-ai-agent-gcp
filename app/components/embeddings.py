from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.config.config import EMBEDDING_MODEL, HF_TOKEN

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def get_embedding_model():
    try:
        logger.info(f"Initializing HuggingFace Endpoint Embeddings with model: {EMBEDDING_MODEL}")

        model = HuggingFaceEndpointEmbeddings(
            model=EMBEDDING_MODEL,
            huggingfacehub_api_token=HF_TOKEN
        )

        logger.info("HuggingFace endpoint embedding model loaded successfully.")

        return model
    
    except Exception as e:
        error_message = CustomException("Error occurred while loading embedding model", e)
        logger.error(str(error_message))
        raise error_message