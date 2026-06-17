# =============================================================
# utils.py — Hàm tiện ích dùng chung toàn app
# =============================================================

import pandas as pd
import plotly.graph_objects as go
from config import COLOR_ACTUAL, COLOR_PLAN, COLOR_DANGER, COLOR_WARNING, COLOR_OK


# ─── MONTH LABELS ───────────────────────────────────────────

def month_display_label(dt_str: str) -> str:
    """'2026-01-01' → 'thg 1'"""
    try:
        return f"thg {int(dt_str[5:7])}"
    except Exception:
        return dt_str


def month_sort_key(label: str) -> int:
    """'thg 1' → 1"""
    try:
        return int(label.replace("thg", "").strip())
    except Exception:
        return 99


# ─── FORMAT SỐ ──────────────────────────────────────────────

def fmt_ty(value: float, decimals: int = 1) -> str:
    """Format số thành 'X.X Tỷ'."""
    if pd.isna(value):
        return "—"
    return f"{value / 1e9:,.{decimals}f} Tỷ"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format số thành 'X.X%'."""
    if pd.isna(value):
        return "—"
    return f"{value:.{decimals}f}%"


def fmt_delta(actual: float, plan: float) -> str:
    """Format chênh lệch thực tế so kế hoạch."""
    if pd.isna(actual) or pd.isna(plan) or plan == 0:
        return "—"
    delta = (actual - plan) / abs(plan) * 100
    sign  = "▲" if delta >= 0 else "▼"
    return f"{sign} {abs(delta):.1f}% vs KH"


def completion_color(pct: float) -> str:
    """Màu theo % hoàn thành."""
    from config import COMPLETION_THRESHOLDS
    if pd.isna(pct):
        return ""
    if pct < COMPLETION_THRESHOLDS["danger"]:
        return COLOR_DANGER
    if pct < COMPLETION_THRESHOLDS["warning"]:
        return COLOR_WARNING
    return COLOR_OK


# ─── PLOTLY LAYOUT ──────────────────────────────────────────

CHART_LAYOUT = dict(
    plot_bgcolor  = "white",
    paper_bgcolor = "white",
    font          = dict(family="Inter, sans-serif", size=11, color="#374151"),
    margin        = dict(l=65, r=85, t=45, b=20),
    legend        = dict(orientation="h", y=1.05, x=0),
    autosize      = True,
    dragmode      = False,
    uniformtext   = dict(minsize=8, mode='hide'),
    xaxis         = dict(
        showline=True, linecolor='#94a3b8', linewidth=1,
        showgrid=False, zeroline=False, mirror=False,
        automargin=True,
    ),
    yaxis         = dict(
        showline=True, linecolor='#94a3b8', linewidth=1,
        showgrid=False, zeroline=False, mirror=False,
        automargin=True,
    ),
)

# Dùng khi cần truyền margin riêng để tránh duplicate keyword
CHART_LAYOUT_NO_MARGIN = {k: v for k, v in CHART_LAYOUT.items() if k != "margin"}

MODEBAR_CONFIG = {
    'modeBarButtonsToRemove': [
        'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d',
        'autoScale2d', 'resetScale2d', 'resetViews',
        'select2d', 'lasso2d', 'toggleSpikelines',
        'hoverClosestCartesian', 'hoverCompareCartesian',
    ],
    'displaylogo': False,
    'scrollZoom': False,
    'doubleClick': False,
}


def smart_textpos(n: int) -> list:
    """Trả về list textposition tránh bị cắt ở 2 đầu trục."""
    if n <= 1:
        return ["top center"]
    return ["top right"] + ["top center"] * max(0, n - 2) + ["top left"]


def apply_chart_style(fig: go.Figure, tickangle: int = -30,
                      horizontal: bool = False) -> go.Figure:
    """Xóa lưới, tick font đậm, cliponaxis=False cho mọi chart."""
    angle = 0 if horizontal else tickangle
    fig.update_xaxes(
        showgrid=False, zeroline=False, ticklabelstandoff=6, tickangle=angle,
        tickfont=dict(size=11, color="#1e293b"),
        title_font=dict(size=12, color="#1e293b"),
    )
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        tickfont=dict(size=11, color="#1e293b"),
        title_font=dict(size=12, color="#1e293b"),
    )
    fig.update_traces(cliponaxis=False)
    return fig


def apply_responsive(fig):
    """Áp dụng sau mỗi fig để đảm bảo
    label/axis không bị mất khi xoay màn hình."""
    fig.update_traces(
        cliponaxis=False,
        selector=dict(type='bar')
    )
    fig.update_traces(
        cliponaxis=False,
        selector=dict(type='scatter')
    )
    fig.update_traces(
        constraintext='none',
        textfont=dict(size=10),
        selector=dict(type='bar')
    )
    fig.update_layout(
        xaxis=dict(automargin=True, fixedrange=True),
        yaxis=dict(automargin=True, fixedrange=True),
    )
    return fig


# ─── CHART HELPERS ──────────────────────────────────────────

def line_chart_actual_vs_plan(
    x_vals, actual_vals, plan_vals,
    actual_name="Thực tế", plan_name="Kế hoạch",
    title="", yaxis_title="Tỷ đồng", height=320,
    value_fmt="ty",
) -> go.Figure:
    import math

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_vals, y=plan_vals, name=plan_name,
        mode="lines",
        line=dict(color="#4caf50", width=1.8,
                  dash="dot", shape="spline", smoothing=1.2),
        hovertemplate=(
            "<b>%{x}</b><br>" + plan_name +
            ": %{y:,.1f}<extra></extra>"
        ),
    ))

    fig.add_trace(go.Scatter(
        x=x_vals, y=actual_vals, name=actual_name,
        mode="lines+markers",
        line=dict(color=COLOR_ACTUAL, width=2.5,
                  shape="spline", smoothing=1.2),
        marker=dict(size=7, color=COLOR_ACTUAL),
        hovertemplate=(
            "<b>%{x}</b><br>" + actual_name +
            ": %{y:,.1f}<extra></extra>"
        ),
    ))

    def _safe(v):
        try:
            return v is not None and not math.isnan(float(v)) and v != 0
        except Exception:
            return False

    all_v = [v for v in list(actual_vals) + list(plan_vals) if _safe(v)]
    if all_v:
        lo    = min(all_v)
        hi    = max(all_v)
        span  = (hi - lo) if hi != lo else hi * 0.3
        y_lo  = lo - span * 0.10
        y_hi  = hi + span * 0.45
        y_off = span * 0.14
    else:
        y_lo, y_hi, y_off = 0, 1, 0.05

    n = len(actual_vals)
    for i, (xv, yv) in enumerate(zip(x_vals, actual_vals)):
        if not _safe(yv):
            continue
        fmt = (f"{yv:.1f}" if value_fmt == "ty"
               else f"{yv:.1f}%")
        xanc = "left" if i == 0 else (
               "right" if i == n - 1 else "center")
        fig.add_annotation(
            x=xv, y=yv + y_off,
            text=f"<b>{fmt}</b>",
            showarrow=False,
            xanchor=xanc,
            yanchor="bottom",
            font=dict(size=10, color="#1e293b"),
            bgcolor="rgba(255,255,255,0.88)",
            borderpad=2,
        )

    base = {k: v for k, v in CHART_LAYOUT.items()
            if k not in ("hovermode", "xaxis", "yaxis")}
    fig.update_layout(
        **base,
        title=dict(text=title, font=dict(size=13)),
        yaxis_title=yaxis_title,
        height=height,
        hovermode="x unified",
    )
    fig.update_xaxes(showline=True, linecolor='#94a3b8', linewidth=1,
                      showgrid=False, zeroline=False, mirror=False,
                      ticklabelstandoff=6,
                      tickfont=dict(size=11, color="#1e293b"))
    fig.update_yaxes(showline=True, linecolor='#94a3b8', linewidth=1,
                      range=[y_lo, y_hi], autorange=False,
                      showgrid=False, zeroline=False, mirror=False,
                      tickfont=dict(size=11, color="#1e293b"))
    return fig


def bar_chart_actual_vs_plan(
    x_vals, actual_vals, plan_vals,
    actual_name="Thực tế", plan_name="Kế hoạch",
    title="", yaxis_title="Tỷ đồng", height=320,
) -> go.Figure:
    """Tạo grouped bar chart TT vs KH chuẩn."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_vals, y=actual_vals, name=actual_name,
        marker_color=COLOR_ACTUAL,
        text=[f"{v/1e9:.1f}" if not pd.isna(v) and v != 0 else "" for v in actual_vals],
        textposition="outside", textfont=dict(size=10),
    ))
    fig.add_trace(go.Bar(
        x=x_vals, y=plan_vals, name=plan_name,
        marker_color=COLOR_PLAN,
        text=[f"{v/1e9:.1f}" if not pd.isna(v) and v != 0 else "" for v in plan_vals],
        textposition="outside", textfont=dict(size=10),
    ))
    fig.update_layout(**CHART_LAYOUT, barmode="group",
                      title=dict(text=title, font=dict(size=13)),
                      yaxis_title=yaxis_title, height=height)
    apply_chart_style(fig)
    return fig


def hbar_chart(
    labels, values, colors=None,
    title="", height=None, text_fmt="ty",
) -> go.Figure:
    """Horizontal bar chart cho top N bộ phận."""
    fmt = (lambda v: f"{v/1e9:.1f} Tỷ") if text_fmt == "ty" else (lambda v: f"{v:.1f}%")
    if colors is None:
        colors = [COLOR_ACTUAL] * len(values)
    if height is None:
        height = max(250, len(labels) * 40 + 80)

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors,
        text=[fmt(v) for v in values],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(**CHART_LAYOUT, title=dict(text=title, font=dict(size=13)),
                      height=height)
    fig.update_yaxes(autorange="reversed")
    apply_chart_style(fig, horizontal=True)
    return fig


# ─── PANDAS STYLER ──────────────────────────────────────────

def style_heat_red(df: pd.DataFrame, col: str) -> pd.DataFrame.style:
    """Tô màu đỏ heat-map cho cột giá trị công nợ."""
    max_val = df[col].max() if df[col].max() > 0 else 1

    def _color(val):
        if pd.isna(val) or val == 0:
            return ""
        intensity = min(val / max_val, 1.0)
        r = int(239 + (255 - 239) * (1 - intensity))
        g = int(68  + (255 - 68)  * (1 - intensity))
        b = int(68  + (255 - 68)  * (1 - intensity))
        return f"background-color: rgba({r},{g},{b},0.6); color: #7f1d1d"

    return df.style.map(_color, subset=[col])


def style_completion(df: pd.DataFrame, col: str) -> pd.DataFrame.style:
    """Tô màu xanh/vàng/đỏ theo % hoàn thành."""
    from config import COMPLETION_THRESHOLDS

    def _color(val):
        if pd.isna(val):
            return ""
        if val < COMPLETION_THRESHOLDS["danger"]:
            return "background-color: #fef2f2; color: #991b1b"
        if val < COMPLETION_THRESHOLDS["warning"]:
            return "background-color: #fffbeb; color: #92400e"
        return "background-color: #f0fdf4; color: #166534"

    return df.style.map(_color, subset=[col])


def fix_chart_yrange_and_labels(
    fig: go.Figure,
    x_vals: list,
    actual_vals: list,
    plan_vals: list = None,
    value_fmt: str = "ty",
) -> go.Figure:
    """
    Áp dụng cho bất kỳ go.Figure() nào:
    1. Xóa text labels khỏi traces (giữ nguyên fill/fillcolor)
    2. Set Y-range phù hợp với data
    3. Thêm annotations cho actual_vals
    """
    import math

    def _safe(v):
        try:
            return (v is not None
                    and not math.isnan(float(v))
                    and float(v) != 0)
        except Exception:
            return False

    # 1. Xóa text-mode trong tất cả trace
    for trace in fig.data:
        mode = getattr(trace, "mode", None)
        if mode and "text" in str(mode):
            new_mode = (str(mode)
                        .replace("+text", "")
                        .replace("text+", "")
                        .replace("text", "lines"))
            trace.update(mode=new_mode, text=None, textposition=None)

    # 2. Tính Y range
    check = [v for v in list(actual_vals) +
             list(plan_vals or []) if _safe(v)]
    if check:
        lo   = min(check)
        hi   = max(check)
        span = (hi - lo) if hi != lo else hi * 0.3
        y_lo = lo - span * 0.10
        y_hi = hi + span * 0.45
        yoff = span * 0.14
    else:
        y_lo, y_hi, yoff = 0, 1, 0.05

    fig.update_yaxes(
        range=[y_lo, y_hi],
        autorange=False,
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=11, color="#1e293b"),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        ticklabelstandoff=6,
        tickfont=dict(size=11, color="#1e293b"),
    )

    # 3. Thêm annotations cho actual_vals
    n = len(actual_vals)
    for i, (xv, yv) in enumerate(zip(x_vals, actual_vals)):
        if not _safe(yv):
            continue
        fmt = (f"{float(yv):.1f}"
               if value_fmt == "ty"
               else f"{float(yv):.1f}%")
        xanc = ("left"  if i == 0 else
                "right" if i == n - 1 else "center")
        fig.add_annotation(
            x=xv, y=float(yv) + yoff,
            text=f"<b>{fmt}</b>",
            showarrow=False,
            xanchor=xanc,
            yanchor="bottom",
            font=dict(size=10, color="#1e293b"),
            bgcolor="rgba(255,255,255,0.88)",
            borderpad=2,
        )

    return fig
