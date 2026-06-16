# =============================================================
# modules/p0_tong_quan.py — Trang 0: Tổng quan P&L
# =============================================================

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from config import (
    FG_BU, FG_DATETIME,
    STT_DT, STT_DT_KH, STT_GVHB, STT_LN_GOP, STT_CPQLDN, STT_LNHDKD, STT_LNST,
    COLOR_OK, COLOR_DANGER, EXCLUDE_FROM_ALERT,
)
from data_loader import get_metric, get_metric_by_bu, get_metric_plan
from utils import (
    fmt_ty, CHART_LAYOUT, CHART_LAYOUT_NO_MARGIN, apply_chart_style,
    month_display_label, month_sort_key,
)


def _sum(d: dict) -> float:
    return sum(d.values()) if d else 0.0


def render(df: pd.DataFrame):
    all_months = sorted(df[FG_DATETIME].dropna().unique().tolist())
    all_bus    = sorted(df[FG_BU].dropna().unique().tolist())

    # Tháng có DT thực tế > 0
    dt_all = get_metric(df, STT_DT, all_months, all_bus)
    active_months = sorted([m for m, v in dt_all.items() if v > 0])
    if not active_months:
        active_months = all_months

    # Mapping label → datetime string
    month_map     = {month_display_label(m): m for m in all_months}
    active_labels = [month_display_label(m) for m in active_months]
    all_labels    = sorted(month_map.keys(), key=month_sort_key)

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Bộ lọc — Tổng quan")

        sel_labels = st.multiselect(
            "Chọn tháng", all_labels,
            default=active_labels,
            key="p0_months",
        )
        sel_months = [month_map[l] for l in sel_labels]
        sel_buses = st.multiselect(
            "Chọn đơn vị",
            options=all_bus,
            default=all_bus,
            key="p0_bu",
        )

    if not sel_months or not sel_buses:
        st.warning("Vui lòng chọn ít nhất 1 tháng và 1 đơn vị.")
        return

    # ── BADGE PERIOD ─────────────────────────────────────────
    first = month_display_label(sorted(sel_months)[0])
    last  = month_display_label(sorted(sel_months)[-1])
    n     = len(sel_months)
    badge = f"Lũy kế {first}–{last}/2026  ·  {n} tháng"
    st.markdown(
        f"<div style='display:inline-block; background:#eff6ff; color:#1d4ed8;"
        f"border:1px solid #bfdbfe; border-radius:999px; padding:4px 14px;"
        f"font-size:12px; font-weight:500; margin-bottom:12px'>{badge}</div>",
        unsafe_allow_html=True,
    )

    # ── LẤY SỐ LIỆU ──────────────────────────────────────────
    dt_tt     = _sum(get_metric(df,      STT_DT,     sel_months, sel_buses))
    dt_kh     = _sum(get_metric_plan(df, STT_DT_KH,  sel_months, sel_buses))  # STT=5 có KH
    ln_tt     = _sum(get_metric(df,      STT_LN_GOP, sel_months, sel_buses))
    ln_kh     = _sum(get_metric_plan(df, STT_LN_GOP, sel_months, sel_buses))
    hd_tt     = _sum(get_metric(df,      STT_LNHDKD, sel_months, sel_buses))
    hd_kh     = _sum(get_metric_plan(df, STT_LNHDKD, sel_months, sel_buses))
    st_tt     = _sum(get_metric(df,      STT_LNST,   sel_months, sel_buses))
    st_kh     = _sum(get_metric_plan(df, STT_LNST,   sel_months, sel_buses))
    gvhb_tt   = _sum(get_metric(df,      STT_GVHB,   sel_months, sel_buses))
    cpqldn_tt = _sum(get_metric(df,      STT_CPQLDN, sel_months, sel_buses))

    gm_pct  = ln_tt / dt_tt * 100 if dt_tt else 0.0
    npm_pct = st_tt / dt_tt * 100 if dt_tt else 0.0

    # ── KPI CARDS ────────────────────────────────────────────
    def _kh_html(tt: float, kh: float) -> str:
        if kh <= 0:
            return ""
        pct = tt / kh * 100
        col   = "#16a34a" if pct >= 100 else "#dc2626"
        arrow = "▲" if pct >= 100 else "▼"
        return (
            f"<p style='margin:3px 0 0; font-size:12px;"
            f"font-weight:500; color:{col}'>{arrow} {pct:.1f}% KH</p>"
        )

    def _card(icon: str, label: str, value: float,
              extra: str = "", tt: float = 0.0, kh: float = 0.0) -> str:
        extra_h = (
            f"<p style='margin:3px 0 0; font-size:11px; color:#64748b'>{extra}</p>"
            if extra else ""
        )
        return (
            f"<div style='background:white; border:1px solid #e2e8f0;"
            f"border-radius:10px; padding:14px 16px;'>"
            f"<p style='margin:0 0 4px; font-size:11px; color:#94a3b8'>{icon} {label}</p>"
            f"<p style='margin:0; font-size:22px; font-weight:600; color:#1e293b'>"
            f"{fmt_ty(value)}</p>"
            f"{extra_h}"
            f"{_kh_html(tt, kh)}"
            f"</div>"
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        _card("💰", "Doanh thu",   dt_tt, tt=dt_tt, kh=dt_kh),
        unsafe_allow_html=True,
    )
    c2.markdown(
        _card("📊", "LN Gộp", ln_tt, extra=f"GM: {gm_pct:.1f}%", tt=ln_tt, kh=ln_kh),
        unsafe_allow_html=True,
    )
    c3.markdown(
        _card("⚙️", "LN HĐKD",    hd_tt, tt=hd_tt, kh=hd_kh),
        unsafe_allow_html=True,
    )
    c4.markdown(
        _card("✅", "LN Sau Thuế", st_tt, extra=f"NPM: {npm_pct:.1f}%", tt=st_tt, kh=st_kh),
        unsafe_allow_html=True,
    )

    # ── ALERT — đơn vị lỗ ────────────────────────────────────
    lnst_by_bu = get_metric_by_bu(df, STT_LNST, sel_months, sel_buses)
    loss_items = sorted(
        [(bu, v) for bu, v in lnst_by_bu.items()
         if v < 0 and bu not in EXCLUDE_FROM_ALERT],
        key=lambda x: x[1],
    )
    if loss_items:
        loss_lines = "".join(
            f"<li><b>{bu}</b>: {v/1e9:.2f} Tỷ</li>"
            for bu, v in loss_items
        )
        st.markdown(
            f"<div style='background:#fef2f2; border:1px solid #fecaca;"
            f"border-radius:8px; padding:12px 16px; margin:16px 0'>"
            f"<b style='color:#991b1b'>⚠️ Đơn vị lỗ trong kỳ</b>"
            f"<ul style='margin:8px 0 0; color:#7f1d1d; font-size:13px'>"
            f"{loss_lines}</ul></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── ROW: Waterfall P&L + Donut ───────────────────────────
    col_wf, col_pie = st.columns(2)

    with col_wf:
        taxes_etc = (st_tt - hd_tt) / 1e9     # LNST - LNHĐKD (thường âm)

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "total",
                     "relative", "total", "relative", "total"],
            x=["Doanh thu", "(−) Giá vốn", "LN Gộp",
               "(−) CP QLDN", "LNHĐKD", "Thuế & khác", "LNST"],
            y=[dt_tt/1e9, -gvhb_tt/1e9, None,
               -cpqldn_tt/1e9, None, taxes_etc, None],
            text=[
                fmt_ty(dt_tt), fmt_ty(gvhb_tt), fmt_ty(ln_tt),
                fmt_ty(cpqldn_tt), fmt_ty(hd_tt),
                fmt_ty(abs(taxes_etc * 1e9)), fmt_ty(st_tt),
            ],
            textposition="outside",
            increasing=dict(marker_color="#22c55e"),
            decreasing=dict(marker_color="#ef4444"),
            totals=dict(marker_color="#1e3a5f"),
            connector=dict(line=dict(color="#cbd5e1", width=1)),
        ))
        fig_wf.update_layout(
            **CHART_LAYOUT_NO_MARGIN,
            margin=dict(l=10, r=20, t=40, b=10),
            title=dict(text="P&L Waterfall (Tỷ đồng)", font=dict(size=13)),
            height=340, showlegend=False, yaxis_title="Tỷ đồng",
        )
        apply_chart_style(fig_wf)
        st.plotly_chart(fig_wf, use_container_width=True)

    with col_pie:
        dt_by_bu   = get_metric_by_bu(df, STT_DT, sel_months, sel_buses)
        pie_labels = [bu for bu, v in dt_by_bu.items() if v > 0]
        pie_values = [v  for v  in dt_by_bu.values() if v > 0]

        if pie_values:
            fig_pie = go.Figure(go.Pie(
                labels=pie_labels, values=pie_values,
                hole=0.42,
                textinfo="percent+label",
                textfont=dict(size=10),
                hovertemplate="%{label}<br>%{value:,.0f}<br>%{percent}<extra></extra>",
            ))
            fig_pie.update_layout(
                **CHART_LAYOUT_NO_MARGIN,
                margin=dict(l=10, r=10, t=40, b=10),
                title=dict(text="Cơ cấu Doanh thu theo Đơn vị", font=dict(size=13)),
                height=340, showlegend=False,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Không có dữ liệu doanh thu.")

    # ── BAR NGANG — LN Sau Thuế theo đơn vị ─────────────────
    if lnst_by_bu:
        bu_sorted  = sorted(lnst_by_bu.items(), key=lambda x: x[1], reverse=True)
        bar_labels = [bu for bu, _ in bu_sorted]
        bar_x      = [v / 1e9 for _, v in bu_sorted]
        bar_colors = [COLOR_OK if v >= 0 else COLOR_DANGER for _, v in bu_sorted]
        bar_texts  = [f"{v/1e9:.2f} Tỷ" for _, v in bu_sorted]

        fig_bar = go.Figure(go.Bar(
            x=bar_x, y=bar_labels, orientation="h",
            marker_color=bar_colors,
            text=bar_texts, textposition="inside",
            insidetextanchor="start",
            textfont=dict(size=10, color="white"),
        ))
        fig_bar.update_layout(**CHART_LAYOUT)
        fig_bar.update_layout(
            margin=dict(l=150, r=60, t=30, b=30),
            height=max(280, len(bar_labels) * 38 + 60),
        )
        apply_chart_style(fig_bar, horizontal=True)
        st.plotly_chart(fig_bar, use_container_width=True)
