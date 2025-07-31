import requests
import csv
from typing import List, Dict
from xml.etree import ElementTree as ET

def search_pubmed(query: str, max_results: int = 10, debug: bool = False) -> List[str]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    response = requests.get(url, params=params)
    data = response.json()
    if debug:
        print("📦 DEBUG (esearch):", data)
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_details(pubmed_ids: List[str], debug: bool = False) -> List[dict]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    response = requests.get(url, params=params)
    if debug:
        print("📦 DEBUG (efetch):", response.text[:500], "...\n")

    root = ET.fromstring(response.content)

    results = []
    for article in root.findall(".//PubmedArticle"):
        pubmed_id = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        pub_date = article.findtext(".//PubDate/Year") or "Unknown"

        authors = article.findall(".//Author")
        non_academic_authors = []
        company_affiliations = []
        email = None

        for author in authors:
            aff = author.findtext(".//AffiliationInfo/Affiliation")
            lastname = author.findtext("LastName") or ""
            firstname = author.findtext("ForeName") or ""

            if aff:
                if not any(word in aff.lower() for word in ["university", "college", "school", "institute", "hospital"]):
                    non_academic_authors.append(f"{firstname} {lastname}")
                    company_affiliations.append(aff)

                if "@" in aff and not email:
                    email = aff.split()[-1] if "@" in aff.split()[-1] else None

        results.append({
            "PubmedID": pubmed_id,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Author(s)": "; ".join(non_academic_authors),
            "Company Affiliation(s)": "; ".join(company_affiliations),
            "Corresponding Author Email": email or "Not found"
        })

    return results

def save_to_csv(data: List[dict], filename: str) -> None:
    if not data:
        print("❗ No data to save.")
        return

    fieldnames = list(data[0].keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Saved {len(data)} records to {filename}")
