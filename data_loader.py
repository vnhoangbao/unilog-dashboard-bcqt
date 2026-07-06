# =============================================================
# data_loader.py — Đọc và cache dữ liệu từ Google Sheets
# data_full_grouped là LONG FORMAT: STT × BU × tháng
# =============================================================

import math
import pandas as pd
import streamlit as st

from config import (
    SHEET_ID, CACHE_TTL, SHEET_GIDS,
    FG_STT, FG_DATETIME, FG_THUC_TE, FG_KE_HOACH, FG_BU,
    FG_NOI_DUNG, FG_QUY,
)


# ─── URL BUILDER ────────────────────────────────────────────
def _sheet_url(gid: str) -> str:
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/export?format=csv&gid={gid}"
    )


def sheet_url(name: str) -> str:
    """Build URL CSV export cho 1 sheet theo tên khai báo trong SHEET_GIDS (dùng ở auth.py)."""
    return _sheet_url(SHEET_GIDS[name])


# ─── LOAD: data_full_grouped (long format) ──────────────────
@st.cache_data(ttl=CACHE_TTL, show_spinner="Đang tải dữ liệu hoạt động...")
def load_full_grouped() -> pd.DataFrame:
    url = _sheet_url(SHEET_GIDS["full_grouped"])
    try:
        df = pd.read_csv(url, low_memory=False)
    except Exception as e:
        st.error(f"❌ Không đọc được sheet full_grouped.")
        raise e

    # Chỉ giữ các cột dữ liệu chính (bỏ cột pivot summary)
    keep = [c for c in [FG_STT, FG_NOI_DUNG, FG_DATETIME,
                        FG_THUC_TE, FG_BU, FG_KE_HOACH, FG_QUY]
            if c in df.columns]
    df = df[keep].copy()

    # STT: dòng có formula (row 0) sẽ thành NaN sau to_numeric → drop
    df[FG_STT] = pd.to_numeric(
        df[FG_STT].astype(str).str.strip(), errors="coerce"
    )
    df = df.dropna(subset=[FG_STT]).copy()

    # Số thực tế / Số kế hoạch → float
    for col in [FG_THUC_TE, FG_KE_HOACH]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str)
                       .str.replace(",", "", regex=False)
                       .str.replace("%", "", regex=False)
                       .str.strip(),
                errors="coerce",
            ).fillna(0.0)

    # Datetime → chuỗi "YYYY-MM-DD"
    if FG_DATETIME in df.columns:
        df[FG_DATETIME] = (
            pd.to_datetime(df[FG_DATETIME], errors="coerce")
            .dt.strftime("%Y-%m-%d")
        )
        df = df.dropna(subset=[FG_DATETIME])

    return df.reset_index(drop=True)


# ─── LOAD: data_CongNo ──────────────────────────────────────
@st.cache_data(ttl=CACHE_TTL, show_spinner="Đang tải dữ liệu công nợ...")
def load_cong_no() -> pd.DataFrame:
    url = _sheet_url(SHEET_GIDS["cong_no"])
    try:
        df = pd.read_csv(url, low_memory=False)
        return df.dropna(how="all").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()   # trả về rỗng nếu lỗi


# ─── LOAD: data_BCQT_target ─────────────────────────────────
@st.cache_data(ttl=CACHE_TTL, show_spinner="Đang tải mục tiêu công việc...")
def load_target() -> pd.DataFrame:
    url = _sheet_url(SHEET_GIDS["target"])
    try:
        df = pd.read_csv(url, low_memory=False)
        # Loại bỏ cột Unnamed
        df = df[[c for c in df.columns if not str(c).startswith("Unnamed")]]
        return df.dropna(how="all").reset_index(drop=True)
    except Exception as e:
        st.error("❌ Không đọc được sheet target")
        raise e


# ─── LOAD: data_BCQT_detail_by_M ────────────────────────────
@st.cache_data(ttl=CACHE_TTL, show_spinner="Đang tải chi tiết công việc...")
def load_detail() -> pd.DataFrame:
    url = _sheet_url(SHEET_GIDS["detail"])
    try:
        df = pd.read_csv(url, low_memory=False)
        df = df[[c for c in df.columns if not str(c).startswith("Unnamed")]]
        return df.dropna(how="all").reset_index(drop=True)
    except Exception as e:
        st.error("❌ Không đọc được sheet detail")
        raise e


# ─── HELPER: lấy chỉ tiêu TT theo tháng ────────────────────
def get_metric(
    df: pd.DataFrame,
    stt: int,
    sel_months: list,
    sel_bu: list,
) -> dict:
    """
    Trả về {month: total_actual} cho 1 STT, các tháng và BU đã chọn.
    """
    mask = df[FG_STT] == float(stt)
    if sel_bu:
        mask &= df[FG_BU].isin(sel_bu)
    rows = df[mask]
    if sel_months:
        rows = rows[rows[FG_DATETIME].isin(sel_months)]
    if rows.empty or FG_THUC_TE not in rows.columns:
        return {}
    return rows.groupby(FG_DATETIME)[FG_THUC_TE].sum().to_dict()


# ─── HELPER: lấy chỉ tiêu TT theo BU ───────────────────────
def get_metric_by_bu(
    df: pd.DataFrame,
    stt: int,
    sel_months: list,
    sel_bu: list,
) -> dict:
    """
    Trả về {bu: total_actual} cho 1 STT, tổng qua các tháng đã chọn.
    """
    mask = df[FG_STT] == float(stt)
    if sel_bu:
        mask &= df[FG_BU].isin(sel_bu)
    rows = df[mask]
    if sel_months:
        rows = rows[rows[FG_DATETIME].isin(sel_months)]
    if rows.empty or FG_THUC_TE not in rows.columns:
        return {}
    return rows.groupby(FG_BU)[FG_THUC_TE].sum().to_dict()


# ─── HELPER: lấy chỉ tiêu KH theo tháng ────────────────────
def get_metric_plan(
    df: pd.DataFrame,
    stt: int,
    sel_months: list,
    sel_bu: list,
) -> dict:
    """
    Trả về {month: total_plan} cho 1 STT, các tháng và BU đã chọn.
    """
    mask = df[FG_STT] == float(stt)
    if sel_bu:
        mask &= df[FG_BU].isin(sel_bu)
    rows = df[mask]
    if sel_months:
        rows = rows[rows[FG_DATETIME].isin(sel_months)]
    if rows.empty or FG_KE_HOACH not in rows.columns:
        return {}
    return rows.groupby(FG_DATETIME)[FG_KE_HOACH].sum().to_dict()


# ─── HELPER: tổng thực tế cho dải STT ──────────────────────
def get_metric_stt_range(
    df: pd.DataFrame,
    stt_from: float,
    stt_to: float,
    sel_months: list,
    sel_bu: list,
) -> dict:
    """
    Trả về {month: total_actual} cho tất cả STT trong [stt_from, stt_to].
    Dùng để tính GVHB mua ngoài (STT 7–10), vận hành, v.v.
    """
    mask = (df[FG_STT] >= float(stt_from)) & (df[FG_STT] <= float(stt_to))
    if sel_bu:
        mask &= df[FG_BU].isin(sel_bu)
    rows = df[mask]
    if sel_months:
        rows = rows[rows[FG_DATETIME].isin(sel_months)]
    if rows.empty or FG_THUC_TE not in rows.columns:
        return {}
    return rows.groupby(FG_DATETIME)[FG_THUC_TE].sum().to_dict()


# ─── HELPER: tổng TT hoặc KH cho danh sách STT ─────────────
def get_metric_multi(
    df: pd.DataFrame,
    stt_list: list,
    sel_months: list,
    sel_bu: list,
    plan: bool = False,
) -> dict:
    """
    Trả về {month: total} = tổng qua nhiều STT.
    plan=False → Số thực tế, plan=True → Số kế hoạch.
    """
    col = FG_KE_HOACH if plan else FG_THUC_TE
    result: dict = {}
    for stt in stt_list:
        mask = df[FG_STT] == float(stt)
        if sel_bu:
            mask &= df[FG_BU].isin(sel_bu)
        rows = df[mask]
        if sel_months:
            rows = rows[rows[FG_DATETIME].isin(sel_months)]
        if rows.empty or col not in rows.columns:
            continue
        for m, v in rows.groupby(FG_DATETIME)[col].sum().items():
            result[m] = result.get(m, 0) + v
    return result


# ─── UTILITY: kiểm tra cột ──────────────────────────────────
def check_columns(df: pd.DataFrame, required: list, sheet_label: str) -> bool:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(
            f"❌ Sheet **{sheet_label}** thiếu {len(missing)} cột:\n"
            + "\n".join(f"- `{c}`" for c in missing)
        )
        with st.expander("📋 Cột thực tế trong sheet"):
            st.write(list(df.columns))
        return False
    return True
