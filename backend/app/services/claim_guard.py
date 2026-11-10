import re
from typing import List, Dict, Any, Tuple
from app.models.brand import ApprovedFact

# Patterns for promotional superlatives and quantitative assertions
SUPERLATIVE_PATTERNS = [
    (r"\b(#1|number one|no\.?\s*1)\b", "Absolute market leadership claim"),
    (r"\b(world'?s? first|industry first)\b", "Pioneering claim"),
    (r"\b(100%|guaranteed|guarantee|unbreakable|zero downtime|100% bug-free|flawless)\b", "Absolute guarantee or perfection claim"),
    (r"\b(fastest|cheapest|best-in-class|most secure|infinitely scalable)\b", "Unqualified superlative claim"),
    (r"\b(\d+(?:\.\d+)?%)\s*(?:uptime|sla|accuracy|availability)\b", "SLA or availability percentage claim"),
    (r"\b(\d+[\d,]*\+?|\d+\s*(?:million|thousand|billion|k))\s*(?:users|customers|clients|enterprises|downloads)\b", "Customer or user count claim"),
    (r"\b(iso\s*\d+|soc\s*2|hipaa|gdpr|pci-dss|fedramp)\b", "Regulatory compliance or certification claim")
]

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences while preserving structure."""
    if not text:
        return []
    # Split by periods, exclamation marks, or newlines
    raw_sentences = re.split(r"(?<=[.!?\n])\s+", text)
    return [s.strip() for s in raw_sentences if len(s.strip()) > 5]

def verify_claims(text: str, approved_facts: List[ApprovedFact]) -> Dict[str, Any]:
    """
    ClaimGuard Engine:
    Detects promotional assertions, verifies against approved facts,
    and applies the Reliability Principle:
    - Never mark unverified claims as 'false'; label them as 'UNSUPPORTED_NEEDS_REVIEW'.
    - Flag direct metric contradictions as 'CONTRADICTION'.
    """
    if not text:
        return {
            "findings": [],
            "score": 100.0,
            "verified_count": 0,
            "unsupported_count": 0,
            "contradiction_count": 0
        }

    findings = []
    sentences = split_into_sentences(text)
    
    verified_count = 0
    unsupported_count = 0
    contradiction_count = 0
    deductions = 0.0

    # Build index of approved facts
    facts_lookup = []
    for f in approved_facts:
        if f.is_active:
            facts_lookup.append({
                "topic": f.claim_topic.lower(),
                "text": f.approved_text,
                "text_lower": f.approved_text.lower(),
                "metrics": f.metrics or {},
                "source": f.verification_source
            })

    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Check if sentence contains any promotional or quantitative patterns
        has_promotional_pattern = False
        pattern_desc = ""
        matched_phrase = ""

        for pattern_regex, desc in SUPERLATIVE_PATTERNS:
            match = re.search(pattern_regex, sentence, re.IGNORECASE)
            if match:
                has_promotional_pattern = True
                pattern_desc = desc
                matched_phrase = match.group(0)
                break

        if not has_promotional_pattern:
            continue

        # Now search for supporting evidence in approved facts
        best_fact = None
        best_score = 0
        for fact in facts_lookup:
            # Check overlap between words in sentence and approved fact (3+ chars to capture SLA, ISO, SOC etc.)
            words_sent = set(re.findall(r"\b\w{3,}\b", sentence_lower))
            words_fact = set(re.findall(r"\b\w{3,}\b", fact["text_lower"]))
            overlap = len(words_sent.intersection(words_fact))
            
            # Check topic match
            topic_words = set(re.findall(r"\b\w{3,}\b", fact["topic"]))
            topic_overlap = len(words_sent.intersection(topic_words))

            # Also check if both contain percentage metrics in similar domains
            sent_has_pct = bool(re.search(r"\d+(?:\.\d+)?%", sentence_lower))
            fact_has_pct = bool(re.search(r"\d+(?:\.\d+)?%", fact["text_lower"]))
            pct_domain_match = sent_has_pct and fact_has_pct and overlap >= 1

            score = overlap + topic_overlap * 2 + (3 if pct_domain_match else 0)
            if (overlap >= 2 or topic_overlap >= 1 or pct_domain_match) and score > best_score:
                best_fact = fact
                best_score = score

        if best_fact:
            # Extract numbers including percentages
            sent_numbers = re.findall(r"\b\d+(?:\.\d+)?(?:%|\b)", sentence)
            fact_numbers = re.findall(r"\b\d+(?:\.\d+)?(?:%|\b)", best_fact["text"])

            is_contradiction = False
            conflicting_sent_num = None
            conflicting_fact_num = None

            for s_num in sent_numbers:
                if s_num in fact_numbers:
                    continue
                # If there are numbers in both, check if sentence number diverges from fact number
                for f_num in fact_numbers:
                    if s_num != f_num:
                        is_contradiction = True
                        conflicting_sent_num = s_num
                        conflicting_fact_num = f_num
                        break
                if is_contradiction:
                    break

            if is_contradiction:
                contradiction_count += 1
                deductions += 25.0
                findings.append({
                    "category": "CLAIM_GUARD",
                    "severity": "CRITICAL",
                    "flagged_text": sentence,
                    "explanation": f"Claim contradicts approved company record: text claims '{conflicting_sent_num}', but approved verified metric is '{conflicting_fact_num}'.",
                    "evidence": f"Approved Fact ({best_fact['topic']}): \"{best_fact['text']}\" [Source: {best_fact['source']}]",
                    "claim_status": "CONTRADICTION",
                    "suggested_revision": sentence.replace(conflicting_sent_num, conflicting_fact_num) if conflicting_sent_num and conflicting_fact_num else best_fact["text"],
                    "revision_rationale": "Corrects factual discrepancy to match audited brand documentation."
                })
            else:
                verified_count += 1
                # Verified claim - good compliance!
                findings.append({
                    "category": "CLAIM_GUARD",
                    "severity": "LOW",
                    "flagged_text": sentence,
                    "explanation": "Claim is supported by verified company records.",
                    "evidence": f"Approved Fact ({best_fact['topic']}): \"{best_fact['text']}\" [Source: {best_fact['source']}]",
                    "claim_status": "VERIFIED",
                    "suggested_revision": sentence,
                    "revision_rationale": "Statement is fully verified against approved proof points."
                })
        else:
            # No matching approved fact found!
            # RELIABILITY PRINCIPLE: Label as UNSUPPORTED_NEEDS_REVIEW, do NOT claim it is false!
            unsupported_count += 1
            deductions += 15.0
            
            # Suggest tempered intent-preserving alternative
            suggested_revision = sentence
            if re.search(r"\b(100%|guaranteed|zero downtime)\b", sentence, re.IGNORECASE):
                suggested_revision = re.sub(r"\b100% bug-free\b", "thoroughly tested and verified", suggested_revision, flags=re.IGNORECASE)
                suggested_revision = re.sub(r"\bguaranteed zero downtime\b", "industry-leading high availability", suggested_revision, flags=re.IGNORECASE)
                suggested_revision = re.sub(r"\b100% secure\b", "enterprise-grade security architecture", suggested_revision, flags=re.IGNORECASE)
            elif re.search(r"\b(#1|world'?s? first)\b", sentence, re.IGNORECASE):
                suggested_revision = re.sub(r"\b(#1|number one)\b", "a leading", suggested_revision, flags=re.IGNORECASE)
                suggested_revision = re.sub(r"\bworld'?s? first\b", "an advanced", suggested_revision, flags=re.IGNORECASE)
            else:
                suggested_revision = f"{sentence} [Requires verification before publishing]"

            findings.append({
                "category": "CLAIM_GUARD",
                "severity": "HIGH",
                "flagged_text": sentence,
                "explanation": f"Unverified promotional claim detected ({pattern_desc}). Supporting evidence was not found in approved brand records.",
                "evidence": "Reliability Principle: This claim is labeled as 'Unsupported / Needs Review'. It has not been verified against approved company facts and requires reviewer sign-off.",
                "claim_status": "UNSUPPORTED_NEEDS_REVIEW",
                "suggested_revision": suggested_revision,
                "revision_rationale": "Tempering unsupported superlatives mitigates legal risk while preserving the creator's value proposition."
            })

    fact_score = max(0.0, min(100.0, round(100.0 - deductions, 1)))

    return {
        "findings": findings,
        "score": fact_score,
        "verified_count": verified_count,
        "unsupported_count": unsupported_count,
        "contradiction_count": contradiction_count
    }
