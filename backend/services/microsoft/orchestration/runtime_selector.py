import os
import logging
from services.microsoft.orchestration.local_runtime import LocalRuntime

logger = logging.getLogger("data_detective.runtime_selector")

_active_runtime = None

def get_active_runtime():
    """
    Dynamically select the active runtime. If Azure credentials exist,
    load AzureRuntime. Otherwise, fall back to LocalRuntime.
    """
    global _active_runtime
    if _active_runtime is not None:
        return _active_runtime

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    if api_key and endpoint and deployment:
        try:
            from services.microsoft.orchestration.azure_runtime import AzureRuntime
            _active_runtime = AzureRuntime()
            logger.info("Selected AzureRuntime as the active orchestration backend.")
            return _active_runtime
        except Exception as e:
            logger.warning(f"Could not load AzureRuntime: {e}. Falling back to LocalRuntime.")

    _active_runtime = LocalRuntime()
    logger.info("Selected LocalRuntime as the active orchestration backend.")
    return _active_runtime

def reset_runtime():
    """
    Resets the cached active runtime. (Useful for testing)
    """
    global _active_runtime
    _active_runtime = None
