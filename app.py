import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Μελέτη Προϊόντος",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: #F8F4F0;
    border-right: 1px solid #E8DDD5;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
    color: #3D2B1F !important;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.stApp { background: #FAFAF8; }

[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #EDE8E3;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 1.6rem !important;
    color: #1A1A1A !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #8B7355 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8B7355;
    border-bottom: 1px solid #EDE8E3;
    padding-bottom: 6px;
    margin: 24px 0 16px 0;
}

.page-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1A1A1A;
    letter-spacing: -0.02em;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #8B7355;
    font-weight: 400;
    margin-bottom: 24px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F0EBE5;
    padding: 4px;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: #8B7355;
    padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #1A1A1A !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

hr { border-color: #EDE8E3; }

.js-plotly-plot {
    border-radius: 12px;
    border: 1px solid #EDE8E3;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Colour palette ─────────────────────────────────────────────────────────────
C = {
    "brand":  "#C75B7A",
    "accent": "#D4845A",
    "green":  "#3D9B8A",
    "red":    "#C0392B",
    "warm":   "#8B7355",
    "grey":   "#B0A090",
    "bg":     "#FFFFFF",
    "card":   "#FAFAF8",
    "grid":   "#EDE8E3",
    "text":   "#1A1A1A",
    "text2":  "#8B7355",
    "y24":    "#A67C30",
    "y25":    "#C75B7A",
    "y26":    "#3D9B8A",
}

YEAR_COLORS = {2024: C["y24"], 2025: C["y25"], 2026: C["y26"]}
YEAR_DASHES = {2024: "dot",    2025: "dash",   2026: "solid"}

MONTH_ORDER = {
    "Ιανουάριος": 1, "Φεβρουάριος": 2, "Μάρτιος": 3,   "Απρίλιος": 4,
    "Μάιος": 5,      "Ιούνιος": 6,     "Ιούλιος": 7,    "Αύγουστος": 8,
    "Σεπτέμβριος": 9,"Οκτώβριος": 10,  "Νοέμβριος": 11, "Δεκέμβριος": 12,
}
MONTH_ABBR = {
    "Ιανουάριος": "ΙΑΝ", "Φεβρουάριος": "ΦΕΒ", "Μάρτιος": "ΜΑΡ",
    "Απρίλιος": "ΑΠΡ",   "Μάιος": "ΜΑΪ",        "Ιούνιος": "ΙΟΥΝ",
    "Ιούλιος": "ΙΟΥΛ",   "Αύγουστος": "ΑΥΓ",    "Σεπτέμβριος": "ΣΕΠ",
    "Οκτώβριος": "ΟΚΤ",  "Νοέμβριος": "ΝΟΕ",    "Δεκέμβριος": "ΔΕΚ",
}
MONTH_NUM_TO_NAME = {v: k for k, v in MONTH_ORDER.items()}

AX = dict(
    gridcolor=C["grid"], gridwidth=0.8,
    zerolinecolor=C["grid"],
    tickfont=dict(color=C["text2"], size=10),
    showline=True, linecolor=C["grid"],
)

# ── Chart layout helper ────────────────────────────────────────────────────────
def apply_layout(fig, title="", height=420, legend_bottom=False):
    fig.update_xaxes(**AX)
    fig.update_yaxes(**AX)
    leg = dict(
        font=dict(size=11, color=C["text2"]),
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
    )
    if legend_bottom:
        leg.update(x=0.5, y=-0.25, xanchor="center")
    else:
        leg.update(x=0, y=1.12)
    fig.update_layout(
        title={"text": title,
               "font": {"size": 13, "color": C["text"], "family": "DM Sans"},
               "x": 0.01, "pad": {"b": 10}} if title else {},
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["card"],
        font={"family": "DM Sans", "color": C["text"]},
        height=height,
        margin={"l": 10, "r": 20, "t": 44 if title else 20, "b": 10},
        legend=leg,
        hoverlabel={"bgcolor": "#fff", "bordercolor": C["grid"],
                    "font_size": 12, "font_family": "DM Sans"},
    )
    return fig

# ── Data parser ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Φόρτωση δεδομένων…")
def parse_excel(file_bytes: bytes) -> pd.DataFrame:
    raw = pd.read_excel(io.BytesIO(file_bytes), header=None, engine="openpyxl")

    row_store = raw.iloc[9].values
    row_month = raw.iloc[10].values
    row_year  = raw.iloc[11].values
    row_type  = raw.iloc[13].values

    col_map = {}
    cur_store = cur_month = cur_year = None
    for i in range(len(row_store)):
        if pd.notna(row_store[i]):  cur_store = str(row_store[i])
        if pd.notna(row_month[i]):  cur_month = str(row_month[i])
        if pd.notna(row_year[i]):   cur_year  = int(row_year[i])
        col_type = str(row_type[i]) if pd.notna(row_type[i]) else None
        if col_type in ["Ποσότητα", "Τζίρος"]:
            if cur_store and "Σύνολο" not in cur_store:
                if cur_month and "Σύνολο" not in cur_month and cur_year:
                    col_map[i] = {
                        "store": cur_store, "month": cur_month,
                        "year": cur_year,   "type": col_type,
                    }

    product_rows = []
    last_family = None
    for row_idx in range(14, len(raw)):
        r0 = raw.iloc[row_idx, 0]
        r1 = raw.iloc[row_idx, 1]
        r3 = raw.iloc[row_idx, 3]
        if pd.notna(r0) and "Σύνολο" not in str(r0) and "FRANCHISE" not in str(r0):
            last_family = str(r0)
        if pd.notna(r1):
            product_rows.append({
                "row_idx": row_idx,
                "family":  last_family,
                "code":    str(r1),
                "desc":    str(r3) if pd.notna(r3) else str(r1),
            })

    records = []
    for prod in product_rows:
        for col_idx, meta in col_map.items():
            val = raw.iloc[prod["row_idx"], col_idx]
            if pd.notna(val) and float(val) != 0:
                records.append({
                    "store":  meta["store"],
                    "month":  meta["month"],
                    "year":   meta["year"],
                    "type":   meta["type"],
                    "family": prod["family"],
                    "code":   prod["code"],
                    "desc":   prod["desc"],
                    "value":  float(val),
                })

    df = pd.DataFrame(records)
    df["month_num"]  = df["month"].map(MONTH_ORDER)
    df["month_abbr"] = df["month"].map(MONTH_ABBR)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🧴 Μελέτη Προϊόντος")
    st.markdown("---")
    uploaded = st.file_uploader(
        "ΑΝΕΒΑΣΕ ΤΟ ΑΡΧΕΙΟ .XLSX",
        type=["xlsx"],
        help="SalesSummaryFranchise_all_companies_…xlsx",
    )

if not uploaded:
    st.markdown('<div class="page-title">🧴 Μελέτη Προϊόντος</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Franchise Sales Analysis Dashboard</div>', unsafe_allow_html=True)
    st.info("👈 Ανέβασε το αρχείο Excel από το **sidebar** για να ξεκινήσεις.")
    st.stop()

# ── Load & filter ──────────────────────────────────────────────────────────────
df_full = parse_excel(uploaded.getvalue())

all_stores   = sorted(df_full["store"].unique())
all_families = sorted(df_full["family"].dropna().unique())
all_products = df_full[["code", "desc"]].drop_duplicates().sort_values("code")
all_years    = sorted(df_full["year"].unique())

with st.sidebar:
    st.success(f"✅ {len(df_full):,} εγγραφές φορτώθηκαν")
    st.markdown("---")
    st.markdown("**ΦΙΛΤΡΑ**")
    sel_families = st.multiselect("ΟΙΚΟΓΕΝΕΙΕΣ", all_families, default=all_families)
    sel_years    = st.multiselect("ΕΤΗ", all_years, default=all_years)
    st.markdown("---")
    st.caption(f"Καταστήματα: **{df_full['store'].nunique()}**")
    st.caption(f"Προϊόντα: **{df_full['code'].nunique()}**")
    st.caption(f"Έτη: **{', '.join(map(str, all_years))}**")

df = df_full.copy()
if sel_families:
    df = df[df["family"].isin(sel_families)]
if sel_years:
    df = df[df["year"].isin(sel_years)]

qty = df[df["type"] == "Ποσότητα"]
rev = df[df["type"] == "Τζίρος"]

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">🧴 Μελέτη Προϊόντος</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Franchise Sales Analysis Dashboard — Ανάλυση Τεμαχίων & Τζίρου ανά Κατάστημα</div>', unsafe_allow_html=True)

# ── Top KPI bar ────────────────────────────────────────────────────────────────
total_qty = qty["value"].sum()
total_rev = rev["value"].sum()
n_stores  = df["store"].nunique()
n_months  = df[["year", "month"]].drop_duplicates().shape[0]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Συνολικά Τεμάχια", f"{int(total_qty):,}")
k2.metric("Συνολικός Τζίρος", f"€{total_rev:,.2f}")
k3.metric("Ενεργά Καταστήματα", n_stores)
k4.metric("Περίοδοι (μήνες)", n_months)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🌐 Σύνολο Δικτύου", "🏪 Ανά Κατάστημα"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ΣΥΝΟΛΟ ΔΙΚΤΥΟΥ
# ─────────────────────────────────────────────────────────────────────────────
with tab1:

    # ── 1A: Κύκλος Ζωής — ετήσια τεμάχια ανά προϊόν ─────────────────────────
    st.markdown('<div class="section-header">📦 Κύκλος Ζωής Προϊόντος</div>', unsafe_allow_html=True)

    lifecycle = qty.groupby(["code", "desc", "year"])["value"].sum().reset_index()

    product_colors = [C["brand"], C["accent"], C["green"], C["y24"], C["warm"]]

    fig_lc = go.Figure()
    for idx, (code, grp) in enumerate(lifecycle.groupby("code")):
        label = grp["desc"].iloc[0]
        label = label[:45] + "…" if len(label) > 45 else label
        fig_lc.add_trace(go.Bar(
            name=f"{code}",
            x=grp["year"].astype(str),
            y=grp["value"],
            text=grp["value"].astype(int),
            textposition="outside",
            textfont=dict(size=11, color=C["text"]),
            marker_color=product_colors[idx % len(product_colors)],
            hovertemplate=f"<b>{label}</b><br>Έτος: %{{x}}<br>Τεμάχια: %{{y:,.0f}}<extra></extra>",
        ))
    apply_layout(fig_lc, height=420)
    fig_lc.update_layout(barmode="group")
    st.plotly_chart(fig_lc, use_container_width=True)

    # ── 1B: Μηνιαία trend τεμαχίων ───────────────────────────────────────────
    st.markdown('<div class="section-header">📈 Μηνιαία Πορεία Τεμαχίων</div>', unsafe_allow_html=True)

    qty_monthly = (qty.groupby(["month", "month_num", "year"])["value"]
                   .sum().reset_index().sort_values(["year", "month_num"]))

    fig_trend = go.Figure()
    for yr, grp in qty_monthly.groupby("year"):
        grp = grp.sort_values("month_num")
        fig_trend.add_trace(go.Scatter(
            x=grp["month_num"], y=grp["value"],
            mode="lines+markers",
            name=str(yr),
            line=dict(color=YEAR_COLORS.get(yr, C["grey"]),
                      dash=YEAR_DASHES.get(yr, "solid"), width=2.5),
            marker=dict(size=7, color=YEAR_COLORS.get(yr, C["grey"])),
            customdata=grp[["month"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>Τεμάχια: %{y:,.0f}<extra>%{fullData.name}</extra>",
        ))
    apply_layout(fig_trend, height=400)
    fig_trend.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=["ΙΑΝ","ΦΕΒ","ΜΑΡ","ΑΠΡ","ΜΑΪ","ΙΟΥΝ","ΙΟΥΛ","ΑΥΓ","ΣΕΠ","ΟΚΤ","ΝΟΕ","ΔΕΚ"],
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── 1C: Σύγκριση 2025 vs 2026 ────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Σύγκριση 2025 vs 2026</div>', unsafe_allow_html=True)

    years_available = sorted(df["year"].unique())
    if 2025 in years_available and 2026 in years_available:
        qty_net = qty.groupby(["month_num", "month_abbr", "year"])["value"].sum().reset_index()
        rev_net = rev.groupby(["month_num", "month_abbr", "year"])["value"].sum().reset_index()

        m25 = set(qty_net[qty_net["year"] == 2025]["month_num"])
        m26 = set(qty_net[qty_net["year"] == 2026]["month_num"])
        common_m = sorted(m25 & m26)
        x_labels = [MONTH_ABBR.get(MONTH_NUM_TO_NAME.get(m, ""), str(m)) for m in common_m]

        fig_cmp = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Τεμάχια: 2025 vs 2026", "Τζίρος (€): 2025 vs 2026"],
            horizontal_spacing=0.08,
        )
        for metric_data, col_idx in [(qty_net, 1), (rev_net, 2)]:
            d25 = metric_data[metric_data["year"] == 2025].set_index("month_num")["value"]
            d26 = metric_data[metric_data["year"] == 2026].set_index("month_num")["value"]
            y25 = [d25.get(m, 0) for m in common_m]
            y26 = [d26.get(m, 0) for m in common_m]
            fmt = ",.0f" if col_idx == 1 else ",.2f"
            prefix = "" if col_idx == 1 else "€"
            for yr, ydata, color in [(2025, y25, C["y25"]), (2026, y26, C["y26"])]:
                fig_cmp.add_trace(go.Bar(
                    name=str(yr), x=x_labels, y=ydata,
                    marker_color=color,
                    legendgroup=str(yr), showlegend=(col_idx == 1),
                    hovertemplate=f"{yr}<br>{prefix}%{{y:{fmt}}}<extra></extra>",
                ), row=1, col=col_idx)

        apply_layout(fig_cmp, height=420)
        fig_cmp.update_layout(barmode="group")
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Delta summary
        total_q25 = sum(qty_net[qty_net["year"] == 2025]["value"])
        total_q26 = sum(qty_net[qty_net["year"] == 2026]["value"])
        total_r25 = sum(rev_net[rev_net["year"] == 2025]["value"])
        total_r26 = sum(rev_net[rev_net["year"] == 2026]["value"])
        dq = (total_q26 - total_q25) / total_q25 * 100 if total_q25 else 0
        dr = (total_r26 - total_r25) / total_r25 * 100 if total_r25 else 0

        c1, c2 = st.columns(2)
        c1.metric("Τεμάχια 2025 → 2026", f"{int(total_q26):,}", f"{dq:+.1f}%")
        c2.metric("Τζίρος 2025 → 2026", f"€{total_r26:,.2f}", f"{dr:+.1f}%")
    else:
        st.info("Χρειάζονται δεδομένα και για τα δύο έτη (2025 & 2026) για τη σύγκριση.")

    # ── 1D: TOP 10 / LOW 10 Καταστήματα ──────────────────────────────────────
    st.markdown('<div class="section-header">🏆 Κατάταξη Καταστημάτων</div>', unsafe_allow_html=True)

    store_qty = qty.groupby("store")["value"].sum().reset_index(name="qty")
    store_rev = rev.groupby("store")["value"].sum().reset_index(name="rev")
    store_total = store_qty.merge(store_rev, on="store", how="outer").fillna(0)
    store_total["rank_qty"] = store_total["qty"].rank(ascending=False).astype(int)
    store_total["rank_rev"] = store_total["rev"].rank(ascending=False).astype(int)

    top10q = store_total.nlargest(10, "qty").sort_values("qty")
    bot10q = store_total.nsmallest(10, "qty").sort_values("qty", ascending=False)

    fig_rank = make_subplots(
        rows=1, cols=2,
        subplot_titles=["🏆 TOP 10 — Τεμάχια", "⚠️ LOW 10 — Τεμάχια"],
        horizontal_spacing=0.12,
    )
    for data, col, color in [(top10q, 1, C["green"]), (bot10q, 2, C["red"])]:
        fig_rank.add_trace(go.Bar(
            y=data["store"], x=data["qty"],
            orientation="h",
            marker_color=color,
            text=data["qty"].astype(int).astype(str),
            textposition="auto",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Τεμάχια: %{x:,.0f}<extra></extra>",
            showlegend=False,
        ), row=1, col=col)
    apply_layout(fig_rank, height=440)
    st.plotly_chart(fig_rank, use_container_width=True)

    # TOP 10 / LOW 10 — Τζίρος
    top10r = store_total.nlargest(10, "rev").sort_values("rev")
    bot10r = store_total.nsmallest(10, "rev").sort_values("rev", ascending=False)

    fig_rev_rank = make_subplots(
        rows=1, cols=2,
        subplot_titles=["🏆 TOP 10 — Τζίρος (€)", "⚠️ LOW 10 — Τζίρος (€)"],
        horizontal_spacing=0.12,
    )
    for data, col, color in [(top10r, 1, C["brand"]), (bot10r, 2, C["accent"])]:
        fig_rev_rank.add_trace(go.Bar(
            y=data["store"], x=data["rev"],
            orientation="h",
            marker_color=color,
            text=["€" + f"{v:,.0f}" for v in data["rev"]],
            textposition="auto",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Τζίρος: €%{x:,.2f}<extra></extra>",
            showlegend=False,
        ), row=1, col=col)
    apply_layout(fig_rev_rank, height=440)
    st.plotly_chart(fig_rev_rank, use_container_width=True)

    # ── 1E: Heatmap ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🗺️ Heatmap — Τεμάχια ανά Κατάστημα & Μήνα</div>', unsafe_allow_html=True)

    hm = qty.groupby(["store", "month_num"])["value"].sum().unstack(fill_value=0)
    hm.columns = [MONTH_ABBR.get(MONTH_NUM_TO_NAME.get(c, ""), str(c)) for c in hm.columns]
    hm = hm.loc[hm.sum(axis=1).sort_values(ascending=False).index]

    fig_hm = go.Figure(go.Heatmap(
        z=hm.values,
        x=list(hm.columns),
        y=list(hm.index),
        colorscale=[[0, "#fff8e1"], [0.4, "#E8C547"], [0.7, C["brand"]], [1, "#4A1020"]],
        hovertemplate="<b>%{y}</b><br>Μήνας: %{x}<br>Τεμάχια: %{z:,.0f}<extra></extra>",
    ))
    fig_hm.update_layout(
        paper_bgcolor=C["bg"], plot_bgcolor=C["card"],
        font={"family": "DM Sans", "color": C["text"]},
        height=max(380, len(hm) * 20),
        margin={"l": 200, "r": 20, "t": 20, "b": 40},
        hoverlabel={"bgcolor": "#fff", "bordercolor": C["grid"],
                    "font_size": 12, "font_family": "DM Sans"},
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    # ── 1F: Full ranking table ────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Πλήρης Πίνακας Καταστημάτων</div>', unsafe_allow_html=True)

    tbl = store_total.sort_values("rank_qty")[["store", "qty", "rev", "rank_qty", "rank_rev"]].copy()
    tbl.columns = ["Κατάστημα", "Τεμάχια", "Τζίρος (€)", "Rank Τεμ.", "Rank Τζίρος"]
    tbl["Τεμάχια"]   = tbl["Τεμάχια"].astype(int)
    tbl["Τζίρος (€)"] = tbl["Τζίρος (€)"].round(2)
    tbl.index = tbl.pop("Rank Τεμ.")
    tbl.index.name = "#"
    st.dataframe(tbl, use_container_width=True, height=420)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ΑΝΑ ΚΑΤΑΣΤΗΜΑ
# ─────────────────────────────────────────────────────────────────────────────
with tab2:

    col_sel, col_rank = st.columns([3, 1])
    with col_sel:
        selected_store = st.selectbox(
            "ΕΠΙΛΟΓΗ ΚΑΤΑΣΤΗΜΑΤΟΣ",
            all_stores,
            format_func=lambda x: x,
        )
    with col_rank:
        s_rank_q = store_total[store_total["store"] == selected_store]["rank_qty"].values
        s_rank_r = store_total[store_total["store"] == selected_store]["rank_rev"].values
        if len(s_rank_q):
            st.metric("Rank Τεμαχίων", f"#{int(s_rank_q[0])}", f"από {len(store_total)} καταστήματα")
        if len(s_rank_r):
            st.metric("Rank Τζίρου", f"#{int(s_rank_r[0])}")

    st.markdown("---")

    s_qty = qty[qty["store"] == selected_store]
    s_rev = rev[rev["store"] == selected_store]

    # KPIs for this store
    s_total_q = s_qty["value"].sum()
    s_total_r = s_rev["value"].sum()
    s_years   = sorted(s_qty["year"].unique())

    sk1, sk2, sk3 = st.columns(3)
    sk1.metric("Τεμάχια (σύνολο)", f"{int(s_total_q):,}")
    sk2.metric("Τζίρος (σύνολο)", f"€{s_total_r:,.2f}")
    sk3.metric("Έτη με πωλήσεις", len(s_years))

    st.markdown('<div class="section-header">📦 Μηνιαία Τεμάχια ανά Έτος</div>', unsafe_allow_html=True)

    # Chart A — monthly qty
    s_qty_m = (s_qty.groupby(["month_num", "year"])["value"]
               .sum().reset_index().sort_values(["year", "month_num"]))

    fig_sq = go.Figure()
    for yr, grp in s_qty_m.groupby("year"):
        grp = grp.sort_values("month_num")
        fig_sq.add_trace(go.Scatter(
            x=grp["month_num"], y=grp["value"],
            mode="lines+markers", name=str(yr),
            line=dict(color=YEAR_COLORS.get(yr, C["grey"]),
                      dash=YEAR_DASHES.get(yr, "solid"), width=2.5),
            marker=dict(size=8, color=YEAR_COLORS.get(yr, C["grey"])),
            hovertemplate="<b>Μήνας %{x}</b><br>Τεμάχια: %{y:,.0f}<extra>%{fullData.name}</extra>",
        ))
    apply_layout(fig_sq, height=380)
    fig_sq.update_xaxes(
        tickmode="array", tickvals=list(range(1, 13)),
        ticktext=["ΙΑΝ","ΦΕΒ","ΜΑΡ","ΑΠΡ","ΜΑΪ","ΙΟΥΝ","ΙΟΥΛ","ΑΥΓ","ΣΕΠ","ΟΚΤ","ΝΟΕ","ΔΕΚ"],
    )
    st.plotly_chart(fig_sq, use_container_width=True)

    # Chart B — monthly revenue
    st.markdown('<div class="section-header">💰 Μηνιαίος Τζίρος ανά Έτος</div>', unsafe_allow_html=True)

    s_rev_m = (s_rev.groupby(["month_num", "month_abbr", "year"])["value"]
               .sum().reset_index().sort_values(["year", "month_num"]))

    fig_sr = go.Figure()
    for yr, grp in s_rev_m.groupby("year"):
        grp = grp.sort_values("month_num")
        fig_sr.add_trace(go.Bar(
            x=grp["month_abbr"], y=grp["value"],
            name=str(yr),
            marker_color=YEAR_COLORS.get(yr, C["grey"]),
            hovertemplate="<b>%{x}</b><br>Τζίρος: €%{y:,.2f}<extra>%{fullData.name}</extra>",
        ))
    apply_layout(fig_sr, height=380)
    fig_sr.update_layout(barmode="group")
    st.plotly_chart(fig_sr, use_container_width=True)

    # Chart C — 2025 vs 2026 for this store
    if 2025 in s_years and 2026 in s_years:
        st.markdown('<div class="section-header">📊 Σύγκριση 2025 vs 2026</div>', unsafe_allow_html=True)

        sm25q = s_qty_m[s_qty_m["year"] == 2025].set_index("month_num")["value"]
        sm26q = s_qty_m[s_qty_m["year"] == 2026].set_index("month_num")["value"]
        sm25r = s_rev_m[s_rev_m["year"] == 2025].set_index("month_num")["value"]
        sm26r = s_rev_m[s_rev_m["year"] == 2026].set_index("month_num")["value"]

        sc_months = sorted(set(sm25q.index) & set(sm26q.index))
        sc_labels = [MONTH_ABBR.get(MONTH_NUM_TO_NAME.get(m, ""), str(m)) for m in sc_months]

        fig_sc = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Τεμάχια: 2025 vs 2026", "Τζίρος (€): 2025 vs 2026"],
            horizontal_spacing=0.08,
        )
        for col_i, (d25, d26) in enumerate([(sm25q, sm26q), (sm25r, sm26r)], start=1):
            fmt = ",.0f" if col_i == 1 else ",.2f"
            for yr, ydata, color in [(2025, d25, C["y25"]), (2026, d26, C["y26"])]:
                fig_sc.add_trace(go.Bar(
                    name=str(yr), x=sc_labels,
                    y=[ydata.get(m, 0) for m in sc_months],
                    marker_color=color,
                    legendgroup=str(yr), showlegend=(col_i == 1),
                    hovertemplate=f"{yr}<br>%{{y:{fmt}}}<extra></extra>",
                ), row=1, col=col_i)
        apply_layout(fig_sc, height=400)
        fig_sc.update_layout(barmode="group")
        st.plotly_chart(fig_sc, use_container_width=True)

        # Delta
        dq_s = (sm26q.sum() - sm25q.sum()) / sm25q.sum() * 100 if sm25q.sum() else 0
        dr_s = (sm26r.sum() - sm25r.sum()) / sm25r.sum() * 100 if sm25r.sum() else 0
        sc1, sc2 = st.columns(2)
        sc1.metric("Τεμάχια 2025 → 2026", f"{int(sm26q.sum()):,}", f"{dq_s:+.1f}%")
        sc2.metric("Τζίρος 2025 → 2026", f"€{sm26r.sum():,.2f}", f"{dr_s:+.1f}%")

    # Chart D — per-product breakdown for this store
    st.markdown('<div class="section-header">🔬 Ανάλυση ανά Προϊόν</div>', unsafe_allow_html=True)

    prod_qty = (s_qty.groupby(["code", "desc", "year"])["value"]
                .sum().reset_index().sort_values(["code", "year"]))

    fig_prod = go.Figure()
    for idx, (code, grp) in enumerate(prod_qty.groupby("code")):
        label = grp["desc"].iloc[0]
        label = label[:40] + "…" if len(label) > 40 else label
        fig_prod.add_trace(go.Bar(
            name=f"{code}",
            x=grp["year"].astype(str), y=grp["value"],
            text=grp["value"].astype(int),
            textposition="outside",
            marker_color=product_colors[idx % len(product_colors)],
            hovertemplate=f"<b>{label}</b><br>Έτος: %{{x}}<br>Τεμάχια: %{{y:,.0f}}<extra></extra>",
        ))
    apply_layout(fig_prod, height=380, legend_bottom=True)
    fig_prod.update_layout(barmode="group")
    st.plotly_chart(fig_prod, use_container_width=True)

    # Store detail table
    st.markdown('<div class="section-header">📋 Αναλυτικός Πίνακας</div>', unsafe_allow_html=True)
    detail = (df[df["store"] == selected_store]
              .pivot_table(index=["code", "desc", "year", "month_abbr"],
                           columns="type", values="value", aggfunc="sum")
              .reset_index()
              .rename(columns={"Ποσότητα": "Τεμάχια", "Τζίρος": "Τζίρος (€)",
                                "code": "Κωδικός", "desc": "Περιγραφή",
                                "year": "Έτος", "month_abbr": "Μήνας"}))
    st.dataframe(detail, use_container_width=True, height=380)
