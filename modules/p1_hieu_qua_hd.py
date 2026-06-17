# =============================================================
# modules/p1_hieu_qua_hd.py — Trang 1: Hiệu quả hoạt động
# =============================================================

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from config import (
    FG_BU, FG_DATETIME,
    STT_DT, STT_DT_KH, STT_GVHB, STT_LN_GOP,
    STT_LNHDKD, STT_LNST, STT_CPQL_LIST,
    COLOR_ACTUAL, COLOR_PLAN, COLOR_OK, COLOR_INFO,
)
from data_loader import get_metric, get_metric_plan, get_metric_multi, get_metric_stt_range
from utils import (
    fmt_ty, fmt_pct, CHART_LAYOUT, apply_chart_style,
    month_display_label, month_sort_key, smart_textpos,
    fix_chart_yrange_and_labels, MODEBAR_CONFIG, apply_responsive,
)


def render(df: pd.DataFrame):
    # Active months: tháng có DT thực tế > 0
    all_months = sorted(df[FG_DATETIME].dropna().unique().tolist())
    all_bus    = sorted(df[FG_BU].dropna().unique().tolist())
    dt_all     = get_metric(df, STT_DT, all_months, all_bus)
    active_months = sorted([m for m, v in dt_all.items() if v > 0])
    if not active_months:
        active_months = all_months

    month_map     = {month_display_label(m): m for m in all_months}
    active_labels = [month_display_label(m) for m in active_months]
    all_labels    = sorted(month_map.keys(), key=month_sort_key)

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Bộ lọc — Trang 1")
        sel_labels = st.multiselect(
            "Tháng", all_labels, default=active_labels, key="p1_months",
        )
        sel_months = [month_map[l] for l in sel_labels]
        sel_buses = st.multiselect(
            "Đơn vị kinh doanh", options=all_bus, default=all_bus,
            key="p1_bu",
        )

    if not sel_months or not sel_buses:
        st.warning("Vui lòng chọn ít nhất 1 tháng và 1 đơn vị.")
        return

    months_sorted = sorted(sel_months)
    x_labels = [month_display_label(m) for m in months_sorted]
    n = len(x_labels)

    def by_month(stt, plan=False):
        fn = get_metric_plan if plan else get_metric
        d = fn(df, stt, sel_months, sel_buses)
        return [d.get(m, 0) for m in months_sorted]

    # Fetch data
    dt_vals      = by_month(STT_DT)
    gvhb_vals    = by_month(STT_GVHB)
    gvhb_kh      = by_month(STT_GVHB,   plan=True)
    ln_gop_vals  = by_month(STT_LN_GOP)
    ln_gop_kh    = by_month(STT_LN_GOP,  plan=True)
    lnhdkd_vals  = by_month(STT_LNHDKD)
    lnst_vals    = by_month(STT_LNST)
    lnst_kh      = by_month(STT_LNST,    plan=True)

    # DT KH dùng STT=5 (Doanh thu thuần — STT=1 không có KH trong sheet)
    dt_kh_d    = get_metric_plan(df, STT_DT_KH, sel_months, sel_buses)
    dt_kh_vals = [dt_kh_d.get(m, 0) for m in months_sorted]

    # LNHDKD KH = LN Gộp KH − CPQL KH (derived, vì STT 146 không có KH)
    gp_kh_d    = get_metric_plan(df, STT_LN_GOP, sel_months, sel_buses)
    cpql_kh_d  = get_metric_multi(df, STT_CPQL_LIST, sel_months, sel_buses, plan=True)
    lnhdkd_kh  = [gp_kh_d.get(m, 0) - cpql_kh_d.get(m, 0) for m in months_sorted]

    # ── KPI CARDS ─────────────────────────────────────────────
    tot_dt     = sum(dt_vals)
    tot_lnst   = sum(lnst_vals)
    tot_ln_gop = sum(ln_gop_vals)
    gm_pct  = tot_ln_gop / tot_dt * 100 if tot_dt else 0.0
    npm_pct = tot_lnst   / tot_dt * 100 if tot_dt else 0.0

    st.markdown("#### Lũy kế kỳ đã chọn")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Doanh thu",   fmt_ty(tot_dt))
    c2.metric("LN Sau Thuế", fmt_ty(tot_lnst))
    c3.metric("Gross Margin", fmt_pct(gm_pct))
    c4.metric("Net Margin",   fmt_pct(npm_pct))

    st.divider()

    # ── HELPER: LINE CHART ────────────────────────────────────
    def line_tt_kh(y_tt_raw, y_kh_raw, title,
                   yaxis="Tỷ đồng", height=320, color=COLOR_ACTUAL):
        """Vẽ line chart TT vs KH — y normalize sang tỷ, hover đầy đủ."""
        y_tt = [v / 1e9 for v in y_tt_raw]
        y_kh = [v / 1e9 for v in y_kh_raw]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_labels, y=y_tt, name="Thực tế",
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=1.2),
            marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(30, 58, 95, 0.12)",
            hovertemplate="<b>%{x}</b><br>Thực tế: %{y:,.1f} Tỷ<extra></extra>",
        ))
        if any(v != 0 for v in y_kh):
            fig.add_trace(go.Scatter(
                x=x_labels, y=y_kh, name="Kế hoạch",
                mode="lines+markers",
                line=dict(color=COLOR_PLAN, width=1.8, dash="dot",
                          shape="spline", smoothing=1.2),
                marker=dict(size=5),
                hovertemplate="<b>%{x}</b><br>Kế hoạch: %{y:,.1f} Tỷ<extra></extra>",
            ))
        fig.update_layout(
            **CHART_LAYOUT, height=height,
            title=dict(text=title, font=dict(size=13)),
            yaxis_title=yaxis,
            hovermode="x unified",
        )
        fix_chart_yrange_and_labels(fig, x_labels, y_tt, y_kh, value_fmt="ty")
        return fig

    # ── HELPER: BAR CHART ─────────────────────────────────────
    def bar_tt_kh(y_tt_raw, y_kh_raw, title, height=320):
        y_tt = [v / 1e9 for v in y_tt_raw]
        y_kh = [v / 1e9 for v in y_kh_raw]

        all_bar_vals = [v for v in y_tt + y_kh if v != 0]
        y_max = max(all_bar_vals) if all_bar_vals else 1
        y_min = min(all_bar_vals) if all_bar_vals else 0
        y_range = [y_min * 1.18 if y_min < 0 else 0, y_max * 1.18]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_labels, y=y_tt, name="Thực tế",
            marker_color=COLOR_ACTUAL,
            text=[f"{v:.1f}" if v else "" for v in y_tt],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{x}</b><br>Thực tế: %{y:,.1f} Tỷ<extra></extra>",
        ))
        if any(v != 0 for v in y_kh):
            fig.add_trace(go.Bar(
                x=x_labels, y=y_kh, name="Kế hoạch",
                marker_color=COLOR_PLAN,
                text=[f"{v:.1f}" if v else "" for v in y_kh],
                textposition="outside", textfont=dict(size=10),
                hovertemplate="<b>%{x}</b><br>Kế hoạch: %{y:,.1f} Tỷ<extra></extra>",
            ))
        fig.update_layout(
            **CHART_LAYOUT, barmode="group", height=height,
            title=dict(text=title, font=dict(size=13)),
            yaxis_title="Tỷ đồng",
            hovermode="x unified",
        )
        fig.update_xaxes(range=[-0.5, n - 0.5])
        fig.update_yaxes(range=y_range)
        apply_chart_style(fig)
        return fig

    # ── A. Doanh thu TT vs KH ─────────────────────────────────
    fig_dt = line_tt_kh(dt_vals, dt_kh_vals, "Doanh thu bán hàng theo thời gian")
    fig_dt = apply_responsive(fig_dt)
    st.plotly_chart(fig_dt, use_container_width=True, config=MODEBAR_CONFIG)

    # ── B. LN Gộp — 1 hàng ───────────────────────────────────
    fig_ln_gop = line_tt_kh(ln_gop_vals, ln_gop_kh, "Lợi nhuận gộp", color=COLOR_OK, height=300)
    fig_ln_gop = apply_responsive(fig_ln_gop)
    st.plotly_chart(fig_ln_gop, use_container_width=True, config=MODEBAR_CONFIG)

    # ── B2. LN HĐKD — 1 hàng ─────────────────────────────────
    fig_lnhdkd = line_tt_kh(
        lnhdkd_vals, lnhdkd_kh,
        "LN Hoạt động kinh doanh (KH = LN Gộp KH − CPQL KH)",
        color=COLOR_OK, height=300,
    )
    fig_lnhdkd = apply_responsive(fig_lnhdkd)
    st.plotly_chart(fig_lnhdkd, use_container_width=True, config=MODEBAR_CONFIG)

    # ── C. GVHB TT vs KH (bar) ───────────────────────────────
    fig_gvhb = bar_tt_kh(gvhb_vals, gvhb_kh, "Giá vốn hàng bán (GVHB) theo thời gian")
    fig_gvhb = apply_responsive(fig_gvhb)
    st.plotly_chart(fig_gvhb, use_container_width=True, config=MODEBAR_CONFIG)

    # ── C2. % GVHB — chỉ show tháng có data (Cách A) ─────────
    # Lọc về các tháng có DT > 0 để bar đủ rộng trên mobile
    act_mask = [d > 0 for d in dt_vals]
    ax       = [x for x, ok in zip(x_labels, act_mask) if ok]
    a_dt     = [v for v, ok in zip(dt_vals,    act_mask) if ok]
    a_dt_kh  = [v for v, ok in zip(dt_kh_vals, act_mask) if ok]
    a_gvhb   = [v for v, ok in zip(gvhb_vals,  act_mask) if ok]
    a_gvhb_kh= [v for v, ok in zip(gvhb_kh,    act_mask) if ok]

    gvhb_mn_d  = get_metric_stt_range(df, 7, 10, sel_months, sel_buses)
    a_gvhb_mn  = [gvhb_mn_d.get(m, 0) for m, ok in zip(months_sorted, act_mask) if ok]
    a_gvhb_vh  = [g - mn for g, mn in zip(a_gvhb, a_gvhb_mn)]

    pct_kh   = [gk / dk * 100 if dk else 0 for gk, dk in zip(a_gvhb_kh, a_dt_kh)]
    pct_mn   = [mn / d * 100  if d  else 0 for mn, d  in zip(a_gvhb_mn, a_dt)]
    pct_vh   = [vh / d * 100  if d  else 0 for vh, d  in zip(a_gvhb_vh, a_dt)]
    pct_tot  = [g  / d * 100  if d  else 0 for g,  d  in zip(a_gvhb,    a_dt)]
    na = len(ax)

    fig_gvhb_pct = go.Figure()
    for name, vals, color in [
        ("% GVHB/DT kế hoạch",     pct_kh,  "#f97316"),
        ("% GVHB mua ngoài/DT TT", pct_mn,  COLOR_ACTUAL),
        ("% GVHB vận hành/DT TT",  pct_vh,  COLOR_OK),
        ("% GVHB tổng/DT TT",      pct_tot, "#854d0e"),
    ]:
        fig_gvhb_pct.add_trace(go.Bar(
            x=ax, y=vals, name=name,
            marker_color=color,
            text=[f"{v:.1f}%" for v in vals],
            textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>",
        ))
    fig_gvhb_pct.update_layout(
        **CHART_LAYOUT, barmode="group", height=400,
        title=dict(text="% Giá vốn hàng bán / Doanh thu", font=dict(size=13)),
        yaxis_title="%",
        hovermode="x unified",
    )
    fig_gvhb_pct.update_xaxes(range=[-0.5, na - 0.5])
    apply_chart_style(fig_gvhb_pct)
    all_pct_vals = pct_kh + pct_mn + pct_vh + pct_tot
    pct_y_max = max((v for v in all_pct_vals if v > 0), default=100)
    fig_gvhb_pct.update_yaxes(range=[0, pct_y_max * 1.18])
    fig_gvhb_pct = apply_responsive(fig_gvhb_pct)
    st.plotly_chart(fig_gvhb_pct, use_container_width=True, config=MODEBAR_CONFIG)

    # ── D. LN Sau Thuế ───────────────────────────────────────
    fig_lnst = line_tt_kh(lnst_vals, lnst_kh, "LN Sau Thuế", color=COLOR_INFO)
    fig_lnst = apply_responsive(fig_lnst)
    st.plotly_chart(fig_lnst, use_container_width=True, config=MODEBAR_CONFIG)

