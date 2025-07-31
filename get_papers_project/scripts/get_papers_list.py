import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # ✅ Add this

import argparse
from get_papers.core import search_pubmed, fetch_details, save_to_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers by query")
    parser.add_argument("query", help="Search query for PubMed")
    parser.add_argument("--file", "-f", help="Filename to save output CSV")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()

    print(f"🔍 Searching PubMed for: {args.query}")
    ids = search_pubmed(args.query, debug=args.debug)

    if not ids:
        print("❌ No paper IDs found for your query.")
        return

    print(f"📄 Found {len(ids)} paper(s). Fetching details...")
    data = fetch_details(ids, debug=args.debug)

    if not data:
        print("❌ No non-academic authors found in the papers.")
        return

    if args.file:
        save_to_csv(data, args.file)
    else:
        for paper in data:
            print("\n🧪 Paper Info:")
            for key, value in paper.items():
                print(f"{key}: {value}")

if __name__ == "__main__":
    main()
