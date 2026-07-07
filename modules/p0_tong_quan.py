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
    month_display_label, month_sort_key, MODEBAR_CONFIG, apply_responsive,
)


def _sum(d: dict) -> float:
    return sum(d.values()) if d else 0.0


def link_badge(linked: bool) -> str:
    if linked:
        return "🔗 *Theo bộ lọc tháng*"
    return "📌 *Toàn bộ thời gian*"


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

        with st.expander("🔗 Liên kết bộ lọc tháng", expanded=False):
            st.caption("Chọn biểu đồ bị ảnh hưởng khi đổi tháng:")
            link_kpi     = st.checkbox("KPI Cards",        value=True,  key="link_kpi")
            link_wf      = st.checkbox("P&L Waterfall",    value=True,  key="link_wf")
            link_donut   = st.checkbox("Cơ cấu Doanh thu", value=False, key="link_donut")
            link_bar_pnl = st.checkbox("P&L theo BU",      value=False, key="link_bar")

            st.caption("Chọn biểu đồ bị ảnh hưởng khi đổi đơn vị (BU):")
            link_kpi_bu = st.checkbox("KPI Cards (BU)",     value=True, key="link_p0_kpi_bu")
            link_wf_bu  = st.checkbox("Waterfall (BU)",     value=True, key="link_p0_wf_bu")

        sel_buses = st.multiselect(
            "Chọn đơn vị",
            options=all_bus,
            default=all_bus,
            key="p0_bu",
        )

    if not sel_months or not sel_buses:
        st.warning("Vui lòng chọn ít nhất 1 tháng và 1 đơn vị.")
        return

    # Tất cả tháng có data (không lọc) — dùng cho biểu đồ KHÔNG liên kết bộ lọc tháng
    all_active_months = [month_map[l] for l in all_labels]

    def get_months(linked: bool) -> list:
        return sel_months if linked else all_active_months

    def get_bu(linked: bool) -> list:
        return sel_buses if linked else all_bus

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

    # ── LẤY SỐ LIỆU: KPI CARDS (theo link_kpi / link_kpi_bu) ──
    kpi_months = get_months(link_kpi)
    kpi_bu     = get_bu(link_kpi_bu)
    dt_tt     = _sum(get_metric(df,      STT_DT,     kpi_months, kpi_bu))
    dt_kh     = _sum(get_metric_plan(df, STT_DT_KH,  kpi_months, kpi_bu))  # STT=5 có KH
    ln_tt     = _sum(get_metric(df,      STT_LN_GOP, kpi_months, kpi_bu))
    ln_kh     = _sum(get_metric_plan(df, STT_LN_GOP, kpi_months, kpi_bu))
    hd_tt     = _sum(get_metric(df,      STT_LNHDKD, kpi_months, kpi_bu))
    hd_kh     = _sum(get_metric_plan(df, STT_LNHDKD, kpi_months, kpi_bu))
    st_tt     = _sum(get_metric(df,      STT_LNST,   kpi_months, kpi_bu))
    st_kh     = _sum(get_metric_plan(df, STT_LNST,   kpi_months, kpi_bu))

    gm_pct  = ln_tt / dt_tt * 100 if dt_tt else 0.0
    npm_pct = st_tt / dt_tt * 100 if dt_tt else 0.0

    # ── LẤY SỐ LIỆU: WATERFALL (theo link_wf / link_wf_bu — độc lập với KPI Cards) ──
    wf_months = get_months(link_wf)
    wf_bu     = get_bu(link_wf_bu)
    dt_tt_wf     = _sum(get_metric(df,      STT_DT,     wf_months, wf_bu))
    ln_tt_wf     = _sum(get_metric(df,      STT_LN_GOP, wf_months, wf_bu))
    hd_tt_wf     = _sum(get_metric(df,      STT_LNHDKD, wf_months, wf_bu))
    st_tt_wf     = _sum(get_metric(df,      STT_LNST,   wf_months, wf_bu))
    gvhb_tt_wf   = _sum(get_metric(df,      STT_GVHB,   wf_months, wf_bu))
    cpqldn_tt_wf = _sum(get_metric(df,      STT_CPQLDN, wf_months, wf_bu))

    # ── KPI CARDS ────────────────────────────────────────────
    def _delta_text(tt: float, kh: float) -> str:
        if kh <= 0:
            return ""
        pct = tt / kh * 100
        arrow = "▲" if pct >= 100 else "▼"
        return f"{arrow} {pct:.1f}% KH"

    fmt_dt, fmt_gop, fmt_hd, fmt_st = (
        fmt_ty(dt_tt), fmt_ty(ln_tt), fmt_ty(hd_tt), fmt_ty(st_tt),
    )
    delta_dt  = _delta_text(dt_tt, dt_kh)
    delta_gop = _delta_text(ln_tt, ln_kh)
    delta_hd  = _delta_text(hd_tt, hd_kh)
    delta_st  = _delta_text(st_tt, st_kh)

    st.caption(link_badge(link_kpi))
    cols = st.columns(4)
    card_data = [
        ("🔥 Doanh thu",   fmt_dt,  delta_dt,  ""),
        ("📊 LN Gộp",      fmt_gop, delta_gop, f"GM: {gm_pct:.1f}%"),
        ("⚙️ LN HĐKD",    fmt_hd,  delta_hd,  ""),
        ("✅ LN Sau Thuế", fmt_st,  delta_st,  f"NPM: {npm_pct:.1f}%"),
    ]
    for col, (label, value, delta, sub) in zip(cols, card_data):
        delta_color = "#22c55e" if delta and "▲" in delta else "#ef4444"
        col.markdown(f"""
        <div style="background:white;border:1px solid #e2e8f0;
                    border-radius:10px;padding:14px 16px;
                    height:120px;box-sizing:border-box;
                    display:flex;flex-direction:column;
                    justify-content:space-between;">
          <div style="font-size:11px;color:#94a3b8">{label}</div>
          <div style="font-size:22px;font-weight:700;color:#1e293b;
                      line-height:1.2">{value}</div>
          <div style="min-height:32px;display:flex;flex-direction:column;
                      gap:2px;justify-content:flex-end">
            <div style="font-size:11px;color:#64748b">{sub}</div>
            <div style="font-size:11px;color:{delta_color}">{delta}</div>
          </div>
        </div>""", unsafe_allow_html=True)

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
        st.caption(link_badge(link_wf))
        taxes_etc = (st_tt_wf - hd_tt_wf) / 1e9     # LNST - LNHĐKD (thường âm)

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "total",
                     "relative", "total", "relative", "total"],
            x=["Doanh thu", "(−) Giá vốn", "LN Gộp",
               "(−) CP QLDN", "LNHĐKD", "Thuế & khác", "LNST"],
            y=[dt_tt_wf/1e9, -gvhb_tt_wf/1e9, None,
               -cpqldn_tt_wf/1e9, None, taxes_etc, None],
            text=[
                fmt_ty(dt_tt_wf), fmt_ty(gvhb_tt_wf), fmt_ty(ln_tt_wf),
                fmt_ty(cpqldn_tt_wf), fmt_ty(hd_tt_wf),
                fmt_ty(abs(taxes_etc * 1e9)), fmt_ty(st_tt_wf),
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
        fig_wf = apply_responsive(fig_wf)
        st.plotly_chart(fig_wf, use_container_width=True, config=MODEBAR_CONFIG)

    with col_pie:
        st.caption(link_badge(link_donut))
        # Donut luôn dùng toàn bộ BU, không phụ thuộc bộ lọc "Chọn đơn vị"
        dt_by_bu  = get_metric_by_bu(df, STT_DT, get_months(link_donut), all_bus)
        dt_labels = [bu for bu, v in dt_by_bu.items() if v > 0]
        dt_vals   = [v  for v  in dt_by_bu.values() if v > 0]

        if dt_vals:
            total = sum(dt_vals)

            fig_pie = go.Figure(go.Pie(
                labels=dt_labels, values=dt_vals,
                hole=0.38,
                textinfo='text',
                textposition='inside',
                insidetextorientation='radial',
                textfont=dict(size=9),
                showlegend=False,
                pull=[0.03 if (v / sum(dt_vals) * 100) < 3 else 0 for v in dt_vals],
                hovertemplate="%{label}<br>%{value:,.0f}<br>%{percent}<extra></extra>",
            ))

            new_texts = []
            for v, lbl in zip(dt_vals, dt_labels):
                pct = v / total * 100 if total > 0 else 0
                new_texts.append("" if pct < 3 else f"{lbl}<br>{pct:.1f}%")
            fig_pie.update_traces(text=new_texts, textinfo='text')

            fig_pie.update_layout(
                title=dict(text="Cơ cấu Doanh thu theo Đơn vị", font=dict(size=13)),
                height=300, margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False, paper_bgcolor='white', plot_bgcolor='white',
            )
            fig_pie = apply_responsive(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True, config=MODEBAR_CONFIG)
        else:
            st.info("Không có dữ liệu doanh thu.")

    # ── BAR NGANG — LN Sau Thuế theo đơn vị ─────────────────
    # Bar chart luôn dùng toàn bộ BU, không phụ thuộc bộ lọc "Chọn đơn vị"
    st.caption(link_badge(link_bar_pnl))
    lnst_by_bu_all = get_metric_by_bu(df, STT_LNST, get_months(link_bar_pnl), all_bus)
    if lnst_by_bu_all:
        # Sort ascending: -7.41 đầu (dưới cùng), 13.85 cuối (trên cùng)
        raw_vals   = [v / 1e9 for v in lnst_by_bu_all.values()]
        raw_labels = list(lnst_by_bu_all.keys())
        pairs = list(zip(raw_vals, raw_labels))
        pairs.sort(key=lambda x: x[0])
        bar_x      = [p[0] for p in pairs]
        bar_labels = [p[1] for p in pairs]
        bar_colors = ["#22c55e" if v >= 0 else "#ef4444" for v in bar_x]
        bar_texts  = [f"{v:.2f} Tỷ" for v in bar_x]

        max_abs = max(abs(v) for v in bar_x) if bar_x else 1
        text_positions = [
            "outside" if abs(v) < max_abs * 0.15 else "inside"
            for v in bar_x
        ]
        text_colors = [
            "#1e293b" if pos == "outside" else "white"
            for pos in text_positions
        ]

        x_min = min(bar_x) if bar_x else 0
        x_max = max(bar_x) if bar_x else 1
        x_range = [x_min * 1.18 if x_min < 0 else 0, x_max * 1.18]

        fig_bar = go.Figure(go.Bar(
            x=bar_x, y=bar_labels, orientation="h",
            marker_color=bar_colors,
            text=bar_texts,
            textposition=text_positions,
            insidetextanchor="start",
            textfont=dict(size=10, color=text_colors),
        ))
        fig_bar.update_traces(cliponaxis=False)
        fig_bar.update_layout(**CHART_LAYOUT)
        fig_bar.update_layout(
            title=dict(text="P&L theo BU", font=dict(size=13), x=0, xanchor="left"),
            margin=dict(l=150, r=60, t=40, b=30),
            height=max(280, len(bar_labels) * 38 + 60),
            xaxis=dict(range=x_range),
        )
        apply_chart_style(fig_bar, horizontal=True)
        fig_bar = apply_responsive(fig_bar)
        st.plotly_chart(fig_bar, use_container_width=True, config=MODEBAR_CONFIG)
