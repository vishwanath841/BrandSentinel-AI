import os
import sys
from pathlib import Path
from docx import Document
from sqlalchemy.orm import Session

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal, engine, Base
from app.models.brand import BrandProfile, BrandRule, ApprovedFact
from app.models.submission import ContentSubmission, AnalysisReport, IssueFinding
from app.services.extractor_service import extract_content
from app.services.dynamic_guideline_parser import parse_brand_guidelines_dynamically
from app.services.inspection_service import run_comprehensive_inspection

def run_end_to_end_policy_test():
    print("=" * 80)
    print(" BRANDSENTINEL AI: REAL DYNAMIC COMPANY POLICY INGESTION & AUDIT TEST")
    print("=" * 80)

    # 1. GENERATE A REAL COMPANY POLICY DOCX (CyberShield Security Solutions)
    docs_dir = Path("sample_documents")
    docs_dir.mkdir(exist_ok=True)
    policy_path = docs_dir / "CyberShield_Security_Policy.docx"

    print(f"\n[STEP 1] Generating dynamic company policy document: {policy_path.name}...")
    doc = Document()
    doc.add_heading("CyberShield Global Enterprise Security Brand Policy & Standards", level=0)
    
    doc.add_paragraph("Mission: Delivering sovereign, resilient cyber defense to Fortune 500 enterprises.")
    doc.add_paragraph("Tagline: Defense Engineered for Zero Trust.")
    
    doc.add_heading("1. Corporate Brand Identity & Visual Palette", level=1)
    doc.add_paragraph("CyberShield uses precise corporate branding colors:")
    doc.add_paragraph("Primary Brand Navy: #0F172A")
    doc.add_paragraph("Secondary Shield Cyan: #06B6D4")
    doc.add_paragraph("Accent Emerald: #10B981")
    doc.add_paragraph("Background Light: #F8FAFC")
    doc.add_paragraph("Text Charcoal: #334155")

    doc.add_heading("2. Brand Voice & Communication Tones", level=1)
    doc.add_paragraph("Tone of Voice: Authoritative, Transparent, Precise, Data-driven.")
    doc.add_paragraph("Avoided Tones: Hyperbolic, Arrogant, Aggressive, Overly informal.")

    doc.add_heading("3. Approved Terminology & Mandatory Nomenclature", level=1)
    doc.add_paragraph("Use 'Zero-Trust Architecture' instead of 'perimeter firewall'.")
    doc.add_paragraph("Use 'Managed Detection and Response' instead of 'antivirus tool'.")
    doc.add_paragraph("Prohibited terms: unhackable, bulletproof, magical security, cheap fix.")
    doc.add_paragraph("Competitor Policy: Never attack competitors; do not disparage other vendors with terms like 'is garbage', 'worthless tool', or 'incompetent rival'.")

    doc.add_heading("4. Verified Service Claims & SLA Facts (ClaimGuard Audit Base)", level=1)
    doc.add_paragraph("Uptime Guarantee: CyberShield Cloud operates under an audited 99.95% uptime SLA.")
    doc.add_paragraph("Enterprise Customer Scale: Currently safeguarding over 4,500 enterprise customers worldwide.")
    doc.add_paragraph("Regulatory Compliance: SOC-2 Type II, ISO 27001, and HIPAA compliance certified.")
    
    doc.save(str(policy_path))
    print(f" -> Successfully saved {policy_path} ({policy_path.stat().st_size} bytes)")

    # 2. INGEST AND PARSE THE POLICY DOCUMENT USING THE DYNAMIC PARSER
    print("\n[STEP 2] Ingesting & Extracting Policy via PyMuPDF / python-docx extractor...")
    extracted_text, metadata = extract_content(str(policy_path), "DOCX")
    print(f" -> Extracted {len(extracted_text)} characters, {metadata.get('paragraphs_count', 0)} paragraphs.")
    
    parsed_dna = parse_brand_guidelines_dynamically(extracted_text, filename=policy_path.name)
    print("\n[STEP 3] Dynamically Extracted Brand DNA:")
    print(f" -> Brand Name: {parsed_dna['name']}")
    print(f" -> Colors: Primary={parsed_dna['primary_color']}, Secondary={parsed_dna['secondary_color']}, Accent={parsed_dna['accent_color']}")
    print(f" -> Voice Traits: {parsed_dna['voice_traits']}")
    print(f" -> Avoided Tones: {parsed_dna['avoided_tones']}")
    print(f" -> Extracted Rules count: {len(parsed_dna['rules'])}")
    for r in parsed_dna['rules']:
        print(f"    * [{r['category']}] {r['rule_name']} | Preferred: '{r['preferred_term']}' | Forbidden: {r['forbidden_terms']}")
    print(f" -> Extracted Approved Facts count: {len(parsed_dna['approved_facts'])}")
    for f in parsed_dna['approved_facts']:
        print(f"    * Topic: {f['claim_topic']} | Fact: \"{f['approved_text']}\"")

    # 3. SAVE DYNAMIC BRAND PROFILE INTO THE DATABASE
    db: Session = SessionLocal()
    try:
        # Clear previous test run if exists
        old = db.query(BrandProfile).filter(BrandProfile.name == parsed_dna['name']).first()
        if old:
            db.delete(old)
            db.commit()

        brand = BrandProfile(
            name=parsed_dna['name'],
            slug=parsed_dna['name'].lower().replace(" ", "-"),
            industry=parsed_dna['industry'],
            tagline=parsed_dna['tagline'],
            mission=parsed_dna['mission'],
            target_audience=parsed_dna['target_audience'],
            primary_color=parsed_dna['primary_color'],
            secondary_color=parsed_dna['secondary_color'],
            accent_color=parsed_dna['accent_color'],
            background_color=parsed_dna['background_color'],
            text_color=parsed_dna['text_color']
        )
        brand.voice_traits = parsed_dna['voice_traits']
        brand.avoided_tones = parsed_dna['avoided_tones']
        db.add(brand)
        db.commit()
        db.refresh(brand)

        for r in parsed_dna['rules']:
            rule = BrandRule(
                brand_id=brand.id,
                category=r['category'],
                rule_name=r['rule_name'],
                description=r.get('description', ''),
                preferred_term=r.get('preferred_term', ''),
                severity=r.get('severity', 'HIGH'),
                rationale=r.get('rationale', ''),
                is_active=True
            )
            rule.forbidden_terms = r.get('forbidden_terms', [])
            db.add(rule)

        for f in parsed_dna['approved_facts']:
            fact = ApprovedFact(
                brand_id=brand.id,
                claim_topic=f['claim_topic'],
                approved_text=f['approved_text'],
                verification_source=f.get('verification_source', 'Policy Doc'),
                is_active=True
            )
            fact.metrics = f.get('metrics', {})
            db.add(fact)

        db.commit()
        db.refresh(brand)
        print(f"\n[STEP 4] Successfully committed Brand Profile #{brand.id} ('{brand.name}') to SQLite.")

        # 4. SUBMIT A DRAFT DOCUMENT WITH SUBTLE REAL-WORLD POLICY VIOLATIONS
        print("\n[STEP 5] Testing an arbitrary draft document against this new Brand Profile...")
        draft_copy = (
            "CyberShield announces our newest security suite release. "
            "Unlike legacy perimeter firewall approaches, our technology provides an unhackable defense "
            "that guarantees a 99.99% uptime SLA for your mission-critical infrastructure. "
            "Our competitor's software is garbage compared to our automated antivirus tool. "
            "We serve 10,000 satisfied enterprise clients with guaranteed zero vulnerabilities."
        )

        print("\n--- DRAFT TEXT UNDER TEST ---")
        print(draft_copy)
        print("-----------------------------\n")

        submission = ContentSubmission(
            brand_id=brand.id,
            title="Q3 Press Release Draft",
            content_type="TEXT",
            extracted_text=draft_copy,
            creator_name="Alex Turner",
            intended_channel="Press Release",
            status="PENDING_REVIEW"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # 5. EXECUTE THE FULL INSPECTION ENGINE
        report = run_comprehensive_inspection(
            db=db,
            submission=submission,
            brand=brand
        )
        db.commit()
        db.refresh(report)

        print(f"[STEP 6] INSPECTION RESULTS:")
        print(f" -> Overall Adherence Score: {report.overall_score}/100 (Risk: {report.risk_level})")
        print(f" -> Engine Used: {report.engine_used}")
        print(f" -> Total Issues Detected: {len(report.findings)}")
        print(f"\nDETAILED FINDINGS BREAKDOWN:")
        for idx, issue in enumerate(report.findings, 1):
            print(f"\n [{idx}] Category: {issue.category} | Severity: {issue.severity}")
            print(f"     Flagged Text: \"{issue.flagged_text}\"")
            print(f"     Explanation: {issue.explanation}")
            print(f"     Suggested Fix: \"{issue.suggested_revision}\"")
            print(f"     Evidence / Citation: {issue.evidence}")

        print("\n" + "=" * 80)
        print(" DYNAMIC POLICY VERIFICATION SUMMARY:")
        print(f"  * Terminology violations caught dynamically: {any(f.category == 'TERMINOLOGY' for f in report.findings)}")
        print(f"  * Prohibited terms caught dynamically: {any('unhackable' in (f.flagged_text or '').lower() for f in report.findings)}")
        print(f"  * Competitor disparagement caught: {any(f.category == 'COMPETITOR' for f in report.findings)}")
        print(f"  * Claim contradiction caught (99.99% vs 99.95%): {any('99.99%' in (f.flagged_text or '') for f in report.findings)}")
        print(f"  * Reliability Principle applied (Needs Review): {any(f.category == 'CLAIM_GUARD' for f in report.findings)}")
        print("=" * 80)

    finally:
        db.close()

if __name__ == "__main__":
    run_end_to_end_policy_test()
