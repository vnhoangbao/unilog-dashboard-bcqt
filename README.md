# Unilog Dashboard BCQT Mobile

Dashboard Streamlit đọc real-time từ Google Sheets — U&I Logistics

## Cài đặt nhanh (5 bước)

```bash
# 1. Vào thư mục project
cd "Unilog-Dashboard BCQT mobile"

# 2. Cài Python packages
pip install -r requirements.txt

# 3. Đảm bảo Google Sheet đã share "Anyone with the link can view"

# 4. Khám phá tên cột thực tế (chỉ cần chạy 1 lần đầu)
python scripts/discover_columns.py

# 5. Chỉnh config.py nếu tên cột sai, rồi chạy app
streamlit run app.py
```

## Deploy lên Streamlit Cloud (miễn phí)

1. Push folder này lên GitHub
2. Vào https://share.streamlit.io → New app
3. Chọn repo → file `app.py` → Deploy

## Cấu trúc project

```
app.py                  ← Chạy cái này
config.py               ← Tên cột, màu sắc, Sheet ID
data_loader.py          ← Đọc Google Sheets
utils.py                ← Hàm format
modules/
  p1_hieu_qua_hd.py    ← Trang 1
  p2_cp_gian_tiep.py   ← Trang 2
  p3_cong_no.py        ← Trang 3
  p4_cong_viec.py      ← Trang 4
scripts/
  discover_columns.py  ← Chạy đầu tiên để xem tên cột
```
