import re
from typing import List, Dict, Any
from app.models.brand import BrandProfile

# Avoided tone keyword patterns
TONE_FLAG_PATTERNS = {
    "Aggressive": [
        (r"\b(or else|idiots?|stupid|wake up|shut up|buy now or suffer|you will regret)\b", "Aggressive or coercive phrasing"),
        (r"\b(crush(?:ed|ing)? our rivals|destroy the competition|rip off)\b", "Combative rhetoric")
    ],
    "Hyperbolic": [
        (r"\b(insane(?:ly)?|miracle|magic|unbelievable|mind-blowing|earth-shattering|revolutionary beyond belief)\b", "Sensationalized hyperbole"),
        (r"\b(infinite(?:ly)?|limitless|never-ending|unstoppable)\b", "Unrealistic hyperbole")
    ],
    "Overly informal": [
        (r"\b(gonna|wanna|y'?all|btw|tbh|omg|coolest thing ever|dude|bro|ain'?t)\b", "Casual colloquialisms unsuitable for enterprise communication"),
        (r"[!?]{2,}", "Excessive exclamation or question punctuation")
    ],
    "Disparaging": [
        (r"\b(inferior|trash|garbage|clueless|pathetic|scam)\b", "Disparaging language targeting others")
    ],
    "Slang": [
        (r"\b(bussin|cap|no cap|flexing|fire af|lit|salty)\b", "Internet slang or non-standard jargon")
    ]
}

def inspect_tone(text: str, brand: BrandProfile) -> Dict[str, Any]:
    """
    Inspects text for tone alignment against brand persona and avoided tones.
    """
    if not text:
        return {
            "findings": [],
            "score": 100.0,
            "detected_tones": [],
            "violations_count": 0
        }

    avoided = brand.avoided_tones or ["Aggressive", "Hyperbolic", "Overly informal"]
    approved_traits = brand.voice_traits or ["Professional", "Empathetic", "Direct"]
    findings = []
    deductions = 0.0

    # Scan for patterns in avoided tones
    for tone_name in avoided:
        patterns = TONE_FLAG_PATTERNS.get(tone_name, [])
        for pattern_regex, explanation in patterns:
            for match in re.finditer(pattern_regex, text, re.IGNORECASE):
                matched = match.group(0)
                start, end = match.span()
                deductions += 15.0

                # Generate clean intent-preserving suggested replacement
                replacement = ""
                if tone_name == "Hyperbolic":
                    replacement = "highly effective" if "insane" in matched.lower() or "miracle" in matched.lower() else "exceptional"
                elif tone_name == "Overly informal":
                    replacement = "going to" if matched.lower() == "gonna" else "want to" if matched.lower() == "wanna" else ""
                elif tone_name == "Aggressive":
                    replacement = "We encourage you to explore"
                else:
                    replacement = "[Refine tone]"

                findings.append({
                    "category": "TONE",
                    "severity": "HIGH" if tone_name in ["Aggressive", "Disparaging"] else "MEDIUM",
                    "flagged_text": matched,
                    "explanation": f"Detected '{tone_name}' tone ({explanation}), which conflicts with approved brand persona ({', '.join(approved_traits)}).",
                    "evidence": f"Brand Voice Guidelines: Explicitly prohibits '{tone_name}' tone in customer-facing communication.",
                    "claim_status": None,
                    "suggested_revision": replacement,
                    "revision_rationale": f"Replaces off-brand '{tone_name}' tone with {approved_traits[0] if approved_traits else 'professional'} phrasing while preserving intent.",
                    "start_char": start,
                    "end_char": end
                })

    tone_score = max(0.0, min(100.0, round(100.0 - deductions, 1)))

    return {
        "findings": findings,
        "score": tone_score,
        "violations_count": len(findings)
    }

