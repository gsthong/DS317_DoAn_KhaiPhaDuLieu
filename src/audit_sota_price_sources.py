"""Save primary-source metadata and HTML tables for the price forecasting review.

This is a source audit, not a model benchmark. Uses requests/bs4 already installed
in the workspace; never downloads checkpoints or installs model dependencies.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "reports" / "sota_price_2023_2026" / "evidence"
SOURCES = {
    "tide_paper": "https://arxiv.org/html/2304.08424v5",
    "tsmixer_paper": "https://arxiv.org/html/2303.06053v5",
    "itransformer_paper": "https://arxiv.org/html/2310.06625v4",
    "timemixer_paper": "https://arxiv.org/html/2405.14616v1",
    "timexer_paper": "https://arxiv.org/html/2402.19072v3",
    "chronos2_paper": "https://arxiv.org/html/2510.15821v1",
    "moirai2_paper": "https://arxiv.org/html/2511.11698v3",
    "tabpfn_ts_paper": "https://arxiv.org/html/2501.02945v4",
    "timesfm3_release": "https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/",
    "tirex2_paper": "https://arxiv.org/html/2607.01204v1",
    "tide_code": "https://raw.githubusercontent.com/google-research/google-research/master/tide/README.md",
    "itransformer_code": "https://raw.githubusercontent.com/thuml/iTransformer/main/README.md",
    "tsmixer_code": "https://raw.githubusercontent.com/google-research/google-research/master/tsmixer/README.md",
    "timexer_code": "https://raw.githubusercontent.com/thuml/TimeXer/main/README.md",
    "timemixer_code": "https://raw.githubusercontent.com/kwuking/TimeMixer/main/README.md",
    "chronos2_code": "https://raw.githubusercontent.com/amazon-science/chronos-forecasting/main/README.md",
    "moirai2_code": "https://raw.githubusercontent.com/SalesforceAIResearch/uni2ts/main/README.md",
    "tabpfn_ts_code": "https://raw.githubusercontent.com/PriorLabs/tabpfn-time-series/main/README.md",
    "timesfm3_code": "https://raw.githubusercontent.com/google-research/timesfm/master/README.md",
    "timesfm3_card": "https://huggingface.co/google/timesfm-3.0-pytorch/raw/main/README.md",
    "tirex2_code": "https://raw.githubusercontent.com/NX-AI/tirex-2/main/README.md",
}


def fetch_source(item):
    name, url = item
    record = {"id": name, "url": url, "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    try:
        response = requests.get(url, timeout=55, headers={"User-Agent": "DS317-academic-source-audit/1.0"})
        record["status_code"] = response.status_code
        response.raise_for_status()
        record["sha256"] = hashlib.sha256(response.content).hexdigest()
        soup = BeautifulSoup(response.content, "html.parser")
        if "Verifying your browser" in soup.get_text():
            raise requests.RequestException("Browser verification page, not verified source content")
        tables = []
        for table in soup.select("figure.ltx_table"):
            caption = table.find("figcaption")
            rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                    for row in table.find_all("tr")]
            tables.append({"id": table.get("id"), "caption": caption.get_text(" ", strip=True) if caption else "", "rows": rows})
        record["tables"] = tables
        text = response.text if "raw." in url or "/raw/" in url else soup.get_text("\n", strip=True)
        (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
        (OUT / f"{name}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record
    except requests.RequestException as exc:
        record["error"] = str(exc)
        return record


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        records = list(pool.map(fetch_source, SOURCES.items()))
    manifest = {"purpose": "Primary-source audit, NOT model execution", "review_cutoff": "2026-11-06", "sources": records}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for record in records:
        print(record["id"], record.get("status_code"), "tables", len(record.get("tables", [])), record.get("error", ""))


if __name__ == "__main__":
    main()