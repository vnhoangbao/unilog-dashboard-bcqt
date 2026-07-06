# =============================================================
# auth.py — Đăng nhập bằng danh sách user lưu trên Google Sheet
# Sheet "users": Username | password_hash | role | active | note
# =============================================================

import hashlib
import pandas as pd
import streamlit as st

from config import (
    US_USERNAME, US_PASSWORD, US_ROLE, US_ACTIVE, COLOR_PRIMARY,
    USERS_SHEET_ID, SHEET_GIDS,
)


def load_users() -> pd.DataFrame:
    """Load danh sách user active từ Google Sheet riêng (không chung sheet dữ liệu BCQT)."""
    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{USERS_SHEET_ID}/export?format=csv&gid={SHEET_GIDS['users']}"
    )
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        if US_ACTIVE in df.columns:
            df = df[df[US_ACTIVE].astype(str).str.upper().str.strip() == "TRUE"]
        return df
    except Exception as e:
        st.error(f"Lỗi đọc sheet users: {e}")
        return pd.DataFrame()


def hash_password(pw: str) -> str:
    """Hash password bằng SHA256."""
    return hashlib.sha256(pw.encode()).hexdigest()


def check_login(username: str, password: str) -> dict | None:
    """
    Kiểm tra login. Trả về dict user nếu đúng, None nếu sai.
    Hỗ trợ cả plaintext lẫn SHA256 hash trong sheet.
    """
    df = load_users()
    if df.empty:
        st.error("Không đọc được danh sách user.")
        return None

    # Debug: chỉ hiện TÊN cột để tìm lỗi KeyError, KHÔNG hiện dữ liệu —
    # trang login public, in cả bảng sẽ lộ password_hash cho bất kỳ ai ghé app
    st.write("Cột trong sheet:", df.columns.tolist())

    # Tìm cột username
    user_col = None
    for c in [US_USERNAME, "Username", "username", "USER", "user"]:
        if c in df.columns:
            user_col = c
            break
    if user_col is None:
        st.error(f"Không tìm thấy cột Username. Cột hiện có: {df.columns.tolist()}")
        return None

    # Tìm cột password
    pw_col = None
    for c in [US_PASSWORD, "password_hash", "password", "Password", "PASSWORD"]:
        if c in df.columns:
            pw_col = c
            break
    if pw_col is None:
        st.error(f"Không tìm thấy cột password. Cột hiện có: {df.columns.tolist()}")
        return None

    row = df[df[user_col].astype(str).str.strip() == username.strip()]
    if row.empty:
        return None

    stored = str(row.iloc[0][pw_col]).strip()
    if password.strip() == stored or hash_password(password) == stored:
        user = row.iloc[0].to_dict()
        # Chuẩn hóa: đảm bảo luôn có key US_USERNAME dù cột thật trong sheet
        # tên khác (vd "username" thay vì "Username") — render_login_page() cần key này
        user[US_USERNAME] = user[user_col]
        return user
    return None


def render_login_page():
    """Render trang đăng nhập."""
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none !important; }}
    .login-container {{
        max-width: 420px;
        margin: 60px auto;
        padding: 40px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    }}
    .login-logo {{
        text-align: center;
        margin-bottom: 32px;
    }}
    .login-logo .icon {{ font-size: 48px; }}
    .login-logo .title {{
        font-size: 22px;
        font-weight: 700;
        color: {COLOR_PRIMARY};
        margin-top: 8px;
    }}
    .login-logo .sub {{
        font-size: 13px;
        color: #94a3b8;
    }}
    .login-footer {{
        text-align: center;
        font-size: 12px;
        color: #94a3b8;
        margin-top: 40px;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-logo">
        <div class="icon">📊</div>
        <div class="title">BCQT Dashboard</div>
        <div class="sub">U&I Logistics · Nội bộ</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Tài khoản", placeholder="Nhập username...")
        password = st.text_input("Mật khẩu", type="password",
                                  placeholder="Nhập password...")
        submitted = st.form_submit_button("🔐 Đăng nhập",
                                          use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Vui lòng nhập đầy đủ tài khoản và mật khẩu.")
        else:
            user = check_login(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user[US_USERNAME]
                st.session_state["role"] = user.get(US_ROLE, "viewer")
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu.")

    st.markdown("""
    <div class="login-footer">
        © 2026 U&I Logistics · Chỉ dùng nội bộ
    </div>
    """, unsafe_allow_html=True)


def logout():
    """Đăng xuất."""
    for key in ["logged_in", "username", "role"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_login():
    """
    Gọi hàm này ở đầu app.py.
    Nếu chưa đăng nhập → hiện trang login.
    Nếu đã đăng nhập → tiếp tục.
    """
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        render_login_page()
        st.stop()
