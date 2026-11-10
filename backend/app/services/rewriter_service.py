import re
from typing import List, Dict, Any, Optional

def apply_revisions_to_text(original_text: str, findings: List[Dict[str, Any]]) -> str:
    """
    Apply accepted or edited revisions to the original text.
    Replaces flagged phrases with their accepted/edited revisions.
    """
    if not original_text:
        return ""

    updated_text = original_text

    # Sort findings by flagged_text length descending to avoid partial prefix collisions
    active_revisions = [
        f for f in findings
        if f.get("review_status") in ["ACCEPTED", "EDITED"] and f.get("flagged_text")
    ]
    active_revisions.sort(key=lambda x: len(x.get("flagged_text", "")), reverse=True)

    for rev in active_revisions:
        flagged = rev.get("flagged_text", "")
        # Prefer custom reviewed revision if user edited it, otherwise use suggested revision
        replacement = rev.get("reviewed_revision") or rev.get("suggested_revision") or ""
        
        if flagged and replacement and flagged in updated_text:
            # Replace occurrences
            updated_text = updated_text.replace(flagged, replacement)

    return updated_text

def generate_sentence_diff(original_sentence: str, revised_sentence: str) -> Dict[str, Any]:
    """
    Generate structured comparison between original and revised sentence.
    """
    return {
        "original": original_sentence,
        "revised": revised_sentence,
        "is_changed": original_sentence.strip() != revised_sentence.strip()
    }

