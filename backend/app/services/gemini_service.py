import os
import json
import base64
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MODELS_CASCADE = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

def get_all_gemini_keys() -> List[str]:
    """Retrieve all configured primary and backup Gemini API keys for failover pool."""
    raw = f"{settings.gemini_api_key},{settings.gemini_backup_keys},{os.getenv('GEMINI_API_KEY', '')},{os.getenv('GEMINI_BACKUP_KEYS', '')}"
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    seen = set()
    result = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            result.append(k)
    return result

def get_active_gemini_key() -> str:
    keys = get_all_gemini_keys()
    return keys[0] if keys else ""

def test_gemini_connection(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Test Gemini API connectivity with given or configured key."""
    key = (api_key or get_active_gemini_key()).strip()
    if not key:
        return {"success": False, "message": "No API key provided."}

    model = settings.gemini_model or "gemini-2.5-flash"
    url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={key}"

    payload = {
        "contents": [
            {"parts": [{"text": "Reply with 'OK' if you can read this."}]}
        ]
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {"success": True, "message": f"Connected successfully to {model}!", "sample_response": text.strip()}
            else:
                return {
                    "success": False,
                    "message": f"Gemini API returned HTTP {resp.status_code}: {resp.text[:300]}"
                }
    except Exception as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}


def analyze_with_gemini(
    text: str,
    brand_context: Dict[str, Any],
    rules: List[Dict[str, Any]],
    approved_facts: List[Dict[str, Any]],
    model_name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Call Gemini LLM with automatic key-pool rotation and multi-model cascade failover.
    If primary key or model hits quota (429/503), it automatically tries backup keys/models.
    """
    keys = get_all_gemini_keys()
    if not keys:
        return None

    preferred_model = model_name or settings.gemini_model or "gemini-2.5-flash"
    models_to_try = [preferred_model] + [m for m in MODELS_CASCADE if m != preferred_model]

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
Do not wrap the json in extra markdown codeblocks if possible, or use standard ```json.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": f"CONTENT TO INSPECT:\n\n{text}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    # Iterate through keys and models cascade
    for key in keys:
        for model in models_to_try:
            url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={key}"
            try:
                with httpx.Client(timeout=25.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        clean_json = raw_text.strip()
                        if clean_json.startswith("```json"):
                            clean_json = clean_json[7:]
                        if clean_json.startswith("```"):
                            clean_json = clean_json[3:]
                        if clean_json.endswith("```"):
                            clean_json = clean_json[:-3]

                        result_data = json.loads(clean_json.strip())
                        result_data["engine_model_used"] = model
                        return result_data
                    elif resp.status_code in [429, 503]:
                        # Rate limit or service overload: cascade to next model or key
                        continue
                    else:
                        # Non-retryable error for this key: try next key
                        break
            except Exception:
                continue

    return None


def extract_brand_guidelines_with_gemini(document_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract Brand DNA parameters from an uploaded brand guideline document.
    """
    key = get_active_gemini_key()
    if not key:
        return None

    model = settings.gemini_model or "gemini-2.5-flash"
    url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={key}"

    prompt = f"""You are BrandSentinel AI's guideline ingestion engine.
Read this brand guideline document and extract a structured Brand DNA profile.

DOCUMENT TEXT:
{document_text[:12000]}

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
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                clean_json = raw_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                return json.loads(clean_json.strip())
            return None
    except Exception:
        return None

