"""
Pull investigation metadata and files from NASA PSI (Physical Sciences Informatics).

PSI has no documented API, but its own web app reads public JSON from
https://psi.nasa.gov/geode-py/ws . Everything we touch here is public and CC0.

usage:
    python scripts/psi_fetch.py catalog --ids 1-200        # find combustion investigations
    python scripts/psi_fetch.py files                      # list every file into data/catalog/psi_files.csv
    python scripts/psi_fetch.py download --max-mb 8        # tables + small docs into data/raw/psi/
"""
import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "raw" / "psi" / "meta"
RAW_DIR = ROOT / "data" / "raw" / "psi"
CAT_DIR = ROOT / "data" / "catalog"
API = "https://psi.nasa.gov/geode-py/ws"
HEADERS = {"User-Agent": "Errorists-SpaceApps-2026/0.1"}

# categories worth pulling automatically (small, text-like, useful for evidence)
WANTED = ("Experimental table", "Publications", "Engineering Documents", "Final Report",
          "Reports", "Representative Image", "Processed Data", "Technical", "Science Requirements",
          "Science Documents", "Analyzed Data", "Reference Data", "metadata")


def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa
            if i == retries - 1:
                raise
            time.sleep(2 * (i + 1))


def parse_ids(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def load_meta(psi_id, refresh=False):
    f = META_DIR / f"{psi_id}.json"
    if f.exists() and not refresh:
        return json.loads(f.read_text())
    raw = get(f"{API}/repo/investigations/{psi_id}")
    data = json.loads(raw)
    META_DIR.mkdir(parents=True, exist_ok=True)
    f.write_bytes(raw)
    return data


def category_of(item):
    p = item.get("remote_path") or item.get("s3_path") or ""
    parts = [x for x in p.split("/") if x]
    # /Home/psi-data/PSI-98/<Category>/<file>
    for i, x in enumerate(parts):
        if x.startswith("PSI-") and i + 1 < len(parts) - 1:
            return parts[i + 1]
    return "Other"


def cmd_catalog(args):
    rows = []
    for n in parse_ids(args.ids):
        pid = f"PSI-{n}"
        try:
            d = load_meta(pid, args.refresh)
        except Exception as e:
            print(f"{pid}: skip ({e.__class__.__name__})")
            continue
        area = " ".join(str(d.get(k) or "") for k in ("researchArea", "subResearchArea"))
        if not d or "ombustion" not in area:
            # keep metadata only for combustion work
            (META_DIR / f"{pid}.json").unlink(missing_ok=True)
            continue
        rows.append({
            "psi_id": pid,
            "acronym": d.get("investigationAcronym") or "",
            "title": (d.get("title") or d.get("projectTitle") or "").strip(),
            "research_area": d.get("researchArea") or "",
            "sub_area": d.get("subResearchArea") or "",
            "hardware": (d.get("experimentHardware") or "").strip(),
            "start": d.get("investigationStartDate") or "",
            "end": d.get("investigationEndDate") or "",
            "license": d.get("licenseName") or "",
            "total_bytes": d.get("totalFileSize") or 0,
            "n_files": len(d.get("added") or []),
            "n_tables": len(d.get("experimentalTable") or []),
            "n_publications": len(d.get("publications") or []),
            "url": f"https://psi.nasa.gov/physci/repo/data/{pid}",
        })
        print(f"{pid}: {rows[-1]['acronym']} | {rows[-1]['sub_area']}")
        time.sleep(0.3)
    CAT_DIR.mkdir(parents=True, exist_ok=True)
    out = CAT_DIR / "psi_investigations.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} combustion investigations -> {out.relative_to(ROOT)}")


def all_metas():
    for f in sorted(META_DIR.glob("PSI-*.json"), key=lambda p: int(p.stem.split("-")[1])):
        yield f.stem, json.loads(f.read_text())


def cmd_files(args):
    rows = []
    for pid, d in all_metas():
        seen = set()
        items = list(d.get("added") or []) + list(d.get("experimentalTable") or []) + list(d.get("images") or [])
        for it in items:
            name = it.get("file_name")
            if not name or name in seen:
                continue
            seen.add(name)
            rows.append({
                "psi_id": pid,
                "acronym": d.get("investigationAcronym") or "",
                "category": category_of(it) if it.get("remote_path") or it.get("s3_path") else "Experimental table",
                "file_name": name,
                "size_mb": round((it.get("file_size") or 0) / 1e6, 3),
                "version": it.get("version") or 1,
                "restricted": bool(it.get("restricted")),
            })
    CAT_DIR.mkdir(parents=True, exist_ok=True)
    out = CAT_DIR / "psi_files.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} files listed -> {out.relative_to(ROOT)}")


def download_one(pid, name, version, dest):
    q = urllib.parse.urlencode({"file": name, "version": version, "redirect": "false"})
    link = get(f"{API}/studies/{pid}/download?{q}").decode().strip().strip('"')
    host = urllib.parse.urlparse(link).netloc
    if not host.endswith("amazonaws.com") and not host.endswith("nasa.gov"):
        raise RuntimeError(f"unexpected host {host}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(get(link))


def cmd_download(args):
    src = CAT_DIR / "psi_files.csv"
    if not src.exists():
        sys.exit("run `files` first")
    rows = list(csv.DictReader(src.open()))
    only = set(args.only.split(",")) if args.only else None
    log = []
    for r in rows:
        if only and r["psi_id"] not in only:
            continue
        if r["restricted"] == "True":
            continue
        size = float(r["size_mb"])
        is_table = r["category"] == "Experimental table"
        wanted = is_table or any(w.lower() in r["category"].lower() for w in WANTED)
        if not wanted or (size > args.max_mb and not is_table):
            continue
        dest = RAW_DIR / r["psi_id"] / r["category"] / r["file_name"]
        if dest.exists() and dest.stat().st_size > 0:
            continue
        try:
            download_one(r["psi_id"], r["file_name"], r["version"], dest)
            log.append((r["psi_id"], r["file_name"], "ok"))
            print(f"ok   {r['psi_id']}  {r['file_name']}  ({size} MB)")
        except Exception as e:
            log.append((r["psi_id"], r["file_name"], f"fail: {e}"))
            print(f"FAIL {r['psi_id']}  {r['file_name']}: {e}")
        time.sleep(0.2)
    with (CAT_DIR / "download_log.csv").open("a", newline="") as fh:
        csv.writer(fh).writerows(log)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("catalog")
    c.add_argument("--ids", default="1-200")
    c.add_argument("--refresh", action="store_true")
    sub.add_parser("files")
    d = sub.add_parser("download")
    d.add_argument("--max-mb", type=float, default=8.0)
    d.add_argument("--only", default="")
    args = ap.parse_args()
    {"catalog": cmd_catalog, "files": cmd_files, "download": cmd_download}[args.cmd](args)


if __name__ == "__main__":
    main()
