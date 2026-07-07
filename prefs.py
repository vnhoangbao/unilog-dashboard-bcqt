# =============================================================
# prefs.py — Lưu/đọc trạng thái checkbox liên kết bộ lọc (🔗)
# Ghi ngược lên tab "prefs" trong Google Sheet users (dùng chung
# mọi thiết bị/người dùng) qua Google Service Account.
#
# YÊU CẦU THIẾT LẬP (làm 1 lần, xem hướng dẫn đầy đủ trong README/chat):
#   1. Tạo Service Account trên Google Cloud Console, bật Sheets API + Drive API
#   2. Tạo key JSON cho service account đó
#   3. Share Google Sheet users (USERS_SHEET_ID trong config.py) cho email
#      service account đó với quyền Editor
#   4. Tạo tab tên "prefs" (config.PREFS_SHEET_TAB) trong đúng file sheet đó,
#      dòng đầu là header: pref_key | value
#   5. Dán nội dung JSON key vào Streamlit secrets với tên "gcp_service_account"
#      (Manage app → Settings → Secrets trên Streamlit Cloud)
#
# Nếu chưa thiết lập xong, các hàm bên dưới tự động fallback về giá trị mặc định
# (không làm crash app) — chỉ đơn giản là chưa lưu được trạng thái.
# =============================================================

import streamlit as st

from config import USERS_SHEET_ID, PREFS_SHEET_TAB

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


@st.cache_resource(show_spinner=False)
def _get_worksheet():
    """Kết nối tới tab 'prefs' — trả về None nếu chưa cấu hình secrets/sheet."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=_SCOPES,
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key(USERS_SHEET_ID)
        return sh.worksheet(PREFS_SHEET_TAB)
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def load_prefs() -> dict:
    """Đọc toàn bộ {pref_key: bool} đã lưu. Trả về {} nếu chưa thiết lập xong."""
    ws = _get_worksheet()
    if ws is None:
        return {}
    try:
        rows = ws.get_all_records()
        return {
            str(r.get("pref_key", "")).strip(): str(r.get("value", "")).strip().upper() == "TRUE"
            for r in rows if r.get("pref_key")
        }
    except Exception:
        return {}


def save_pref(key: str, value: bool) -> None:
    """Ghi 1 pref_key vào sheet — tìm dòng theo key, update hoặc thêm dòng mới."""
    ws = _get_worksheet()
    if ws is None:
        return
    try:
        cell = ws.find(key, in_column=1)
        new_val = "TRUE" if value else "FALSE"
        if cell:
            ws.update_cell(cell.row, 2, new_val)
        else:
            ws.append_row([key, new_val])
        load_prefs.clear()  # bỏ cache để lần load sau lấy giá trị mới nhất
    except Exception:
        pass
