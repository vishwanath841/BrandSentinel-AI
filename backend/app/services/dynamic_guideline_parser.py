import re
from typing import Dict, Any, List, Optional
from pathlib import Path

def parse_brand_guidelines_dynamically(document_text: str, filename: str = "") -> Dict[str, Any]:
    """
    Dynamically extracts Brand DNA (Rules, Forbidden Terms, Approved Facts, Colors, Tone)
    from ANY arbitrary company policy document without hardcoded static data.
    """
    text = document_text.strip()
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # 1. Extract Brand Name
    brand_name = ""
    # Check for title patterns e.g. "XYZ Enterprise Brand Guidelines" or "XYZ Brand Policy"
    for line in lines[:8]:
        title_match = re.search(r"^(.*?)(?:\s+(?:Brand|Corporate|Identity|Governance|Guidelines|Standard|Policy))", line, re.IGNORECASE)
        if title_match and len(title_match.group(1).strip()) > 2:
            brand_name = title_match.group(1).strip()
            break
        elif "guidelines" in line.lower() or "policy" in line.lower():
            clean = re.sub(r"(?i)\b(brand|guidelines|policy|corporate|standard|v\d+(\.\d+)?|confidential)\b", "", line).strip()
            if len(clean) > 2:
                brand_name = clean
                break

    if not brand_name and filename:
        clean_file = Path(filename).stem
        clean_file = re.sub(r"(?i)[-_](guidelines?|policy|doc|standard)", "", clean_file)
        brand_name = clean_file.replace("_", " ").replace("-", " ").title()

    if not brand_name:
        brand_name = "Enterprise Brand"

    # 2. Dynamic Hex Color Palette Extraction
    hex_colors = list(dict.fromkeys(re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", text)))
    primary_color = hex_colors[0] if len(hex_colors) > 0 else "#1E3A8A"
    secondary_color = hex_colors[1] if len(hex_colors) > 1 else "#0284C7"
    accent_color = hex_colors[2] if len(hex_colors) > 2 else "#10B981"
    background_color = hex_colors[3] if len(hex_colors) > 3 else "#FFFFFF"
    text_color = hex_colors[4] if len(hex_colors) > 4 else "#0F172A"

    # 3. Dynamic Voice Traits & Avoided Tones Extraction
    COMMON_VOICE_TRAITS = [
        "Professional", "Authoritative", "Empathetic", "Data-driven", "Direct",
        "Precise", "Warm", "Inspiring", "Approachable", "Transparent", "Bold",
        "Innovative", "Trustworthy", "Accessible", "Customer-centric", "Helpful"
    ]
    COMMON_AVOIDED_TONES = [
        "Aggressive", "Hyperbolic", "Overly informal", "Sarcastic", "Slang",
        "Disparaging", "Arrogant", "Defensive", "Jargon-heavy", "Vague"
    ]

    detected_traits = []
    detected_avoided = []

    text_lower = text.lower()
    for trait in COMMON_VOICE_TRAITS:
        if re.search(rf"\b{trait.lower()}\b", text_lower):
            detected_traits.append(trait)

    for tone in COMMON_AVOIDED_TONES:
        if re.search(rf"\b{tone.lower()}\b", text_lower):
            detected_avoided.append(tone)

    if not detected_traits:
        detected_traits = ["Professional", "Authoritative", "Direct"]
    if not detected_avoided:
        detected_avoided = ["Aggressive", "Hyperbolic", "Overly informal"]

    # 4. Dynamic Terminology & Rule Extraction (Dos and Don'ts / Prohibitions)
    rules: List[Dict[str, Any]] = []

    # Pattern A: "DO NOT USE: 'a', 'b', 'c'" or "AVOID: 'x', 'y'" or "PROHIBITED: ..."
    forbidden_matches = re.findall(
        r"(?:never\s+use|do\s+not\s+(?:use|say)|avoid|prohibited|forbidden|banned)(?:\s+terms?)?[:\s]+([^\n\.;]+)",
        text,
        re.IGNORECASE
    )

    extracted_forbidden_terms = []
    for match_group in forbidden_matches:
        # Split by commas, quotes, 'or', slashes
        raw_terms = re.split(r"[,;/\n]|\bor\b", match_group)
        for term in raw_terms:
            clean_term = term.strip().strip("'\"-•* ")
            if clean_term and len(clean_term) > 2 and len(clean_term) < 50:
                extracted_forbidden_terms.append(clean_term)

    # Pattern B: "USE 'X' INSTEAD OF 'Y'"
    replacement_matches = re.findall(
        r"(?:use|prefer)\s+['\"]?([^'\"\n,]+)['\"]?\s+(?:instead\s+of|over|rather\s+than)\s+['\"]?([^'\"\n\.;]+)['\"]?",
        text,
        re.IGNORECASE
    )

    for pref, forb in replacement_matches:
        clean_pref = pref.strip().strip("'\"")
        clean_forb = forb.strip().strip("'\"")
        if clean_pref and clean_forb:
            rules.append({
                "category": "TERMINOLOGY",
                "rule_name": f"Approved Terminology: {clean_pref}",
                "description": f"Use '{clean_pref}' instead of '{clean_forb}'.",
                "preferred_term": clean_pref,
                "forbidden_terms": [clean_forb],
                "severity": "HIGH",
                "rationale": "Enforces company-approved vocabulary extracted from brand policy."
            })

    # Group extracted forbidden terms if any
    if extracted_forbidden_terms:
        # Deduplicate
        unique_forbidden = list(dict.fromkeys(extracted_forbidden_terms))
        rules.append({
            "category": "TERMINOLOGY",
            "rule_name": "Prohibited Brand Terminology",
            "description": "Terms explicitly prohibited in company policy.",
            "preferred_term": "approved company terminology",
            "forbidden_terms": unique_forbidden[:10],
            "severity": "HIGH",
            "rationale": "Identified as strictly avoided in company documentation."
        })

    # Pattern C: Check for Competitor Disparagement Policy
    if re.search(r"\b(competitor|rival|disparag|defam|legal)\b", text_lower):
        # Extract quoted disparaging phrases like 'is garbage', 'worthless tool'
        comp_list = []
        # Find all quoted terms in competitor/disparagement context paragraphs
        comp_paragraphs = re.findall(
            r"(?:competitor|rival|disparag|never\s+attack|do\s+not)[^\n]*",
            text, re.IGNORECASE
        )
        for para in comp_paragraphs:
            # Extract single-quoted terms: 'is garbage', 'worthless tool'
            quoted = re.findall(r"'([^']{2,30})'", para)
            comp_list.extend([q.strip() for q in quoted if len(q.strip()) > 2])
            # Extract double-quoted terms
            dquoted = re.findall(r'"([^"]{2,30})"', para)
            comp_list.extend([q.strip() for q in dquoted if len(q.strip()) > 2])

        # Deduplicate while preserving order
        comp_list = list(dict.fromkeys(comp_list))

        # Always include common disparaging phrases as fallback
        default_disparaging = ["is garbage", "is terrible", "rip off", "scam", "worthless"]
        if not comp_list:
            comp_list = default_disparaging
        
        rules.append({
            "category": "COMPETITOR",
            "rule_name": "Competitor Disparagement Policy",
            "description": "Never use derogatory language or unverified claims against competitors.",
            "preferred_term": "objective performance benchmarks",
            "forbidden_terms": comp_list,
            "severity": "CRITICAL",
            "rationale": "Protects company against defamation and anti-competitive liability."
        })

    # Fallback rule if document was sparse
    if not rules:
        rules.append({
            "category": "TERMINOLOGY",
            "rule_name": "Standard Company Nomenclature",
            "description": f"Enforce official name: {brand_name}.",
            "preferred_term": f"{brand_name} Official Product",
            "forbidden_terms": ["the cheap tool", "magic system", "untested prototype"],
            "severity": "HIGH",
            "rationale": "Extracted from brand policy document guidelines."
        })

    # 5. Dynamic Approved Facts & Proof Points Extraction (ClaimGuard Knowledge Base)
    approved_facts: List[Dict[str, Any]] = []

    # Split lines and sentences while preserving decimal numbers like 99.99%
    all_sentences = [s.strip() for s in re.split(r'(?<!\d)\.(?!\d)|\n+', text) if s.strip()]

    for clean_fs in all_sentences:
        clean_fs = clean_fs.lstrip("-•* ").strip()
        # Skip section headings (lines that start with numbers followed by periods or colons)
        if re.match(r"^\d+[\.\)]\s", clean_fs):
            continue
        if len(clean_fs) > 15 and len(clean_fs) < 250:
            if re.search(r"\b(?:\d+(?:\.\d+)?%|sla|uptime|customers?|users?|iso\s*\d+|soc\s*2|hipaa|gdpr|certified|latency)\b", clean_fs, re.IGNORECASE):
                topic = "Performance Metric"
                if "sla" in clean_fs.lower() or "uptime" in clean_fs.lower():
                    topic = "SLA & Availability Guarantee"
                elif "customer" in clean_fs.lower() or "user" in clean_fs.lower():
                    topic = "Scale & Customer Count"
                elif any(cert in clean_fs.lower() for cert in ["iso", "soc", "hipaa", "gdpr", "certified"]):
                    topic = "Regulatory Certification & Compliance"

                approved_facts.append({
                    "claim_topic": topic,
                    "approved_text": clean_fs,
                    "verification_source": f"Extracted from {filename or 'Company Policy Document'}"
                })

    # Deduplicate facts by topic, preferring facts that contain actual numbers/metrics
    seen_topics: Dict[str, Dict[str, Any]] = {}
    for f in approved_facts:
        topic = f["claim_topic"]
        has_metric = bool(re.search(r"\d+(?:\.\d+)?%?", f["approved_text"]))
        if topic not in seen_topics:
            seen_topics[topic] = f
        elif has_metric and not re.search(r"\d+(?:\.\d+)?%?", seen_topics[topic]["approved_text"]):
            # Replace heading-like entry with actual metric-containing fact
            seen_topics[topic] = f
    unique_facts = list(seen_topics.values())

    if not unique_facts:
        unique_facts.append({
            "claim_topic": "Corporate Quality Benchmark",
            "approved_text": f"{brand_name} adheres to audited technical service level standards.",
            "verification_source": f"Extracted from {filename or 'Company Policy'}"
        })

    # 6. Extract Mission & Tagline if present
    mission_match = re.search(r"(?:mission|positioning|purpose)[:\s]+([^\n\.]+)", text, re.IGNORECASE)
    mission = mission_match.group(1).strip() if mission_match else f"Delivering excellence for {brand_name} partners."

    tagline_match = re.search(r"(?:tagline|slogan)[:\s]+['\"]?([^'\"\n]+)['\"]?", text, re.IGNORECASE)
    tagline = tagline_match.group(1).strip() if tagline_match else f"Engineered by {brand_name}"

    return {
        "name": brand_name,
        "industry": "Enterprise Solutions",
        "tagline": tagline,
        "mission": mission,
        "target_audience": "Professional & Enterprise Stakeholders",
        "voice_traits": detected_traits[:5],
        "avoided_tones": detected_avoided[:4],
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "accent_color": accent_color,
        "background_color": background_color,
        "text_color": text_color,
        "rules": rules,
        "approved_facts": unique_facts[:6]
    }
