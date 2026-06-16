import urllib.request
import io
import pandas as pd
import sys

SHEET_ID = "1F-W0BbBqzKKr-wCXZJBswW-afBpYkTxvvtHT6AdL77I"

sheets = {
    "target": "1974781100",
    "detail": "1080595888",
}

out = []
for name, gid in sheets.items():
    url = (
        "https://docs.google.com/spreadsheets/d/"
        + SHEET_ID
        + "/export?format=csv&gid="
        + gid
    )
    out.append("\n=== " + name + " (gid=" + gid + ") ===")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
        df = pd.read_csv(io.BytesIO(raw), nrows=3, encoding="utf-8-sig")
        out.append("Columns (" + str(len(df.columns)) + " total):")
        for i, c in enumerate(df.columns, 1):
            val = str(df[c].iloc[0])[:50] if len(df) > 0 else "?"
            line = "  " + str(i) + ". " + c + " => " + val
            out.append(line)
    except Exception as e:
        out.append("ERROR: " + str(e))

out.append("\nDone.")
result = "\n".join(out)

# Write to file to avoid encoding issues in console
with open("scripts/cols_output.txt", "w", encoding="utf-8") as f:
    f.write(result)
print("Written to scripts/cols_output.txt")
