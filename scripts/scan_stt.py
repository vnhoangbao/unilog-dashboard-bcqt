import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd

SHEET_ID = "1F-W0BbBqzKKr-wCXZJBswW-afBpYkTxvvtHT6AdL77I"
GID      = "353917314"

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
df  = pd.read_csv(url)

print("Columns:", list(df.columns))

STT_COL = "STT"
NOI_COL = "Nội dung_Stt"
KH_COL  = "Số kế hoạch"
DT_COL  = "Ngày tháng_datetime"
BU_COL  = "Grouped_BU"

# All unique STT + NỘI DUNG
stt_noi = df[[STT_COL, NOI_COL]].drop_duplicates().dropna(subset=[STT_COL])
stt_noi[STT_COL] = pd.to_numeric(stt_noi[STT_COL], errors="coerce")
stt_noi = stt_noi.dropna(subset=[STT_COL]).sort_values(STT_COL)

print("\n=== TẤT CẢ STT + NỘI DUNG ===")
print(stt_noi.to_string(index=False))

# STT 140-170 chi tiết
print("\n=== STT 130–170 (KH area) ===")
sub = stt_noi[(stt_noi[STT_COL] >= 130) & (stt_noi[STT_COL] <= 170)]
print(sub.to_string(index=False))

# Kiểm tra STT nào có KH != 0
print("\n=== STT có KH > 0 ===")
df[STT_COL] = pd.to_numeric(df[STT_COL], errors="coerce")
df[KH_COL]  = pd.to_numeric(df[KH_COL],  errors="coerce")
has_kh = df[df[KH_COL] > 0][[STT_COL, NOI_COL, KH_COL]].drop_duplicates(subset=[STT_COL])
has_kh = has_kh.sort_values(STT_COL)
print(has_kh.to_string(index=False))

# STT 148-165 NỘI DUNG
print("\n=== STT 145–165 ===")
rng = stt_noi[(stt_noi[STT_COL] >= 145) & (stt_noi[STT_COL] <= 165)]
print(rng.to_string(index=False))
