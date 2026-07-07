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
from utils import render_link_controls, link_badge

REQUIRED_COLS = [CN_BP, CN_TIEN]

# Tên bảng trong p3 — unlinked = bỏ qua toàn bộ bộ lọc (Bộ phận/Số ngày/ĐVT), hiện dữ liệu gốc
P3_CHARTS = [
    "Bảng theo bộ phận",
    "Bảng theo khách hàng",
]

# ── HEADER/CELL STYLE — khớp giao diện trang 4 (df_to_html) ────
_TABLE_STYLE = "width:100%;border-collapse:collapse"
_TD = (
    "padding:7px 12px;font-size:12px;color:#1e293b;"
    "border-bottom:0.5px solid #e2e8f0"
)


def _heat_style(val, max_val):
    if pd.isna(val) or val == 0:
        return ""
    intensity = min(val / max_val, 1.0)
    r = int(239 + (255 - 239) * (1 - intensity))
    g = int(68  + (255 - 68)  * (1 - intensity))
    b = int(68  + (255 - 68)  * (1 - intensity))
    return f";background-color:rgba({r},{g},{b},0.6);color:#7f1d1d;font-weight:600"


def df_to_html(df_show: pd.DataFrame, heat_col: str = None, max_height: int = None) -> str:
    max_val = df_show[heat_col].max() if heat_col and df_show[heat_col].max() > 0 else 1

    rows_html = ""
    for _, row in df_show.iterrows():
        cells = ""
        for col in df_show.columns:
            val = row[col]
            style = _TD
            if col == heat_col and isinstance(val, (int, float)):
                style += _heat_style(val, max_val)
                cells += f"<td style='{style}'>{val:,.0f}</td>"
            else:
                cells += f"<td style='{style}'>{val}</td>"
        rows_html += f"<tr>{cells}</tr>"

    header_cells = ""
    for c in df_show.columns:
        style_th = (
            f"background:#1e3a5f;color:white;font-weight:700;"
            f"font-size:12px;padding:10px 12px;text-align:left;"
            f"border-bottom:2px solid #2d4a7a;"
            f"width:100px;overflow:hidden;text-overflow:ellipsis;"
            f"white-space:nowrap"
        )
        header_cells += f"<th style='{style_th}'>{c}</th>"

    wrap_style = "overflow-x:auto;border-radius:8px;border:1px solid #e2e8f0;margin-bottom:12px"
    if max_height:
        wrap_style += f";overflow-y:auto;max-height:{max_height}px"

    return (
        f"<div style='{wrap_style}'>"
        f"<table style='{_TABLE_STYLE}'>"
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table></div>"
    )


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

        links_bp_p3 = render_link_controls(P3_CHARTS, "p3", "bp")

    # ── LỌC ─────────────────────────────────────────────────
    dff = df.copy()
    if sel_bp:
        dff = dff[dff[CN_BP].isin(sel_bp)]
    if sel_ngay and has_ngay:
        dff = dff[dff[CN_NGAY].isin(sel_ngay)]
    if sel_dvt and has_dvt:
        dff = dff[dff[CN_DVT].isin(sel_dvt)]

    def data_for(chart_name: str) -> pd.DataFrame:
        """Trả về df đã lọc (linked) hoặc df gốc không lọc (unlinked)."""
        return dff if links_bp_p3[chart_name] else df

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
    st.caption(link_badge(links_bp_p3["Bảng theo bộ phận"]))
    data_bp = data_for("Bảng theo bộ phận")
    grp_cols = [CN_BP]
    if has_dvt:
        grp_cols.append(CN_DVT)
    by_bp = data_bp.groupby(grp_cols)[CN_TIEN].sum().reset_index()
    by_bp = by_bp.sort_values(CN_TIEN, ascending=False)

    rename_map = {CN_BP: "Bộ phận", CN_TIEN: "Thành tiền"}
    if has_dvt:
        rename_map[CN_DVT] = "ĐVT"
    by_bp_disp = by_bp.rename(columns=rename_map)

    st.markdown(
        df_to_html(by_bp_disp, heat_col="Thành tiền", max_height=300),
        unsafe_allow_html=True,
    )

    # ── BẢNG 2: THEO KHÁCH HÀNG ─────────────────────────────
    if has_khach:
        st.markdown("#### Bảng công nợ quá hạn theo khách hàng")
        st.caption(link_badge(links_bp_p3["Bảng theo khách hàng"]))
        data_kh = data_for("Bảng theo khách hàng")
        grp_cols2 = [CN_KHACH]
        if has_dvt:
            grp_cols2.append(CN_DVT)
        by_kh = data_kh.groupby(grp_cols2)[CN_TIEN].sum().reset_index()
        by_kh = by_kh.sort_values(CN_TIEN, ascending=False)

        rename_kh = {CN_KHACH: "Tên công ty", CN_TIEN: "Thành tiền"}
        if has_dvt:
            rename_kh[CN_DVT] = "ĐVT"
        by_kh_disp = by_kh.rename(columns=rename_kh)

        total_rows = len(by_kh_disp)
        st.markdown(
            df_to_html(by_kh_disp, heat_col="Thành tiền",
                       max_height=min(600, total_rows * 35 + 60)),
            unsafe_allow_html=True,
        )
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

        total_full = len(by_full_disp)
        st.markdown(
            df_to_html(by_full_disp, heat_col="Thành tiền",
                       max_height=min(600, total_full * 35 + 60)),
            unsafe_allow_html=True,
        )
