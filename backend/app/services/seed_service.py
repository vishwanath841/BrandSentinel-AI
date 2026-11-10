from sqlalchemy.orm import Session
from app.models.brand import BrandProfile, BrandRule, ApprovedFact
from app.models.submission import ContentSubmission
from app.services.inspection_service import run_comprehensive_inspection

def seed_database(db: Session):
    """Seed sample brand profiles, rules, and approved facts if empty."""
    existing_brand = db.query(BrandProfile).first()
    if existing_brand:
        return

    # 1. ApexCloud Enterprise
    apex = BrandProfile(
        name="ApexCloud Enterprise",
        slug="apexcloud",
        industry="Cloud Infrastructure & Enterprise SaaS",
        tagline="Engineered for Uncompromising Uptime",
        mission="Empowering global enterprises with high-resilience, verifiable cloud data architecture.",
        target_audience="CTOs, Enterprise Architects, and DevOps Engineering Leads",
        primary_color="#1E3A8A",
        secondary_color="#0284C7",
        accent_color="#10B981",
        background_color="#F8FAFC",
        text_color="#0F172A",
        color_tolerance=45.0
    )
    apex.voice_traits = ["Authoritative", "Data-driven", "Empathetic", "Direct", "Precise"]
    apex.avoided_tones = ["Aggressive", "Hyperbolic", "Overly informal", "Disparaging"]
    db.add(apex)
    db.flush()

    # ApexCloud Rules
    rules_data = [
        {
            "category": "TERMINOLOGY",
            "rule_name": "Approved Product Nomenclature",
            "description": "Always use approved cloud platform nomenclature.",
            "preferred_term": "ApexCloud Data Fabric",
            "forbidden_terms": ["magic cloud", "infinite cloud", "the backend tool"],
            "severity": "HIGH",
            "rationale": "Clear, professional product branding differentiates our multi-tenant enterprise tier."
        },
        {
            "category": "TERMINOLOGY",
            "rule_name": "Corporate Jargon Restriction",
            "description": "Avoid buzzwords without concrete technical meaning.",
            "preferred_term": "integrated architecture",
            "forbidden_terms": ["synergy", "synergistic", "game-changing"],
            "severity": "MEDIUM",
            "rationale": "Engineers and enterprise buyers distrust vague buzzwords."
        },
        {
            "category": "LEGAL",
            "rule_name": "No Absolute Reliability Guarantees",
            "description": "Never claim 100% bug-free or unbreakable availability.",
            "preferred_term": "99.99% uptime SLA backed by financial credits",
            "forbidden_terms": ["100% bug-free", "guaranteed zero downtime", "unbreakable platform"],
            "severity": "CRITICAL",
            "rationale": "Legal liability: Absolute guarantees conflict with customer contractual SLAs."
        },
        {
            "category": "COMPETITOR",
            "rule_name": "Competitor Disparagement Policy",
            "description": "Do not insult or use derogatory phrasing toward competitors.",
            "preferred_term": "outperforms legacy cloud alternatives",
            "forbidden_terms": ["AWS is garbage", "Azure is terrible", "clueless competitors", "rip off"],
            "severity": "CRITICAL",
            "rationale": "Corporate integrity policy requires strictly objective, benchmark-focused comparisons."
        },
        {
            "category": "STYLE",
            "rule_name": "Casual Slang Restriction",
            "description": "Avoid casual internet slang in enterprise whitepapers and announcements.",
            "preferred_term": "streamlined implementation",
            "forbidden_terms": ["gonna", "wanna", "tbh", "fire af", "bussin"],
            "severity": "MEDIUM",
            "rationale": "Maintains an authoritative enterprise executive register."
        }
    ]

    for r in rules_data:
        rule = BrandRule(
            brand_id=apex.id,
            category=r["category"],
            rule_name=r["rule_name"],
            description=r["description"],
            preferred_term=r["preferred_term"],
            severity=r["severity"],
            rationale=r["rationale"],
            is_active=True
        )
        rule.forbidden_terms = r["forbidden_terms"]
        db.add(rule)

    # ApexCloud Approved Facts (ClaimGuard KB)
    facts_data = [
        {
            "claim_topic": "SLA & Uptime Guarantee",
            "approved_text": "ApexCloud guarantees 99.99% monthly uptime SLA backed by automated financial service credits.",
            "metrics": {"uptime": "99.99%", "credit_model": "automated"},
            "verification_source": "Enterprise Master Service Agreement 2024 & SOC 2 Type II Report"
        },
        {
            "claim_topic": "Customer Enterprise Scale",
            "approved_text": "Over 14,000 enterprise customers across 45 countries operate mission-critical workloads on ApexCloud.",
            "metrics": {"customers": "14,000+", "countries": 45},
            "verification_source": "Q3 2024 Audited Financial Investor Disclosure"
        },
        {
            "claim_topic": "Security & Regulatory Compliance",
            "approved_text": "ApexCloud is certified ISO 27001, SOC 2 Type II, HIPAA compliant, and GDPR verified.",
            "metrics": {"certifications": ["ISO 27001", "SOC 2 Type II", "HIPAA", "GDPR"]},
            "verification_source": "Annual Independent Security Compliance Audit 2024"
        },
        {
            "claim_topic": "Performance Benchmark Latency",
            "approved_text": "Delivers sub-15ms p99 query latency across globally distributed multi-region clusters.",
            "metrics": {"latency_p99": "sub-15ms"},
            "verification_source": "2024 Third-Party Cloud Benchmark Whitepaper"
        }
    ]

    for f in facts_data:
        fact = ApprovedFact(
            brand_id=apex.id,
            claim_topic=f["claim_topic"],
            approved_text=f["approved_text"],
            verification_source=f["verification_source"],
            last_verified_date="2024-10-15",
            is_active=True
        )
        fact.metrics = f["metrics"]
        db.add(fact)

    # 2. EcoPulse Organics
    eco = BrandProfile(
        name="EcoPulse Organics",
        slug="ecopulse",
        industry="Sustainable Consumer Wellness & Nutrition",
        tagline="Nourishing Life in Harmony with the Earth",
        mission="Providing regenerative, 100% plant-based wellness solutions that restore both human vitality and soil biodiversity.",
        target_audience="Health-conscious families and eco-ethical consumers",
        primary_color="#15803D",
        secondary_color="#84CC16",
        accent_color="#EAB308",
        background_color="#FDFBF7",
        text_color="#1C1917",
        color_tolerance=50.0
    )
    eco.voice_traits = ["Warm", "Transparent", "Inspiring", "Approachable"]
    eco.avoided_tones = ["Aggressive", "Hyperbolic", "Slang"]
    db.add(eco)
    db.flush()

    eco_rules = [
        {
            "category": "LEGAL",
            "rule_name": "Medical Treatment Claims Prohibited",
            "description": "Never claim our products cure, treat, or prevent clinical diseases.",
            "preferred_term": "supports holistic daily wellness",
            "forbidden_terms": ["cures all diseases", "miracle detox", "cancels illness"],
            "severity": "CRITICAL",
            "rationale": "FDA compliance: Dietary supplements cannot make clinical cure claims."
        },
        {
            "category": "MESSAGING",
            "rule_name": "Authentic Sustainability Terminology",
            "description": "Avoid unscientific or misleading 'chemical free' phrasing.",
            "preferred_term": "100% certified organic ingredients without synthetic pesticides",
            "forbidden_terms": ["100% chemical free", "zero chemicals", "magic elixir"],
            "severity": "HIGH",
            "rationale": "Water and air are chemicals; 'chemical-free' is scientifically misleading."
        }
    ]
    for r in eco_rules:
        rule = BrandRule(
            brand_id=eco.id,
            category=r["category"],
            rule_name=r["rule_name"],
            description=r["description"],
            preferred_term=r["preferred_term"],
            severity=r["severity"],
            rationale=r["rationale"],
            is_active=True
        )
        rule.forbidden_terms = r["forbidden_terms"]
        db.add(rule)

    eco_facts = [
        {
            "claim_topic": "Organic Certification & Packaging",
            "approved_text": "EcoPulse is USDA Certified Organic, Non-GMO Project Verified, with 100% compostable plant-based packaging.",
            "metrics": {"certifications": ["USDA Organic", "Non-GMO Project Verified"]},
            "verification_source": "USDA Organic Certificate #94821"
        },
        {
            "claim_topic": "Regenerative Farm Sourcing",
            "approved_text": "100% of our botanicals are directly sourced from over 250 family-owned regenerative farms.",
            "metrics": {"farms": "250+"},
            "verification_source": "Regenerative Agriculture Partner Registry 2024"
        }
    ]
    for f in eco_facts:
        fact = ApprovedFact(
            brand_id=eco.id,
            claim_topic=f["claim_topic"],
            approved_text=f["approved_text"],
            verification_source=f["verification_source"],
            last_verified_date="2024-11-01",
            is_active=True
        )
        fact.metrics = f["metrics"]
        db.add(fact)

    db.commit()

    # Pre-seed realistic sample submissions for demo
    sample_sub = ContentSubmission(
        brand_id=apex.id,
        title="Q4 Product Launch Press Draft",
        content_type="TEXT",
        creator_name="Alex Chen (Marketing Lead)",
        intended_channel="Global Press Release & TechCrunch",
        extracted_text=(
            "We are thrilled to unveil our new magic cloud platform! "
            "Unlike legacy solutions where AWS is garbage, ApexCloud guarantees 100% bug-free performance "
            "with guaranteed zero downtime for every customer. "
            "Our insane synergistic architecture delivers sub-15ms p99 query latency, "
            "trusted by over 14,000 enterprise customers across 45 countries. "
            "We are gonna crush our rivals and ensure your data is 100% secure with ISO 27001 certification."
        ),
        status="PENDING_REVIEW"
    )
    db.add(sample_sub)
    db.commit()
    db.refresh(sample_sub)

    # Run inspection for this sample submission
    run_comprehensive_inspection(db, sample_sub, apex)

