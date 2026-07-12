SENIOR_KEYWORDS = [
    "founder", "co-founder", "ceo", "cto", "coo", "cfo",
    "chief", "vp", "vice president", "director", "head of", "president"
]


def score_lead(lead: dict) -> dict:
    """
    Rule-based lead scoring (0-100), fully transparent and explainable.
    Factors: number of contacts found, seniority of contacts, Hunter's
    confidence score on those emails.
    """
    contacts = lead.get("contacts", [])
    reasons = []
    score = 0

    # Factor 1: contact count (up to 30 points)
    contact_points = min(len(contacts), 3) * 10
    score += contact_points
    if contacts:
        reasons.append(f"{len(contacts)} contact(s) found (+{contact_points})")
    else:
        reasons.append("No contacts found (+0)")

    # Factor 2: seniority of titles found (up to 40 points)
    senior_hits = 0
    for c in contacts:
        title = (c.get("title") or "").lower()
        if any(keyword in title for keyword in SENIOR_KEYWORDS):
            senior_hits += 1

    seniority_points = min(senior_hits, 2) * 20
    score += seniority_points
    if senior_hits:
        reasons.append(f"{senior_hits} senior-level contact(s) (+{seniority_points})")
    else:
        reasons.append("No senior-level titles detected (+0)")

    # Factor 3: average email confidence from Hunter (up to 30 points)
    confidences = [c.get("confidence") for c in contacts if c.get("confidence") is not None]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        confidence_points = round((avg_confidence / 100) * 30)
        score += confidence_points
        reasons.append(f"Avg email confidence {avg_confidence:.0f}% (+{confidence_points})")
    else:
        reasons.append("No confidence data (+0)")

    lead["score"] = min(score, 100)
    lead["score_reasoning"] = "; ".join(reasons)
    return lead


def score_node(state: dict) -> dict:
    """LangGraph node: scores every lead and sorts highest first"""
    state["leads"] = [score_lead(lead) for lead in state["leads"]]
    state["leads"] = sorted(state["leads"], key=lambda x: x.get("score", 0), reverse=True)
    return state
