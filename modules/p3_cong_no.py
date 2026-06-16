# =============================================================
# modules/p3_cong_no.py — Trang 3: Công nợ quá hạn
# Sheet data_CongNo — gid=111484222 (HTTP 400 nếu chưa accessible)
# =============================================================

import pandas as pd
import streamlit as st

from config import (
    CN_BP, CN_KHACH, CN_NGAY, CN_DVT, CN_TIEN, CN_NGAY_OPTIONS,
)
from data_loader import check_columns
from utils import style_heat_red

REQUIRED_COLS = [CN_BP, CN_TIEN]


def render(df: pd.DataFrame):
    SHEET_URL = (
        "https://docs.google.com/spreadsheets/d/"
        "1F-W0BbBqzKKr-wCXZJBswW-afBpYkTxvvtHT6AdL77I"
        "/edit#gid=111484222"
    )
    if df is None or df.empty:
        st.error(
            "⚠️ **Không thể tải dữ liệu Công nợ** (HTTP 400 — sheet chưa accessible).\n\n"
            "**Thử thủ công:**\n"
            f"1. [Mở sheet data_CongNo]({SHEET_URL})\n"
            "2. Nếu bị từ chối truy cập → nhờ admin chia sẻ \"Anyone with link → Viewer\"\n"
            "3. Copy `gid=XXXXXXX` từ URL và cập nhật `SHEET_GIDS['cong_no']` trong `config.py`\n"
            "4. Bấm 🔄 Làm mới dữ liệu"
        )
        st.stop()

    # Convert comma-formatted number strings → float
    df = df.copy()
    if CN_TIEN in df.columns:
        df[CN_TIEN] = pd.to_numeric(
            df[CN_TIEN].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce",
        ).fillna(0.0)

    if not check_columns(df, REQUIRED_COLS, "data_CongNo"):
        with st.expander("📋 Cột thực tế (bấm để xem)"):
            st.write(list(df.columns))
        return

    has_khach = CN_KHACH in df.columns
    has_ngay  = CN_NGAY  in df.columns
    has_dvt   = CN_DVT   in df.columns

    # ── SIDEBAR FILTERS ──────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🎛️ Bộ lọc — Trang 3")

        all_bp = sorted(df[CN_BP].dropna().unique().tolist())
        sel_bp = st.multiselect("Bộ phận (Ma_Bp)", all_bp, default=all_bp, key="p3_bp")

        if has_ngay:
            all_ngay = sorted(df[CN_NGAY].dropna().unique().tolist())
            sel_ngay = st.multiselect("Số ngày quá hạn", all_ngay, default=all_ngay, key="p3_ngay")
        else:
            sel_ngay = []

        if has_dvt:
            all_dvt = sorted(df[CN_DVT].dropna().unique().tolist())
            sel_dvt = st.multiselect("Đơn vị tiền tệ", all_dvt, default=all_dvt, key="p3_dvt")
        else:
            sel_dvt = []

    # ── LỌC ─────────────────────────────────────────────────
    dff = df.copy()
    if sel_bp:
        dff = dff[dff[CN_BP].isin(sel_bp)]
    if sel_ngay and has_ngay:
        dff = dff[dff[CN_NGAY].isin(sel_ngay)]
    if sel_dvt and has_dvt:
        dff = dff[dff[CN_DVT].isin(sel_dvt)]

    # ── TỔNG CÔNG NỢ ────────────────────────────────────────
    total_vnd = dff[dff[CN_DVT] == "VND"][CN_TIEN].sum() if has_dvt and "VND" in (sel_dvt or []) else dff[CN_TIEN].sum()
    st.markdown(
        f"<div style='padding:12px 16px; background:#fef2f2; border:0.5px solid #fecaca; "
        f"border-radius:8px; margin-bottom:16px;'>"
        f"<p style='margin:0; font-size:12px; color:#b91c1c'>⚠️ Tổng công nợ quá hạn</p>"
        f"<p style='margin:4px 0 0; font-size:24px; font-weight:600; color:#991b1b'>"
        f"{dff[CN_TIEN].sum():,.0f}</p></div>",
        unsafe_allow_html=True,
    )

    # ── BẢNG 1: THEO BỘ PHẬN ────────────────────────────────
    st.markdown("#### Bảng công nợ quá hạn theo bộ phận")
    grp_cols = [CN_BP]
    if has_dvt:
        grp_cols.append(CN_DVT)
    by_bp = dff.groupby(grp_cols)[CN_TIEN].sum().reset_index()
    by_bp = by_bp.sort_values(CN_TIEN, ascending=False)

    rename_map = {CN_BP: "Bộ phận", CN_TIEN: "Thành tiền"}
    if has_dvt:
        rename_map[CN_DVT] = "ĐVT"
    by_bp_disp = by_bp.rename(columns=rename_map)

    styled1 = style_heat_red(by_bp_disp, "Thành tiền")
    styled1 = styled1.format({"Thành tiền": "{:,.0f}"})
    st.dataframe(styled1, use_container_width=True, height=300)

    # ── BẢNG 2: THEO KHÁCH HÀNG ─────────────────────────────
    if has_khach:
        st.markdown("#### Bảng công nợ quá hạn theo khách hàng")
        grp_cols2 = [CN_KHACH]
        if has_dvt:
            grp_cols2.append(CN_DVT)
        by_kh = dff.groupby(grp_cols2)[CN_TIEN].sum().reset_index()
        by_kh = by_kh.sort_values(CN_TIEN, ascending=False)

        rename_kh = {CN_KHACH: "Tên công ty", CN_TIEN: "Thành tiền"}
        if has_dvt:
            rename_kh[CN_DVT] = "ĐVT"
        by_kh_disp = by_kh.rename(columns=rename_kh)

        styled2 = style_heat_red(by_kh_disp, "Thành tiền")
        styled2 = styled2.format({"Thành tiền": "{:,.0f}"})
        total_rows = len(by_kh_disp)
        st.dataframe(styled2, use_container_width=True,
                     height=min(600, total_rows * 35 + 60))
        st.caption(f"1 – {total_rows} / {total_rows} khách hàng")

    # ── BẢNG 3: THEO BỘ PHẬN + NGÀY QUÁ HẠN ────────────────
    if has_khach and has_ngay:
        st.markdown("#### Bảng công nợ theo bộ phận và số ngày quá hạn")
        grp_cols3 = [CN_BP]
        if has_khach:
            grp_cols3.append(CN_KHACH)
        if has_ngay:
            grp_cols3.append(CN_NGAY)
        if has_dvt:
            grp_cols3.append(CN_DVT)

        by_full = dff.groupby(grp_cols3)[CN_TIEN].sum().reset_index()
        by_full = by_full.sort_values(CN_TIEN, ascending=False)

        rename_full = {
            CN_BP: "Bộ phận", CN_KHACH: "Tên công ty",
            CN_NGAY: "Số ngày quá hạn", CN_DVT: "ĐVT", CN_TIEN: "Thành tiền"
        }
        by_full_disp = by_full.rename(columns={k: v for k, v in rename_full.items() if k in by_full.columns})

        styled3 = style_heat_red(by_full_disp, "Thành tiền")
        styled3 = styled3.format({"Thành tiền": "{:,.0f}"})
        total_full = len(by_full_disp)
        st.dataframe(styled3, use_container_width=True,
                     height=min(600, total_full * 35 + 60))
