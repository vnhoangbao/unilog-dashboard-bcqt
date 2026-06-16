# CLAUDE.md — Unilog Dashboard BCQT Mobile

## Mục đích dự án
Dashboard Streamlit đọc real-time từ Google Sheets của Công ty U&I Logistics,
phục vụ báo cáo BCQT cho ban lãnh đạo xem trên mobile và PC.

## Kiến trúc tổng thể
```
app.py                  ← Entry point, sidebar navigation, load data
config.py               ← TẤT CẢ hằng số: Sheet ID, tên cột, màu sắc ← CHỈNH Ở ĐÂY
data_loader.py          ← Đọc + cache dữ liệu từ Google Sheets (CSV export)
utils.py                ← Hàm format số, màu sắc, helper
modules/
  p1_hieu_qua_hd.py     ← Trang 1: Hiệu quả hoạt động
  p2_cp_gian_tiep.py    ← Trang 2: Chi phí bộ phận gián tiếp
  p3_cong_no.py         ← Trang 3: Công nợ quá hạn
  p4_cong_viec.py       ← Trang 4: Báo cáo công việc
scripts/
  discover_columns.py   ← Chạy đầu tiên để kiểm tra tên cột thực tế
```

## Quy trình khi chạy lần đầu tiên
```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Khám phá tên cột thực tế trong Google Sheets
python scripts/discover_columns.py

# 3. Cập nhật tên cột trong config.py nếu cần

# 4. Chạy app
streamlit run app.py
```

## Yêu cầu bắt buộc với Google Sheets
- Sheet phải được share: **Anyone with the link → Viewer**
- Sheet ID hiện tại: `1F-W0BbBqzKKr-wCXZJBswW-afBpYkTxvvtHT6AdL77I`
- 4 sheet tabs cần có: `data_full_grouped`, `data_CongNo`, `data_BCQT_target V.2`, `data_BCQT_detail_by_M V.2`

## Khi gặp lỗi "KeyError" hoặc "column not found"
1. Chạy: `python scripts/discover_columns.py`
2. Tìm tên cột đúng trong output (in ra toàn bộ columns của mỗi sheet)
3. Cập nhật constant tương ứng trong `config.py` — KHÔNG sửa trực tiếp trong file modules/
4. Chạy lại app

## Quy ước code bắt buộc
- **Format số**: dùng `utils.fmt_ty(value)` cho tỷ đồng, `utils.fmt_pct(value)` cho %
- **Màu chart**: `COLOR_ACTUAL` (xanh đậm, thực tế) và `COLOR_PLAN` (xanh lá, kế hoạch)
- **Cache**: `@st.cache_data(ttl=CACHE_TTL)` — không cache tạm thời bên ngoài decorator
- **Chart size**: luôn dùng `use_container_width=True` + `height=` phù hợp mobile (≤400px)
- **Số liệu**: chia cho `1e9` trước khi hiển thị (đơn vị tỷ đồng)
- **Import**: tất cả import từ config, không hardcode strings

## Thêm trang mới
1. Tạo `modules/p5_ten_trang.py` với function `render(df)`
2. Thêm entry vào `PAGES` dict trong `config.py`
3. Thêm load + call vào block if/elif trong `app.py`

## Deploy lên Streamlit Cloud
1. Push toàn bộ folder lên GitHub repo (public hoặc private)
2. Vào share.streamlit.io → New app → chọn repo + file `app.py`
3. Không cần secrets nếu Google Sheet đã public
4. App URL sẽ dạng: `https://username-reponame.streamlit.app`

## Cấu trúc dữ liệu dự kiến

### data_full_grouped
- Filter: Grouped_BU, Ngày tháng/datetime
- Metrics: DT thực tế/kế hoạch, GVHB, LN gộp, CPQL, LNST, BLN%
- Dạng: mỗi dòng = 1 BU × 1 tháng

### data_CongNo
- Columns: Ma_Bp, Tên công ty, Số ngày quá hạn, ĐVT, Thành tiền
- Dùng cho: bảng công nợ với heat-map màu đỏ

### data_BCQT_target V.2
- Columns: Phòng, Tên công việc, Owner, Đơn vị đo lường, Mức độ thực hiện, Ngày tháng
- Dùng cho: bảng % hoàn thành với màu xanh/vàng/đỏ

### data_BCQT_detail_by_M V.2
- Columns: Tên công việc, Chi tiết công việc con, Tháng, Trạng thái, Kết quả, Việc tiếp theo
- Dùng cho: bảng chi tiết công việc theo tháng
