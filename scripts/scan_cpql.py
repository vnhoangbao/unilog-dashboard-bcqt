import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd

SHEET_ID = "1F-W0BbBqzKKr-wCXZJBswW-afBpYkTxvvtHT6AdL77I"
GID      = "353917314"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
df_raw = pd.read_csv(url, low_memory=False)

# Keep relevant cols
STT_COL = "STT"
NOI_COL = "Nội dung_Stt"
DT_COL  = "Ngày tháng_datetime"
TT_COL  = "Số thực tế"
KH_COL  = "Số kế hoạch"
BU_COL  = "Grouped_BU"

df = df_raw[[STT_COL, NOI_COL, DT_COL, TT_COL, KH_COL, BU_COL]].copy()
df[STT_COL] = pd.to_numeric(df[STT_COL].astype(str).str.strip(), errors="coerce")
for col in [TT_COL, KH_COL]:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",","",regex=False).str.strip(),
        errors="coerce"
    ).fillna(0)
df = df.dropna(subset=[STT_COL, DT_COL])

months = sorted(df[DT_COL].unique())
first_m = months[0]
print(f"First month: {first_m}")
print(f"All months: {months}")

# Check STT 82 and 151 by month
print("\n=== STT 82 (Chi phí QLDN) per month ===")
s82 = df[df[STT_COL] == 82].groupby(DT_COL)[[TT_COL, KH_COL]].sum()
print(s82.to_string())

print("\n=== STT 151 (Phân bổ CP gián tiếp) per month ===")
s151 = df[df[STT_COL] == 151].groupby(DT_COL)[[TT_COL, KH_COL]].sum()
print(s151.to_string())

print("\n=== STT 82 + 151 combined per month ===")
combined = s82.add(s151, fill_value=0)
print(combined.to_string())

# Check STT 72 (LN Gộp) KH
print("\n=== STT 72 (LN Gộp) KH per month ===")
s72 = df[df[STT_COL] == 72].groupby(DT_COL)[[TT_COL, KH_COL]].sum()
print(s72.to_string())

# Check STT 146 (LNHDKD) - verify KH=0
print("\n=== STT 146 (LNHDKD) per month ===")
s146 = df[df[STT_COL] == 146].groupby(DT_COL)[[TT_COL, KH_COL]].sum()
print(s146.to_string())

# Derived LNHDKD_KH = LN_Gop_KH - CPQL_KH
print("\n=== Derived LNHDKD_KH = STT72_KH - (STT82+STT151)_KH ===")
for m in months:
    gp_kh = s72.loc[m, KH_COL] if m in s72.index else 0
    cp_kh = (s82.loc[m, KH_COL] if m in s82.index else 0) + \
            (s151.loc[m, KH_COL] if m in s151.index else 0)
    lnhd_kh = gp_kh - cp_kh
    print(f"  {m}: GP_KH={gp_kh/1e9:.2f}T  CP_KH={cp_kh/1e9:.2f}T  LNHD_KH={lnhd_kh/1e9:.2f}T")

# Check CN_TIEN format in cong_no sheet
print("\n=== Checking data_CongNo THÀNH TIỀN format ===")
url_cn = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2111484222"
df_cn = pd.read_csv(url_cn, low_memory=False)
print("Cols:", list(df_cn.columns))
if "THÀNH TIỀN" in df_cn.columns:
    sample = df_cn["THÀNH TIỀN"].dropna().head(5)
    print("Sample values:", sample.tolist())
    print("dtypes:", df_cn["THÀNH TIỀN"].dtype)
