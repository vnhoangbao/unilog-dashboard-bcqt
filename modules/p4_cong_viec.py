# =============================================================
# modules/p4_cong_viec.py — Trang 4: Báo cáo công việc
# Gồm: filter Phòng/Phân loại/Tháng, bảng mục tiêu theo Owner
#       (màu % hoàn thành), bảng chi tiết công việc theo tháng
# =============================================================

import pandas as pd
import streamlit as st

from config import (
    TG_ID, TG_PHONG, TG_PHANLOAI, TG_THANG, TG_CONGVIEC, TG_OWNER, TG_DVL, TG_MDTH,
    DT_TARGET_ID, DT_CONGVIEC, DT_CHITIET, DT_THANG, DT_TRANGTHAI, DT_KETQUA, DT_TIEPTHEO,
    TRANG_THAI_COLORS, TRANG_THAI_DEFAULT, COMPLETION_THRESHOLDS,
)
from data_loader import check_columns
from utils import link_badge, linked_checkbox
from prefs import load_prefs

REQUIRED_TARGET = [TG_CONGVIEC]
REQUIRED_DETAIL = [DT_THANG, DT_TRANGTHAI]

# Trạng thái được tính là "hoàn thành" khi tính % động — khớp cách Looker Studio
# đang tính (đếm dòng chi tiết theo Trạng thái, không đọc cột tĩnh trong sheet target)
HOAN_THANH_STATUSES = {"Đúng kế hoạch", "Vượt kế hoạch"}

COL_WIDTHS = {
    "Tên công việc":          "260px",
    "Chi tiết công việc con": "240px",
    "Tháng báo cáo":          "70px",
    "Trạng thái":             "90px",
    "Kết quả / Vấn đề":      "200px",
    "Việc tiếp theo / KPI":   "200px",
    "Owner":                  "90px",
    "Đơn vị đo lường":       "70px",
    "Mức độ thực hiện (%)":   "80px",
}

_TABLE_STYLE = (
    "width:100%;border-collapse:collapse;"
    "min-width:800px;table-layout:fixed"
)
_TD = (
    "padding:7px 12px;font-size:12px;color:#1e293b;"
    "border-bottom:0.5px solid #e2e8f0;"
    "overflow:hidden;text-overflow:ellipsis"
)


def df_to_html(df_show, pct_col=None, status_col=None):
    rows_html = ""
    for _, row in df_show.iterrows():
        cells = ""
        for col in df_show.columns:
            val = row[col]
            style = _TD
            if col == pct_col and isinstance(val, (int, float)) and pd.isna(val):
                # Chưa có dòng chi tiết nào khớp trong tháng đang chọn — hiện "—"
                # thay vì 0% để tránh hiểu nhầm là "hoàn toàn chưa làm gì"
                cells += f"<td style='{style}'>—</td>"
            elif col == pct_col and isinstance(val, (int, float)):
                if val >= 90:
                    style += ";background:#f0fdf4;color:#166534;font-weight:600"
                elif val >= 70:
                    style += ";background:#fffbeb;color:#92400e;font-weight:600"
                else:
                    style += ";background:#fef2f2;color:#991b1b;font-weight:600"
                cells += f"<td style='{style}'>{val:.1f}%</td>"
            elif col == status_col:
                if val == "Đúng kế hoạch":
                    style += ";background:#f0fdf4;color:#166534"
                elif val == "Đang thực hiện":
                    style += ";background:#fffbeb;color:#92400e"
                elif val == "Chậm tiến độ":
                    style += ";background:#fef2f2;color:#991b1b"
                elif val == "Hoàn thành":
                    style += ";background:#eff6ff;color:#1d4ed8"
                cells += f"<td style='{style}'>{val}</td>"
            else:
                cells += f"<td style='{style}'>{val}</td>"
        rows_html += f"<tr>{cells}</tr>"

    header_cells = ""
    for c in df_show.columns:
        w = COL_WIDTHS.get(c, "100px")
        style_th = (
            f"background:#1e3a5f;color:white;font-weight:700;"
            f"font-size:12px;padding:10px 12px;text-align:left;"
            f"border-bottom:2px solid #2d4a7a;"
            f"width:{w};overflow:hidden;text-overflow:ellipsis;"
            f"white-space:nowrap"
        )
        header_cells += f"<th style='{style_th}'>{c}</th>"

    return (
        "<div style='overflow-x:auto;border-radius:8px;"
        "border:1px solid #e2e8f0;margin-bottom:12px'>"
        f"<table style='{_TABLE_STYLE}'>"
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table></div>"
    )


def render(df_target: pd.DataFrame, df_detail: pd.DataFrame):
    ok_target = check_columns(df_target, REQUIRED_TARGET, "data_BCQT_target V.2")
    ok_detail = check_columns(df_detail, REQUIRED_DETAIL, "data_BCQT_detail_by_M V.2")

    has_phong    = TG_PHONG    in df_target.columns
    has_phanloai = TG_PHANLOAI in df_target.columns
    has_thang    = TG_THANG    in df_target.columns
    has_mdth     = TG_MDTH     in df_target.columns

    prefs = load_prefs()

    # ── SIDEBAR FILTERS ──────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🎛️ Bộ lọc — Trang 4")

        if has_phong:
            all_phong = sorted(df_target[TG_PHONG].dropna().unique().tolist())
            sel_phong = st.multiselect("Phòng", all_phong, default=all_phong, key="p4_phong")
        else:
            sel_phong = []

        with st.expander("🔗"):
            link_mt_phong = linked_checkbox("Bảng mục tiêu", "link_p4_mt_phong", prefs)
            link_ct_phong = linked_checkbox("Bảng chi tiết",  "link_p4_ct_phong", prefs)

        if has_phanloai:
            all_phanloai = sorted(df_target[TG_PHANLOAI].dropna().unique().tolist())
            _DEFAULT_PL = ["Công việc mặc định"]
            default_pl = [p for p in _DEFAULT_PL if p in all_phanloai] or all_phanloai[:1]
            sel_pl = st.multiselect("Phân loại", all_phanloai, default=default_pl, key="p4_pl")
        else:
            sel_pl = []

        if has_thang:
            all_thang = sorted(df_target[TG_THANG].dropna().unique().tolist())
            sel_thang = st.multiselect("Tháng", all_thang, default=all_thang, key="p4_thang")
        else:
            sel_thang = []

        all_months_detail = sorted(df_detail[DT_THANG].dropna().unique().tolist()) if ok_detail else []

        def _fmt(v): return f"Tháng {int(str(v)[5:7])}" if str(v)[4]=='-' else str(v)
        _map = {_fmt(m): m for m in all_months_detail}

        sel_dt_thang_labels = st.multiselect("Tháng (chi tiết)", list(_map.keys()),
                                             default=list(_map.keys()), key="p4_dt_thang")
        sel_dt_thang = [_map[x] for x in sel_dt_thang_labels]

        # Đặt ngay sau "Tháng (chi tiết)" — vì sheet target hiện KHÔNG có cột
        # "Tháng" thực tế (has_thang=False), nên bộ lọc tháng thật sự đang hoạt
        # động trên trang này chính là "Tháng (chi tiết)", không phải "Tháng"
        with st.expander("🔗"):
            link_mt_thang = linked_checkbox("Bảng mục tiêu", "link_p4_mt_thang", prefs)
            link_ct_thang = linked_checkbox("Bảng chi tiết",  "link_p4_ct_thang", prefs)

    # ── LỌC TARGET ──────────────────────────────────────────
    def build_target(link_phong: bool, link_thang: bool) -> pd.DataFrame:
        """Lọc df_target theo Phòng/Tháng — mỗi bộ lọc bật/tắt riêng theo link tương ứng.
        Phân loại luôn áp dụng (không có toggle riêng)."""
        d = df_target.copy()
        if link_phong and sel_phong and has_phong:
            d = d[d[TG_PHONG].isin(sel_phong)]
        if sel_pl is not None and has_phanloai:
            d = d[d[TG_PHANLOAI].isin(sel_pl)]
        if link_thang and sel_thang and has_thang:
            d = d[d[TG_THANG].isin(sel_thang)]
        return d

    def completion_pct_by_target(target_ids, link_thang: bool) -> dict:
        """
        Tính % hoàn thành ĐỘNG cho từng TARGETID từ sheet chi tiết — khớp cách Looker Studio
        đang tính: (số dòng Trạng thái = Đúng kế hoạch/Vượt kế hoạch) / tổng số dòng khớp
        TARGETID đó, lọc theo "Tháng (chi tiết)" đang chọn nếu link_thang=True.
        """
        if not ok_detail or DT_TARGET_ID not in df_detail.columns or DT_TRANGTHAI not in df_detail.columns:
            return {}
        d = df_detail.copy()
        if link_thang and sel_dt_thang:
            d = d[d[DT_THANG].isin(sel_dt_thang)]
        d = d[d[DT_TARGET_ID].isin(target_ids)]
        result = {}
        for tid, grp in d.groupby(DT_TARGET_ID):
            hoan_thanh = grp[DT_TRANGTHAI].isin(HOAN_THANH_STATUSES).sum()
            result[tid] = hoan_thanh / len(grp) * 100 if len(grp) else float("nan")
        return result

    if ok_target:
        dft_for_table = build_target(link_mt_phong, link_mt_thang)

        st.markdown("#### Mục tiêu, nhiệm vụ và mô tả công việc theo Owner")
        st.caption(
            f"{link_badge(link_mt_phong)} (Phòng) · "
            f"{link_badge(link_mt_thang)} (Tháng)"
        )

        # Tính % hoàn thành ĐỘNG từ sheet chi tiết (giống Looker Studio) —
        # thay vì đọc cột "Mức độ thực hiện" tĩnh trong sheet target (không đáng tin cậy,
        # không cập nhật đồng bộ theo dữ liệu chi tiết thực tế)
        if has_mdth and TG_ID in dft_for_table.columns:
            pct_map = completion_pct_by_target(dft_for_table[TG_ID].tolist(), link_mt_thang)
            dft_for_table = dft_for_table.copy()
            dft_for_table[TG_MDTH] = dft_for_table[TG_ID].map(pct_map)

        cols_show = []
        if TG_CONGVIEC in dft_for_table.columns: cols_show.append(TG_CONGVIEC)
        if TG_OWNER    in dft_for_table.columns: cols_show.append(TG_OWNER)
        if TG_DVL      in dft_for_table.columns: cols_show.append(TG_DVL)
        if has_mdth:                              cols_show.append(TG_MDTH)

        dft_disp = dft_for_table[cols_show].copy() if cols_show else dft_for_table.copy()

        rename_t = {
            TG_CONGVIEC: "Tên công việc",
            TG_OWNER:    "Owner",
            TG_DVL:      "Đơn vị đo lường",
            TG_MDTH:     "Mức độ thực hiện (%)",
        }
        dft_disp = dft_disp.rename(columns={k: v for k, v in rename_t.items() if k in dft_disp.columns})

        # Đảm bảo là số float sạch — giữ NaN nếu không có dòng chi tiết nào khớp
        # (df_to_html sẽ hiện "—" cho NaN thay vì hiểu nhầm thành 0%)
        if has_mdth and "Mức độ thực hiện (%)" in dft_disp.columns:
            dft_disp["Mức độ thực hiện (%)"] = pd.to_numeric(
                dft_disp["Mức độ thực hiện (%)"], errors="coerce",
            )

        total_t = len(dft_disp)
        st.markdown(
            df_to_html(dft_disp, pct_col="Mức độ thực hiện (%)"),
            unsafe_allow_html=True,
        )
        st.caption(f"1 – {min(total_t, 100)} / {total_t} công việc")

    # ── LỌC DETAIL ──────────────────────────────────────────
    def build_detail(link_phong: bool, link_thang: bool) -> pd.DataFrame:
        """Lọc df_detail theo Tháng (chi tiết)/Phòng — mỗi bộ lọc bật/tắt riêng theo link tương ứng.
        Phòng lọc gián tiếp qua khóa quan hệ TARGETID (TG_ID ở target ↔ DT_TARGET_ID ở detail)."""
        d = df_detail.copy()
        if link_thang and sel_dt_thang:
            d = d[d[DT_THANG].isin(sel_dt_thang)]
        if (link_phong and sel_phong and has_phong
                and TG_ID in df_target.columns and DT_TARGET_ID in d.columns):
            target_ids_phong = df_target.loc[df_target[TG_PHONG].isin(sel_phong), TG_ID]
            d = d[d[DT_TARGET_ID].isin(target_ids_phong)]
        return d

    if ok_detail:
        dfd_for_table = build_detail(link_ct_phong, link_ct_thang)

        st.markdown("#### Chi tiết mục tiêu và công việc đã thực hiện theo tháng")
        st.caption(
            f"{link_badge(link_ct_phong)} (Phòng) · "
            f"{link_badge(link_ct_thang)} (Tháng)"
        )

        cols_detail = []
        for c in [DT_CONGVIEC, DT_CHITIET, DT_THANG, DT_TRANGTHAI, DT_KETQUA, DT_TIEPTHEO]:
            if c in dfd_for_table.columns:
                cols_detail.append(c)

        dfd_disp = dfd_for_table[cols_detail].copy() if cols_detail else dfd_for_table.copy()
        rename_d = {
            DT_CONGVIEC:  "Tên công việc",
            DT_CHITIET:   "Chi tiết công việc con",
            DT_THANG:     "Tháng báo cáo",
            DT_TRANGTHAI: "Trạng thái",
            DT_KETQUA:    "Kết quả / Vấn đề",
            DT_TIEPTHEO:  "Việc tiếp theo / KPI",
        }
        dfd_disp = dfd_disp.rename(columns={k: v for k, v in rename_d.items() if k in dfd_disp.columns})

        import re

        def _fmt_month(val):
            s = str(val)
            m = re.search(r'[-/](\d{1,2})[-/]', s)
            if m:
                return f"Tháng {int(m.group(1))}"
            m2 = re.search(r'(\d{4})-(\d{2})', s)
            if m2:
                return f"Tháng {int(m2.group(2))}"
            return s

        thang_col = next(
            (c for c in dfd_disp.columns
             if "tháng" in c.lower() or "thang" in c.lower()),
            None,
        )
        if thang_col:
            dfd_disp[thang_col] = dfd_disp[thang_col].apply(_fmt_month)

        total_d = len(dfd_disp)
        st.markdown(
            df_to_html(dfd_disp, status_col="Trạng thái"),
            unsafe_allow_html=True,
        )
        st.caption(f"1 – {min(total_d, 100)} / {total_d} bản ghi")
