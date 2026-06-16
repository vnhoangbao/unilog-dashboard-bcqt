"""
scripts/discover_columns.py
===========================
Khám phá tên cột thực tế của từng Google Sheet tab dùng gid.

Cách dùng:
    python scripts/discover_columns.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from config import SHEET_ID, SHEET_GIDS


def sheet_url(gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"


def discover_sheet(key: str, gid: str):
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"SHEET key='{key}'  gid={gid}")
    print(sep)
    url = sheet_url(gid)
    print(f"URL: {url}")
    try:
        df = pd.read_csv(url, nrows=5, low_memory=False)
        print(f"\nDoc thanh cong — {len(df.columns)} cot, {len(df)} dong mau")
        print("\nDANH SACH COT:")
        for i, col in enumerate(df.columns, 1):
            sample = str(df[col].iloc[0]) if len(df) > 0 else "—"
            if len(sample) > 40:
                sample = sample[:40] + "..."
            print(f"  {i:>3}. '{col}'  (mau: {sample})")
        print("\n5 DONG DAU:")
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(df.to_string(max_colwidth=25))
    except Exception as e:
        print(f"\nLOI: {e}")
        print("   -> Kiem tra Google Sheet da share 'Anyone with the link' chua?")


if __name__ == "__main__":
    print("KHAM PHA COT GOOGLE SHEETS — U&I Logistics BCQT")
    print(f"Sheet ID: {SHEET_ID}")

    for key, gid in SHEET_GIDS.items():
        discover_sheet(key, gid)

    print(f"\n{'=' * 60}")
    print("XONG. Copy ten cot dung vao config.py")
    print(f"{'=' * 60}\n")
