# =============================================================
# modules/p2_cp_gian_tiep.py — Trang 2: Chi phí QLDN & gián tiếp
# CPQL = STT 82 (Chi phí QLDN) + STT 151 (Phân bổ CP gián tiếp)
# =============================================================

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from config import (
    FG_BU, FG_DATETIME, FG_STT, FG_NOI_DUNG,
    STT_DT, STT_DT_KH,
    STT_CPQL_LIST, STT_CPGT_FROM, STT_CPGT_TO,
    COLOR_ACTUAL, COLOR_PLAN,
)
from data_loader import get_metric, get_metric_plan, get_metric_multi, get_metric_stt_range
from utils import (
    fmt_ty, CHART_LAYOUT, apply_chart_style,
    month_display_label, month_sort_key, smart_textpos,
    fix_chart_yrange_and_labels, MODEBAR_CONFIG,
)


def render(df: pd.DataFrame):
    # Active months: tháng có DT thực tế > 0
    all_months    = sorted(df[FG_DATETIME].dropna().unique().tolist())
    all_bus       = sorted(df[FG_BU].dropna().unique().tolist())
    dt_all        = get_metric(df, STT_DT, all_months, all_bus)
    active_months = sorted([m for m, v in dt_all.items() if v > 0])
    if not active_months:
        active_months = all_months

    month_map     = {month_display_label(m): m for m in all_months}
    active_labels = [month_display_label(m) for m in active_months]
    all_labels    = sorted(month_map.keys(), key=month_sort_key)

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Bộ lọc — Trang 2")
        sel_labels = st.multiselect(
            "Tháng", all_labels, default=active_labels, key="p2_months",
        )
        sel_months = [month_map[l] for l in sel_labels]
        sel_buses = st.multiselect(
            "Đơn vị", options=all_bus, default=all_bus, key="p2_bu",
        )

    if not sel_months or not sel_buses:
        st.warning("Vui lòng chọn ít nhất 1 tháng và 1 đơn vị.")
        return

    months_sorted = sorted(sel_months)
    x_labels      = [month_display_label(m) for m in months_sorted]
    n             = len(x_labels)

    # ── LẤY DỮ LIỆU ─────────────────────────────────────────
    # CPQL = STT 82 + STT 151
    cp_d    = get_metric_multi(df, STT_CPQL_LIST, sel_months, sel_buses)
    cp_kh_d = get_metric_multi(df, STT_CPQL_LIST, sel_months, sel_buses, plan=True)
    dt_d    = get_metric(df, STT_DT,    sel_months, sel_buses)
    dt_kh_d = get_metric_plan(df, STT_DT_KH, sel_months, sel_buses)

    y_cp_tt  = [cp_d.get(m, 0)    for m in months_sorted]
    y_cp_kh  = [cp_kh_d.get(m, 0) for m in months_sorted]
    y_dt_tt  = [dt_d.get(m, 0)    for m in months_sorted]
    y_dt_kh  = [dt_kh_d.get(m, 0) for m in months_sorted]

    tot_cpql_tt = sum(cp_d.values())
    tot_cpql_kh = sum(cp_kh_d.values())

    # ── SECTION A: Progress bar màu động ────────────────────
    pct      = min(tot_cpql_tt / tot_cpql_kh, 1.5) if tot_cpql_kh > 0 else 0
    is_good  = tot_cpql_tt < tot_cpql_kh
    bar_col  = "#16a34a" if is_good else "#dc2626"
    txt_col  = "#14532d" if is_good else "#7f1d1d"
    bg_col   = "#f0fdf4" if is_good else "#fef2f2"
    label    = "✅ Đang tiết kiệm chi phí" if is_good else "⚠️ Đang vượt kế hoạch"

    st.markdown(f"""
    <div style="padding:16px 20px; background:{bg_col};
                border-radius:10px; margin-bottom:16px">
      <p style="margin:0 0 2px; font-size:13px; color:#64748b; font-weight:500">
        Chi phí QLDN (STT 82 + 151)
      </p>
      <p style="margin:0 0 4px; font-size:28px; font-weight:700; color:{txt_col}">
        {fmt_ty(tot_cpql_tt)}
      </p>
      <p style="margin:0 0 10px; font-size:13px; color:#64748b">
        {fmt_ty(tot_cpql_tt)} / {fmt_ty(tot_cpql_kh)} Kế hoạch
      </p>
      <div style="background:#e2e8f0; border-radius:6px; height:10px; overflow:hidden">
        <div style="width:{min(pct,1.0)*100:.1f}%; height:100%;
                    background:{bar_col}; border-radius:6px"></div>
      </div>
      <p style="margin:6px 0 0; font-size:12px; font-weight:600; color:{txt_col}">
        {label} — {pct*100:.1f}% kế hoạch
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── SECTION B: CPQL TT vs KH theo tháng ─────────────────
    fig_cp = go.Figure()
    fig_cp.add_trace(go.Scatter(
        x=x_labels, y=[v / 1e9 for v in y_cp_tt], name="Thực tế",
        mode="lines+markers+text",
        line=dict(color=COLOR_ACTUAL, width=2.5, shape="spline", smoothing=1.2),
        marker=dict(size=7),
        text=[f"{v/1e9:.1f}" if v else "" for v in y_cp_tt],
        textposition=smart_textpos(n),
        textfont=dict(size=10, color=COLOR_ACTUAL),
        fill="tozeroy", fillcolor="rgba(30,58,95,0.07)",
        hovertemplate="<b>%{x}</b><br>Thực tế: %{y:,.1f} Tỷ<extra></extra>",
    ))
    if any(v != 0 for v in y_cp_kh):
        fig_cp.add_trace(go.Scatter(
            x=x_labels, y=[v / 1e9 for v in y_cp_kh], name="Kế hoạch",
            mode="lines+markers",
            line=dict(color=COLOR_PLAN, width=1.8, dash="dot",
                      shape="spline", smoothing=1.2),
            marker=dict(size=5),
            hovertemplate="<b>%{x}</b><br>Kế hoạch: %{y:,.1f} Tỷ<extra></extra>",
        ))
    fig_cp.update_layout(
        **CHART_LAYOUT, height=300,
        title=dict(text="Chi phí QLDN theo thời gian (STT 82 + 151)", font=dict(size=13)),
        yaxis_title="Tỷ đồng",
        xaxis=dict(range=[-0.3, n - 0.7]),
        hovermode="x unified",
    )
    apply_chart_style(fig_cp)
    fix_chart_yrange_and_labels(
        fig_cp, x_labels,
        actual_vals=[v / 1e9 for v in y_cp_tt],
        plan_vals=[v / 1e9 for v in y_cp_kh],
        value_fmt="ty",
    )
    st.plotly_chart(fig_cp, use_container_width=True, config=MODEBAR_CONFIG)

    # ── SECTION C: % CPQL / DT ───────────────────────────────
    pct_cp_tt = [cp / dt * 100 if dt else 0 for cp, dt in zip(y_cp_tt, y_dt_tt)]
    pct_cp_kh = [ck / dk * 100 if dk else 0 for ck, dk in zip(y_cp_kh, y_dt_kh)]

    fig_pct = go.Figure()
    fig_pct.add_trace(go.Scatter(
        x=x_labels, y=pct_cp_tt, name="% CPQLDN/DT TT",
        mode="lines+markers+text",
        line=dict(color=COLOR_ACTUAL, width=2.5, shape="spline", smoothing=1.2),
        marker=dict(size=7),
        text=[f"{v:.1f}%" if v else "" for v in pct_cp_tt],
        textposition=smart_textpos(n),
        textfont=dict(size=10, color=COLOR_ACTUAL),
        fill="tozeroy", fillcolor="rgba(30,58,95,0.07)",
        hovertemplate="<b>%{x}</b><br>Thực tế: %{y:.1f}%<extra></extra>",
    ))
    if any(v != 0 for v in pct_cp_kh):
        fig_pct.add_trace(go.Scatter(
            x=x_labels, y=pct_cp_kh, name="% CPQLDN/DT KH",
            mode="lines+markers",
            line=dict(color=COLOR_PLAN, width=1.8, dash="dot",
                      shape="spline", smoothing=1.2),
            marker=dict(size=5),
            hovertemplate="<b>%{x}</b><br>Kế hoạch: %{y:.1f}%<extra></extra>",
        ))
    fig_pct.update_layout(
        **CHART_LAYOUT, height=280,
        title=dict(text="% Chi phí QLDN / Doanh thu", font=dict(size=13)),
        yaxis_title="%",
        xaxis=dict(range=[-0.3, n - 0.7]),
        hovermode="x unified",
    )
    apply_chart_style(fig_pct)
    fix_chart_yrange_and_labels(
        fig_pct, x_labels,
        actual_vals=pct_cp_tt,
        plan_vals=pct_cp_kh,
        value_fmt="pct",
    )
    st.plotly_chart(fig_pct, use_container_width=True, config=MODEBAR_CONFIG)

    st.divider()

    # ── SECTION D: Chi phí gián tiếp theo phòng ban ──────────
    st.markdown("#### Chi phí bộ phận gián tiếp")

    dept_tt: dict = {}
    dept_kh: dict = {}
    for stt in range(int(STT_CPGT_FROM), int(STT_CPGT_TO) + 1):
        rows = df[df[FG_STT] == float(stt)]
        if rows.empty:
            continue
        name_vals = rows[FG_NOI_DUNG].dropna()
        if name_vals.empty:
            continue
        name = name_vals.iloc[0]
        tt_total = sum(get_metric(df,      stt, sel_months, sel_buses).values())
        kh_total = sum(get_metric_plan(df, stt, sel_months, sel_buses).values())
        if tt_total != 0 or kh_total != 0:
            dept_tt[name] = tt_total
            dept_kh[name] = kh_total

    if dept_tt:
        sorted_depts = sorted(dept_tt, key=dept_tt.get, reverse=True)
        has_kh_dept  = any(dept_kh.get(d, 0) != 0 for d in sorted_depts)

        fig_gt = go.Figure()
        fig_gt.add_trace(go.Bar(
            y=sorted_depts,
            x=[dept_tt[d] / 1e9 for d in sorted_depts],
            name="Thực tế", orientation="h",
            marker_color=COLOR_ACTUAL,
            text=[f"{dept_tt[d]/1e9:.2f} Tỷ" for d in sorted_depts],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Thực tế: %{x:,.2f} Tỷ<extra></extra>",
        ))
        if has_kh_dept:
            fig_gt.add_trace(go.Bar(
                y=sorted_depts,
                x=[dept_kh.get(d, 0) / 1e9 for d in sorted_depts],
                name="Kế hoạch", orientation="h",
                marker_color=COLOR_PLAN,
                text=[f"{dept_kh.get(d,0)/1e9:.2f} Tỷ" for d in sorted_depts],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Kế hoạch: %{x:,.2f} Tỷ<extra></extra>",
            ))
        all_dept_x = [dept_tt[d] / 1e9 for d in sorted_depts]
        if has_kh_dept:
            all_dept_x += [dept_kh.get(d, 0) / 1e9 for d in sorted_depts]
        x_max_dept = max((v for v in all_dept_x if v > 0), default=1)

        fig_gt.update_layout(
            **CHART_LAYOUT, barmode="group",
            title=dict(text="Chi phí bộ phận gián tiếp TT vs KH", font=dict(size=13)),
            xaxis_title="Tỷ đồng",
            yaxis=dict(autorange="reversed"),
            height=max(300, len(sorted_depts) * 55 + 100),
            hovermode="y unified",
        )
        fig_gt.update_xaxes(range=[0, x_max_dept * 1.18])
        apply_chart_style(fig_gt, horizontal=True)
        st.plotly_chart(fig_gt, use_container_width=True, config=MODEBAR_CONFIG)

    # ── SECTION E: % CP gián tiếp / DT theo tháng ───────────
    cpgt_d   = get_metric_stt_range(df, STT_CPGT_FROM, STT_CPGT_TO, sel_months, sel_buses)
    pct_cpgt = [
        cpgt_d.get(m, 0) / dt_d.get(m, 0) * 100
        if dt_d.get(m, 0) > 0 else 0
        for m in months_sorted
    ]

    # Tính % KH: dùng CPQL KH / DT KH làm proxy
    pct_cpgt_kh = []
    for m in months_sorted:
        cp_kh_m = sum(
            get_metric_plan(df, stt, [m], sel_buses).get(m, 0)
            for stt in STT_CPQL_LIST
        )
        dt_kh_m = get_metric_plan(df, STT_DT_KH, [m], sel_buses).get(m, 0)
        pct_cpgt_kh.append(cp_kh_m / dt_kh_m * 100 if dt_kh_m > 0 else 0)

    fig_pgt = go.Figure()
    fig_pgt.add_trace(go.Scatter(
        x=x_labels, y=pct_cpgt, name="% CP gián tiếp/DT TT",
        mode="lines+markers+text",
        line=dict(color=COLOR_ACTUAL, width=2.5, shape="spline", smoothing=1.2),
        marker=dict(size=7),
        text=[f"{v:.1f}%" if v else "" for v in pct_cpgt],
        textposition=smart_textpos(n),
        textfont=dict(size=10, color=COLOR_ACTUAL),
        fill="tozeroy", fillcolor="rgba(30,58,95,0.07)",
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
    ))
    if any(v != 0 for v in pct_cpgt_kh):
        fig_pgt.add_trace(go.Scatter(
            x=x_labels, y=pct_cpgt_kh, name="Kế hoạch",
            mode="lines",
            line=dict(color=COLOR_PLAN, width=1.8, dash="dot",
                      shape="spline", smoothing=1.2),
            hovertemplate="<b>%{x}</b><br>KH: %{y:.1f}%<extra></extra>",
        ))
    fig_pgt.update_layout(
        **CHART_LAYOUT, height=280,
        title=dict(text="% Chi phí bộ phận gián tiếp / Doanh thu", font=dict(size=13)),
        yaxis_title="%",
        xaxis=dict(range=[-0.3, n - 0.7]),
        hovermode="x unified",
    )
    apply_chart_style(fig_pgt)
    fix_chart_yrange_and_labels(
        fig_pgt, x_labels,
        actual_vals=pct_cpgt,
        plan_vals=pct_cpgt_kh,
        value_fmt="pct",
    )
    st.plotly_chart(fig_pgt, use_container_width=True, config=MODEBAR_CONFIG)
