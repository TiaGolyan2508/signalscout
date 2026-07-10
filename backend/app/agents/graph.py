from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from app.services.serper_client import search_companies, extract_domain
from app.services.hunter_client import find_contacts

AGGREGATOR_DOMAINS = {
    "ycombinator.com", "builtin.com", "topstartups.io", "reddit.com",
    "wellfound.com", "f6s.com", "crunchbase.com", "linkedin.com",
    "medium.com", "facebook.com", "instagram.com", "quora.com",
    "economictimes.indiatimes.com", "rockethub.com", "tuvoc.com",
    "naukri.com", "youtube.com", "wikipedia.org", "pwc.com", "startupindia.gov.in"
}

MAX_COMPANIES = 5


class PipelineState(TypedDict):
    query: str
    companies: List[dict]
    leads: List[dict]


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


def enrich_node(state: PipelineState) -> PipelineState:
    leads = []
    for company in state["companies"]:
        try:
            contacts = find_contacts(company["domain"], num_results=3)
        except Exception:
            contacts = []
        leads.append({
            "company_name": company["name"],
            "domain": company["domain"],
            "snippet": company["snippet"],
            "contacts": contacts
        })
    state["leads"] = leads
    return state


def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("search", search_node)
    graph.add_node("enrich", enrich_node)

    graph.set_entry_point("search")
    graph.add_edge("search", "enrich")
    graph.add_edge("enrich", END)

    return graph.compile()


pipeline = build_pipeline()


def run_pipeline(query: str):
    result = pipeline.invoke({"query": query, "companies": [], "leads": []})
    return result["leads"]
