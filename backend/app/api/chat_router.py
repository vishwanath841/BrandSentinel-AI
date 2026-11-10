from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.brand import BrandProfile
from app.services.local_llm_service import get_llm_headers, is_local_llm_available
from app.services.gemini_service import get_active_gemini_key, GEMINI_BASE_URL
from app.config import settings
import httpx
import json

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    brand_id: int
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str
    model_used: str

@router.post("", response_model=ChatResponse)
async def chat_with_sentinel(payload: ChatRequest, db: Session = Depends(get_db)):
    brand = db.query(BrandProfile).filter(BrandProfile.id == payload.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_rules_text = "\n".join([
        f"- {r.rule_name} ({r.category}): Preferred: '{r.preferred_term}', Avoid: {r.forbidden_terms}. Severity: {r.severity}"
        for r in brand.rules if r.is_active
    ])
    facts_text = "\n".join([
        f"- {f.claim_topic}: {f.approved_text} [Source: {f.verification_source}]"
        for f in brand.approved_facts if f.is_active
    ])

    system_prompt = f"""You are BrandSentinel AI Assistant.
You help creators, copywriters, and marketers write on-brand content and check brand policies.

CURRENT BRAND CONTEXT:
Brand Name: {brand.name}
Industry: {brand.industry}
Mission: {brand.mission}
Voice Traits: {', '.join(brand.voice_traits or [])}
Avoided Tones: {', '.join(brand.avoided_tones or [])}
Primary Colors: {brand.primary_color}, {brand.secondary_color}, {brand.accent_color}

APPROVED TERMINOLOGY & RULES:
{brand_rules_text or 'No specific custom rules configured.'}

APPROVED CLAIMGUARD FACTS:
{facts_text or 'No specific facts configured.'}

GUIDELINES FOR YOUR RESPONSES:
1. Be helpful, concise, authoritative, and direct.
2. If asked to rewrite or check text, explain whether it complies with this brand's rules and suggest an intent-preserving compliant version.
3. If asked about facts/SLAs, cite only the approved facts listed above.
4. Keep answers short and actionable (under 150 words)."""

    # 1. Try NVIDIA / Custom LLM (Tier 2)
    if settings.local_llm_enabled:
        url = settings.local_llm_endpoint.rstrip("/")
        model = settings.local_llm_model
        
        messages = [{"role": "system", "content": system_prompt}]
        for h in (payload.history or [])[-6:]:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": payload.message})

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    f"{url}/chat/completions",
                    headers=get_llm_headers(),
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 800,
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get("choices", [{}])[0].get("message", {})
                    reply_text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                    if reply_text:
                        return ChatResponse(reply=reply_text, model_used="Sentinel AI Copilot")
                else:
                    print(f"Chatbot LLM failed with HTTP {resp.status_code}: {resp.text[:200]}", flush=True)
        except Exception as e:
            print(f"Chatbot LLM request error: {str(e)}", flush=True)

    # 2. Try Gemini (Tier 1)
    gemini_key = get_active_gemini_key()
    if gemini_key:
        model = settings.gemini_model or "gemini-2.5-flash"
        gemini_url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={gemini_key}"
        full_prompt = f"{system_prompt}\n\nUser Question:\n{payload.message}"
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    gemini_url,
                    json={"contents": [{"parts": [{"text": full_prompt}]}]}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return ChatResponse(reply=text.strip(), model_used="Sentinel AI Copilot")
        except Exception:
            pass

    # 3. Fallback: Context-Aware Brand Knowledge Engine
    msg_lower = payload.message.lower()
    if any(q in msg_lower for q in ["sla", "uptime", "guarantee", "fact"]):
        facts_list = [f.approved_text for f in brand.approved_facts if f.is_active]
        reply = f"Here are {brand.name}'s verified proof points:\n" + "\n".join(f"• {f}" for f in facts_list[:3])
    elif any(q in msg_lower for q in ["rule", "forbidden", "term", "avoid", "word"]):
        rules_list = [f"Use '{r.preferred_term}' instead of '{r.forbidden_terms}'" for r in brand.rules if r.is_active and r.preferred_term]
        reply = f"Key terminology guidelines for {brand.name}:\n" + "\n".join(f"• {r}" for r in rules_list[:3])
    elif any(q in msg_lower for q in ["tone", "voice"]):
        reply = f"{brand.name}'s approved voice traits are: {', '.join(brand.voice_traits or [])}. Please avoid: {', '.join(brand.avoided_tones or [])}."
    else:
        reply = f"I'm BrandSentinel's AI Guardian for **{brand.name}**. You can ask me to check headlines, rewrite copy, or verify brand SLA facts."

    return ChatResponse(reply=reply, model_used="Sentinel AI Copilot (Knowledge Base)")
