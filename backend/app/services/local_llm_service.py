"""
Local LLM Service — connects to any OpenAI-compatible local endpoint
(Ollama, LM Studio, text-generation-webui, etc.).

This tier sits between Gemini Cloud and the deterministic Semantic Engine:
  Tier 1: Gemini API  (cloud, if key configured)
  Tier 2: Local LLM   (if LOCAL_LLM_ENABLED=true and server reachable)
  Tier 3: Semantic Engine (always works, zero dependencies)

After deployment: if the local LLM isn't running on the server,
the call fails gracefully in <2 s and the Semantic Engine takes over.
"""

import os
import json
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings


def get_llm_headers() -> Dict[str, str]:
    """Build request headers, adding Bearer token if API key is configured."""
    headers = {"Content-Type": "application/json"}
    token = (settings.custom_llm_api_key or os.getenv("CUSTOM_LLM_API_KEY", "") or os.getenv("NVIDIA_API_KEY", "")).strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def is_local_llm_available() -> bool:
    """Quick health-check — returns True only if the endpoint responds."""
    if not settings.local_llm_enabled:
        return False
    try:
        url = settings.local_llm_endpoint.rstrip("/")
        # Ollama exposes /v1/models; LM Studio and NVIDIA the same
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{url}/models", headers=get_llm_headers())
            return resp.status_code == 200
    except Exception:
        return False


def test_local_llm_connection() -> Dict[str, Any]:
    """Explicit connectivity test with a tiny prompt."""
    if not settings.local_llm_enabled:
        return {"success": False, "message": "Local/Custom LLM is not enabled. Set LOCAL_LLM_ENABLED=true in .env"}

    url = settings.local_llm_endpoint.rstrip("/")
    model = settings.local_llm_model

    try:
        with httpx.Client(timeout=25.0) as client:
            resp = client.post(
                f"{url}/chat/completions",
                headers=get_llm_headers(),
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "Reply with 'OK' in one word."}],
                    "temperature": 0.0,
                    "max_tokens": 400,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                return {"success": True, "message": f"Connected to {model} successfully!", "sample_response": text[:100]}
            else:
                return {"success": False, "message": f"LLM Endpoint returned HTTP {resp.status_code}: {resp.text[:300]}"}
    except httpx.ConnectError:
        return {"success": False, "message": f"Cannot connect to {url} — server unreachable."}
    except Exception as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}


def _clean_json_from_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse valid JSON even if wrapped in markdown or preceded by reasoning."""
    if not raw_text:
        return None
    clean = raw_text.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0].strip()
    
    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1 and end > start:
        clean = clean[start:end+1]
        
    try:
        return json.loads(clean)
    except Exception:
        return None


def analyze_with_local_llm(
    text: str,
    brand_context: Dict[str, Any],
    rules: List[Dict[str, Any]],
    approved_facts: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Send the same BrandSentinel inspection prompt to the local LLM.
    Returns parsed JSON result or None on any failure.
    """
    if not settings.local_llm_enabled:
        return None

    url = settings.local_llm_endpoint.rstrip("/")
    model = settings.local_llm_model

    system_prompt = f"""You are BrandSentinel AI's deep content inspection engine.
Analyze the submitted content strictly against the provided brand governance rules and approved facts.

BRAND PROFILE:
Name: {brand_context.get('name')}
Industry: {brand_context.get('industry')}
Approved Voice Traits: {', '.join(brand_context.get('voice_traits', []))}
Avoided/Prohibited Tones: {', '.join(brand_context.get('avoided_tones', []))}

CONFIGURED TERMINOLOGY RULES:
{json.dumps(rules, indent=2)}

APPROVED COMPANY FACTS (CLAIMGUARD KNOWLEDGE BASE):
{json.dumps(approved_facts, indent=2)}

CRITICAL GOVERNANCE RULES:
1. Reliability Principle: Distinguish verified violations from uncertain findings. Never claim a promotional statement is false solely because supporting evidence was not found; label it as 'UNSUPPORTED_NEEDS_REVIEW'.
2. Intent-Preserving Rewriting: For every violation, generate a suggestion that fixes the tone or terminology while strictly preserving the author's original context, purpose, and value proposition.
3. Classify claims as:
   - 'VERIFIED': Fully backed by approved facts.
   - 'CONTRADICTION': Directly conflicts with an approved fact or certified number.
   - 'UNSUPPORTED_NEEDS_REVIEW': Unsubstantiated promotional claim, superlative, or unverified statistic requiring human reviewer sign-off.
   - 'COMPLIANT': Appropriate.

OUTPUT FORMAT:
Respond ONLY with a valid JSON object with the following exact keys:
{{
  "overall_score": float (0-100),
  "tone_score": float (0-100),
  "terminology_score": float (0-100),
  "fact_score": float (0-100),
  "risk_level": "PASS" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "summary": "Comprehensive 3-4 sentence executive briefing describing the core subject matter of the document, key compliance deviations identified, and the essential action required before publication. Write in polished enterprise prose without generic label prefixes.",
  "findings": [
    {{
      "category": "TONE" | "TERMINOLOGY" | "CLAIM_GUARD" | "MESSAGING",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "flagged_text": "Exact substring from content",
      "explanation": "Why this violates brand rules",
      "evidence": "Citation of rule or approved fact",
      "claim_status": "VERIFIED" | "CONTRADICTION" | "UNSUPPORTED_NEEDS_REVIEW" | null,
      "suggested_revision": "Intent-preserving rewrite",
      "revision_rationale": "Why this revision works while preserving creator's message"
    }}
  ]
}}
Do not include any text outside the JSON object."""

    try:
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(
                f"{url}/chat/completions",
                headers=get_llm_headers(),
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"CONTENT TO INSPECT:\n\n{text}"},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4096,
                },
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            msg = data.get("choices", [{}])[0].get("message", {})
            raw_text = (msg.get("content") or msg.get("reasoning_content") or "").strip()

            result = _clean_json_from_response(raw_text)
            if result:
                result["engine_model_used"] = f"custom:{model}"
            return result

    except (httpx.ConnectError, httpx.ReadTimeout):
        # Server not running — graceful fallback
        return None
    except (json.JSONDecodeError, KeyError, IndexError):
        # Model returned non-JSON — graceful fallback
        return None
    except Exception:
        return None


def extract_guidelines_with_local_llm(document_text: str) -> Optional[Dict[str, Any]]:
    """
    Use the local LLM to extract Brand DNA from an uploaded guideline document.
    Falls back to None so the dynamic parser takes over.
    """
    if not settings.local_llm_enabled:
        return None

    url = settings.local_llm_endpoint.rstrip("/")
    model = settings.local_llm_model

    prompt = f"""You are BrandSentinel AI's guideline ingestion engine.
Read this brand guideline document and extract a structured Brand DNA profile.

DOCUMENT TEXT:
{document_text[:8000]}

Extract the following in JSON format:
{{
  "name": "Brand Name",
  "industry": "Industry / Domain",
  "tagline": "Brand Tagline",
  "mission": "Mission or positioning statement",
  "target_audience": "Target audience",
  "voice_traits": ["Trait 1", "Trait 2", "Trait 3"],
  "avoided_tones": ["Avoided Tone 1", "Avoided Tone 2"],
  "primary_color": "#HEX",
  "secondary_color": "#HEX",
  "accent_color": "#HEX",
  "background_color": "#FFFFFF",
  "text_color": "#0F172A",
  "rules": [
    {{
      "category": "TERMINOLOGY" | "MESSAGING" | "LEGAL",
      "rule_name": "Rule Title",
      "description": "Rule explanation",
      "preferred_term": "Approved term",
      "forbidden_terms": ["forbidden1", "discouraged2"],
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "rationale": "Why this matters"
    }}
  ],
  "approved_facts": [
    {{
      "claim_topic": "Topic like SLA / User Base / Security",
      "approved_text": "Exact verified wording",
      "verification_source": "Source citation"
    }}
  ]
}}
Respond ONLY with valid JSON. No extra text."""

    try:
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(
                f"{url}/chat/completions",
                headers=get_llm_headers(),
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            msg = data.get("choices", [{}])[0].get("message", {})
            raw_text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
            return _clean_json_from_response(raw_text)

    except Exception:
        return None

