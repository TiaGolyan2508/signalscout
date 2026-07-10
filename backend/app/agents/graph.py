import os
import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from anthropic import Anthropic
from app.services.serper_client import search_companies, extract_domain
from app.services.hunter_client import find_contacts

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

AGGREGATOR_DOMAINS = {
    "ycombinator.com", "builtin.com", "topstartups.io", "reddit.com",
    "wellfound.com", "f6s.com", "crunchbase.com", "linkedin.com",
    "medium.com", "facebook.com", "instagram.com", "quora.com",
    "economictimes.indiatimes.com", "rockethub.com", "tuvoc.com"
}

MAX_COMPANIES = 5  # keeps Claude API usage safe/cheap per run


class PipelineState(TypedDict):
    query: str
    companies: List[dict]
    leads: List[dict]


# ---------- AGENT 1: SEARCH ----------
def search_node(state: PipelineState) -> PipelineState:
    results = search_companies(state["query"], num_results=10)
    companies = []
    for r in results:
        domain = extract_domain(r["link"])
        if domain and domain not in AGGREGATOR_DOMAINS:
            companies.append({
                "name": r["title"],
                "domain": domain,
                "snippet": r["snippet"]
            })
    state["companies"] = companies[:MAX_COMPANIES]
    return state


# ---------- AGENT 2: ENRICH ----------
def enrich_node(state: PipelineState) -> PipelineState:
    leads = []
    for company in state["companies"]:
        try:
            contacts = find_contacts(company["domain"], num_results=3)
        except Exception as e:
            contacts = []
        leads.append({
            "company_name": company["name"],
            "domain": company["domain"],
            "snippet": company["snippet"],
            "contacts": contacts
        })
    state["leads"] = leads
    return state


# ---------- AGENT 3: SCORE (Claude reasoning) ----------
def score_node(state: PipelineState) -> PipelineState:
    for lead in state["leads"]:
        prompt = f"""You are a B2B sales analyst scoring a lead's quality.

Company: {lead['company_name']}
Domain: {lead['domain']}
Description: {lead['snippet']}
Contacts found: {len(lead['contacts'])} (titles: {[c.get('title') for c in lead['contacts']]})

Score this lead from 1-100 based on: relevance to the search, seniority of contacts found, and how likely this is a real, active company (not a directory/article).
Respond ONLY in this exact JSON format, nothing else:
{{"score": <number>, "reasoning": "<one sentence why>"}}"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = response.content[0].text.strip()
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(result_text)
            lead["score"] = parsed.get("score")
            lead["score_reasoning"] = parsed.get("reasoning")
        except Exception as e:
            lead["score"] = None
            lead["score_reasoning"] = f"Scoring failed: {str(e)}"

    # Sort leads by score, highest first
    state["leads"] = sorted(
        state["leads"],
        key=lambda x: x.get("score") or 0,
        reverse=True
    )
    return state


# ---------- AGENT 4: PERSONALIZED OUTREACH ----------
def outreach_node(state: PipelineState) -> PipelineState:
    for lead in state["leads"]:
        if not lead["contacts"]:
            lead["outreach_message"] = None
            continue

        top_contact = lead["contacts"][0]
        prompt = f"""Write a short, personalized cold outreach email (max 80 words) to:

Name: {top_contact.get('first_name')} {top_contact.get('last_name')}
Title: {top_contact.get('title')}
Company: {lead['company_name']}
Company context: {lead['snippet']}

The email should be warm, specific to their company/role, and end with a soft call-to-action for a 15-min call. No generic filler. Sign off as "Alex from SignalScout."
Respond with ONLY the email body, no subject line, no preamble."""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            lead["outreach_message"] = response.content[0].text.strip()
        except Exception as e:
            lead["outreach_message"] = f"Generation failed: {str(e)}"

    return state


# ---------- BUILD GRAPH ----------
def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("search", search_node)
    graph.add_node("enrich", enrich_node)
    graph.add_node("score", score_node)
    graph.add_node("outreach", outreach_node)

    graph.set_entry_point("search")
    graph.add_edge("search", "enrich")
    graph.add_edge("enrich", "score")
    graph.add_edge("score", "outreach")
    graph.add_edge("outreach", END)

    return graph.compile()


pipeline = build_pipeline()


def run_pipeline(query: str):
    result = pipeline.invoke({"query": query, "companies": [], "leads": []})
    return result["leads"]