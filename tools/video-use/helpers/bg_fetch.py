#!/usr/bin/env python3
"""Fetch clean verse text from BibleGateway's rendered passage view.

Why this exists: there is no free NIV API. BibleGateway has no documented
verse API either, but its print-interface passage page renders clean,
copyright-noted text. This pulls the verse text out of that HTML.

  /passage/bcv/?version=NIV        -> 130KB JSON: the whole version's book/
                                      chapter structure + each chapter's opening
                                      line. A navigation index, NOT a verse API
                                      (it ignores passage params).
  /passage/?search=<ref>&version=<V>&interface=print
                                   -> the rendered passage. Verse text lives in
                                      <span class="text BOOK-C-V"> ... </span>,
                                      ending right before "Read full chapter".

LICENSING — read before using at scale:
  NIV is copyright Biblica/Zondervan. Their courtesy policy allows quoting up to
  500 verses without written permission, with attribution, provided the quotes
  are not a whole book and under 25% of the work. Sermon-overlay use (a handful
  of verses per message, attributed) sits inside that. BibleGateway's ToS
  discourages automated scraping — keep volume low (one sermon's refs), cache
  results, and always carry the copyright line this script emits.

Usage:
  bg_fetch.py "John 3:3" "Hebrews 4:12" "Psalm 34:8"      # refs as args
  bg_fetch.py --version KJV "Hebrews 4:12"                 # any BibleGateway version code
  bg_fetch.py --refs refs.txt -o verses.json              # one ref per line
"""
import argparse, json, re, sys, html, time, urllib.request
from urllib.parse import quote

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
ATTRIB = {
    "NIV": "Scripture quotations taken from the Holy Bible, New International Version®, NIV®. Copyright © 1973, 1978, 1984, 2011 by Biblica, Inc.® Used by permission. All rights reserved worldwide.",
}

def fetch(ref, version):
    url = f"https://www.biblegateway.com/passage/?search={quote(ref)}&version={version}&interface=print"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cookie": f"BGP_default_version={version}"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def clean(h):
    i = h.find("passage-text")
    if i < 0:
        return ""
    i = h.find(">", i) + 1
    b = h[i:i + 12000].split("Read full chapter")[0]
    b = re.sub(r"<sup\b[^>]*>.*?</sup>", "", b, flags=re.S)            # versenum, crossref, footnote
    b = re.sub(r"<h[1-6]\b[^>]*>.*?</h[1-6]>", "", b, flags=re.S)       # section headings
    b = re.sub(r"<span[^>]*chapternum[^>]*>.*?</span>", "", b, flags=re.S)
    b = re.sub(r"<span[^>]*small-caps[^>]*>(.*?)</span>", lambda m: m.group(1).upper(), b, flags=re.S)  # divine name -> LORD
    t = html.unescape(re.sub(r"<[^>]+>", " ", b))
    return re.sub(r"\s+", " ", t).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="*", help="references, e.g. \"1 Peter 1:22-23\"")
    ap.add_argument("--version", default="NIV", help="BibleGateway version code (NIV, KJV, ESV, NLT, ...)")
    ap.add_argument("--refs", dest="refs_file", help="file with one reference per line")
    ap.add_argument("-o", "--out", help="write JSON here instead of stdout")
    ap.add_argument("--delay", type=float, default=0.6, help="seconds between requests (be polite)")
    a = ap.parse_args()

    refs = list(a.refs)
    if a.refs_file:
        with open(a.refs_file, encoding="utf-8") as f:
            refs += [ln.strip() for ln in f if ln.strip()]
    if not refs:
        sys.exit("no references given")

    verses = []
    for n, ref in enumerate(refs):
        if n:
            time.sleep(a.delay)
        try:
            verses.append({"ref": ref, "translation": a.version, "text": clean(fetch(ref, a.version))})
        except Exception as e:
            verses.append({"ref": ref, "translation": a.version, "text": "", "error": repr(e)})

    result = {"translation": a.version,
              "attribution": ATTRIB.get(a.version, f"Scripture quotation: {a.version} via BibleGateway. Verify the version's license before redistribution."),
              "verses": verses}
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"wrote {len(verses)} verses -> {a.out}")
    else:
        print(payload)

if __name__ == "__main__":
    main()
