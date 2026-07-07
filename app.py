# =============================================================
# app.py — Entry point chính
# Chạy: streamlit run app.py
# =============================================================

import streamlit as st
from config import PAGE_NAMES, COLOR_PRIMARY
from auth import require_login, logout

st.set_page_config(
    page_title="BCQT | U&I Logistics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_login()

st.markdown("""
<style>
  #MainMenu { visibility: hidden; }
  footer     { visibility: hidden; }

  /* ── SIDEBAR TỐI ── */
  [data-testid="stSidebar"] {
      background-color: #0f1c35 !important;
  }
  section[data-testid="stSidebar"] {
      color: #ffffff !important;
  }
  section[data-testid="stSidebar"] * {
      color: #ffffff !important;
  }

  /* ── NỘI DUNG CHÍNH — NỀN SÁNG ── */
  [data-testid="stAppViewContainer"] > .main {
      background-color: #f8fafc;
  }

  /* ── METRIC CARDS ── */
  [data-testid="metric-container"] {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  [data-testid="stMetricLabel"] {
      color: #64748b !important;
      font-size: 12px;
      font-weight: 500;
  }
  [data-testid="stMetricValue"] {
      color: #1e293b !important;
      font-size: 22px;
      font-weight: 700;
  }

  /* ── CHART CONTAINER ── */
  [data-testid="stPlotlyChart"] {
      background: #ffffff;
      border-radius: 10px;
      padding: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  /* ── DATAFRAME ── */
  [data-testid="stDataFrame"] {
      border-radius: 8px;
      overflow: hidden;
  }

  /* ── SIDEBAR MULTISELECT TAGS ── */
  [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
      background-color: #1e3a5f !important;
      color: white !important;
  }

  /* ── SIDEBAR BUTTON ── */
  [data-testid="stSidebar"] .stButton button {
      background: #1e3a5f;
      color: white;
      border: 1px solid #2d4a7a;
      border-radius: 8px;
      width: 100%;
      font-weight: 600;
  }
  [data-testid="stSidebar"] .stButton button:hover {
      background: #2d4a7a;
  }

  /* ── HEADING CHÍNH ── */
  h1, h2, h3 {
      color: #1e293b !important;
      font-weight: 700 !important;
  }

  /* ── PROGRESS BAR ── */
  [data-testid="stProgressBar"] > div > div {
      background-color: #1e3a5f !important;
  }

  /* ── DIVIDER ── */
  hr { border-color: #e2e8f0; }

  /* ── EXPANDER ── */
  [data-testid="stExpander"] {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
  }

  /* ── EXPANDER 🔗 TRONG SIDEBAR — nền tối riêng, không dùng nền trắng ở trên ── */
  /* (nếu không có rule này, chữ trắng sẽ nằm trên nền trắng và biến mất) */
  section[data-testid="stSidebar"] [data-testid="stExpander"] {
      background: #1e3a5f !important;
      border: 1px solid #2d4a7a !important;
  }

  /* Force sidebar white text - nuclear option */
  section[data-testid="stSidebar"] .stCheckbox label p { color: white !important; }
  section[data-testid="stSidebar"] .stCheckbox span[data-baseweb] { color: white !important; }
  section[data-testid="stSidebar"] details summary p { color: white !important; }
  section[data-testid="stSidebar"] details div p { color: white !important; }
  section[data-testid="stSidebar"] details label p { color: white !important; }

</style>
""", unsafe_allow_html=True)

from data_loader import load_full_grouped, load_cong_no, load_target, load_detail
import modules.p0_tong_quan  as p0
import modules.p1_hieu_qua_hd  as p1
import modules.p2_cp_gian_tiep as p2
import modules.p3_cong_no      as p3
import modules.p4_cong_viec    as p4

with st.sidebar:
    st.markdown(
        "<div style='background:linear-gradient(135deg,#1e3a5f 0%,#2d4a7a 100%); color:white; "
        "padding:14px 16px; border-radius:10px; margin-bottom:16px;'>"
        "<p style='margin:0; font-size:10px; opacity:.6; letter-spacing:1.5px'>U&I LOGISTICS</p>"
        "<p style='margin:2px 0 0; font-size:17px; font-weight:500'>BCQT Dashboard</p>"
        "<p style='margin:4px 0 0; font-size:10px; opacity:.6'>Năm 2026 · Auto-refresh 5 phút</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    page = st.radio("Chọn báo cáo", PAGE_NAMES, label_visibility="collapsed")

    st.markdown("---")
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([2, 1])
    col1.markdown(f"👤 **{st.session_state.get('username', '')}**")
    if col2.button("Đăng xuất"):
        logout()

st.markdown(
    f"<h2 style='margin:0 0 16px; color:{COLOR_PRIMARY}; font-size:20px'>{page}</h2>",
    unsafe_allow_html=True,
)

if page == PAGE_NAMES[0]:          # 0. Tổng quan
    df_fg = load_full_grouped()
    p0.render(df_fg)

elif page == PAGE_NAMES[1]:        # 1. Hiệu quả hoạt động
    df_fg = load_full_grouped()
    p1.render(df_fg)

elif page == PAGE_NAMES[2]:        # 2. CP bộ phận gián tiếp
    df_fg = load_full_grouped()
    p2.render(df_fg)

elif page == PAGE_NAMES[3]:        # 3. Công nợ quá hạn
    df_cn = load_cong_no()
    p3.render(df_cn)

elif page == PAGE_NAMES[4]:        # 4. Báo cáo công việc
    df_tg = load_target()
    df_dt = load_detail()
    p4.render(df_tg, df_dt)
