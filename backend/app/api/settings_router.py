import os
from fastapi import APIRouter
from app.config import settings, update_gemini_key
from app.schemas.analysis_schema import SettingsResponse, SettingsUpdateRequest
from app.services.gemini_service import test_gemini_connection, get_active_gemini_key
from app.services.local_llm_service import test_local_llm_connection, is_local_llm_available

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=SettingsResponse)
def get_settings_status():
    key = get_active_gemini_key()
    local_reachable = is_local_llm_available()

    if key:
        active_engine = "GEMINI_HYBRID"
    elif local_reachable:
        active_engine = f"LOCAL_LLM ({settings.local_llm_model})"
    else:
        active_engine = "CONTEXTUAL_SEMANTIC_ENGINE (Local NLP)"

    return SettingsResponse(
        app_name=settings.app_name,
        version=settings.version,
        gemini_api_key_configured=bool(key),
        gemini_model=settings.gemini_model,
        active_engine=active_engine,
        backup_keys_configured=bool(settings.gemini_backup_keys),
        custom_endpoint_configured=bool(settings.custom_llm_endpoint),
        custom_llm_api_key_configured=bool(settings.custom_llm_api_key or os.getenv("CUSTOM_LLM_API_KEY", "") or os.getenv("NVIDIA_API_KEY", "")),
        local_llm_enabled=settings.local_llm_enabled,
        local_llm_endpoint=settings.local_llm_endpoint if settings.local_llm_enabled else "",
        local_llm_model=settings.local_llm_model,
        local_llm_reachable=local_reachable
    )

@router.post("", response_model=SettingsResponse)
def update_settings(payload: SettingsUpdateRequest):
    if payload.gemini_api_key is not None and payload.gemini_api_key.strip():
        update_gemini_key(payload.gemini_api_key)
    if payload.gemini_backup_keys is not None and payload.gemini_backup_keys.strip():
        settings.gemini_backup_keys = payload.gemini_backup_keys.strip()
    if payload.gemini_model:
        settings.gemini_model = payload.gemini_model
    if payload.custom_llm_endpoint is not None and payload.custom_llm_endpoint.strip():
        settings.custom_llm_endpoint = payload.custom_llm_endpoint.strip()
    if payload.custom_llm_api_key is not None and payload.custom_llm_api_key.strip():
        settings.custom_llm_api_key = payload.custom_llm_api_key.strip()
        os.environ["CUSTOM_LLM_API_KEY"] = settings.custom_llm_api_key
    if payload.local_llm_enabled is not None:
        settings.local_llm_enabled = payload.local_llm_enabled
    if payload.local_llm_endpoint is not None:
        settings.local_llm_endpoint = payload.local_llm_endpoint.strip()
    if payload.local_llm_model is not None:
        settings.local_llm_model = payload.local_llm_model.strip()

    return get_settings_status()

@router.post("/test-gemini")
def test_gemini():
    return test_gemini_connection()

@router.post("/test-local-llm")
def test_local_llm():
    return test_local_llm_connection()
