# =============================================================
# config.py — Tất cả cấu hình tập trung tại đây
# =============================================================

# ─── GOOGLE SHEETS ───────────────────────────────────────────
SHEET_ID  = "1F-W0BbBqzKKr-wCXZJBswW-afBpYkTxvvtHT6AdL77I"
CACHE_TTL = 300   # giây — refresh mỗi 5 phút

SHEET_GIDS = {
    "full_grouped": "353917314",
    "cong_no":      "2111484222",
    "target":       "1974781100",
    "detail":       "1080595888",
}

# ─── CỘT: data_full_grouped (LONG FORMAT) ────────────────────
# Cấu trúc: mỗi dòng = 1 STT × 1 BU × 1 tháng
FG_STT       = "STT"
FG_NOI_DUNG  = "Nội dung_Stt"
FG_DATETIME  = "Ngày tháng_datetime"
FG_THUC_TE   = "Số thực tế"
FG_KE_HOACH  = "Số kế hoạch"
FG_BU        = "Grouped_BU"
FG_QUY       = "Quý"

# ─── STT CHỈ TIÊU ────────────────────────────────────────────
STT_DT     = 1      # Doanh thu bán hàng
STT_DT_KH  = 5      # Doanh thu thuần — cột KH cho DT (STT=1 KH=0 trong sheet)
STT_GVHB   = 6      # Giá vốn hàng bán
STT_LN_GOP = 72     # Lợi nhuận gộp
STT_CPQLDN = 82     # Chi phí QLDN
STT_LNHDKD = 146    # LN Hoạt động kinh doanh (không có KH riêng trong sheet)
STT_LNTT   = 162    # LN Trước thuế
STT_LNST   = 165    # LN Sau thuế

# STT 152–160: phân bổ chi phí gián tiếp theo phòng ban
# 152=PT THI TRUONG, 153=PHONG SALE, 154=HCNS, 155=KETOAN,
# 156=PHAP CHE-KSNB, 157=BGD, 158=QTDC, 159=DUNGCHUNG, 160=SDDM
STT_CPGT_FROM = 152
STT_CPGT_TO   = 160

# CPQL = STT 82 (Chi phí QLDN) + STT 151 (Phân bổ CP gián tiếp)
STT_CPQL_LIST = [82, 151]

# ─── ALERT FILTER ────────────────────────────────────────────
# Cost center / dự án đầu tư — không hiển thị trong cảnh báo lỗ
EXCLUDE_FROM_ALERT = ["HỘI ĐÒNG QUẢN TRỊ", "LOG", "DỰ ÁN CÁI MÉP"]

# ─── CỘT: data_CongNo (gid=111484222 — cần kiểm tra access) ─
CN_BP    = "Ma_Bp"
CN_KHACH = "TÊN CÔNG TY"
CN_NGAY  = "SỐ NGÀY QUÁ HẠN"
CN_DVT   = "ĐVT"
CN_TIEN  = "THÀNH TIỀN"

CN_NGAY_OPTIONS = [">90", ">60", ">30", ">15"]

# ─── CỘT: data_BCQT_target V.2 ───────────────────────────────
TG_ID        = "TARGETID"
TG_PHONG     = "Phòng"
TG_MA_BP     = "Ma_BP"
TG_NGAY_BD   = "Ngày bắt đầu"
TG_NGAY_KT   = "Ngày kết thúc"
TG_CONGVIEC  = "Tên công việc"
TG_THANG     = "Tháng"              # không có trong sheet → has_thang=False, filter ẩn
TG_MOTA      = "Mô tả mục tiêu cần thực hiện "   # có trailing space
TG_PHANLOAI  = "Phân loại"
TG_OWNER     = "Owner"
TG_DVL       = "Đơn vị đo lường"
TG_SO_TH     = "Số liệu đo lường"
TG_SO_KH     = "Số liệu kế hoạch"
TG_MDTH      = "Mức độ thực hiện"
TG_TRANGTHAI = "Trạng thái hiện tại"

# ─── CỘT: data_BCQT_detail_by_M V.2 ─────────────────────────
DT_ID        = "DETAIL_ID"
DT_TARGET_ID = "TARGETID"
DT_MA_BP     = "Ma_Bp"
DT_NGAY      = "Ngày tháng"
DT_THANG     = "Ngày tháng"        # alias cho DT_NGAY — dùng làm filter tháng trong p4
DT_CONGVIEC  = "Tên công việc"     # không có trong detail sheet → bỏ qua gracefully
DT_CHITIET   = "Chi tiết công việc con"
DT_KETQUA    = "Công việc đã làm,kết quả, vấn đề"
DT_TIEPTHEO  = "Công việc tiếp theo, kpi đo lường , kết quả dự kiến"
DT_SO_TH     = "Số liệu đo lường"
DT_SO_KH     = "Số liệu kế hoạch"
DT_MDTH      = "Mức độ thực hiện"
DT_TRANGTHAI = "Trạng thái"

# ─── TRẠNG THÁI CÔNG VIỆC ────────────────────────────────────
TRANG_THAI_COLORS = {
    "Vượt kế hoạch":   "#22c55e",
    "Đúng kế hoạch":   "#3b82f6",
    "Tiệm cận":        "#f59e0b",
    "Cảnh báo":        "#f97316",
    "Đang thực hiện":  "#f59e0b",
    "Chậm tiến độ":    "#ef4444",
}
TRANG_THAI_DEFAULT = "#94a3b8"

COMPLETION_THRESHOLDS = {
    "danger":  70,
    "warning": 90,
}

# ─── UI / NAVIGATION ─────────────────────────────────────────
PAGE_NAMES = [
    "0. Tổng quan",
    "1. Hiệu quả hoạt động",
    "2. Chi phí QLDN theo BU",
    "3. Công nợ quá hạn",
    "4. Báo cáo công việc",
]

# ─── COLORS ──────────────────────────────────────────────────
COLOR_PRIMARY = "#1e3a5f"
COLOR_ACTUAL  = "#1e3a5f"
COLOR_PLAN    = "#4caf50"
COLOR_DANGER  = "#ef4444"
COLOR_WARNING = "#f59e0b"
COLOR_OK      = "#22c55e"
COLOR_INFO    = "#3b82f6"
COLOR_MUTED   = "#94a3b8"
