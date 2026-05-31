
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

try:
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# =============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =============================================================================

st.set_page_config(page_title="GEX Wheel Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  /* Importamos Inter (títulos) y Roboto Mono (datos/números) */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Roboto+Mono:wght@400;500;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Roboto Mono', monospace;
    background-color: #0a0d14;
    color: #e2e8f0;
  }
  .main { background-color: #0a0d14; }
  .block-container { padding-top: 1.5rem; padding-left: 2rem; padding-right: 2rem; }
  
  /* Títulos usando Inter */
  h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.02em; color: #f1f5f9; }

  /* Metric cards */
  .metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid #2d3f55;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
  }
  .metric-card .label {
    font-size: 0.70rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Inter', sans-serif;
  }
  .metric-card .value {
    font-size: 1.45rem;
    font-weight: 700;
    color: #f1f5f9;
    font-family: 'Inter', sans-serif;
    margin-top: 0.15rem;
  }
  .metric-card .delta { font-size: 0.78rem; margin-top: 0.15rem; }
  .pos { color: #4ade80; }
  .neg { color: #f87171; }

  /* Precio destacado */
  .price-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    border: 1px solid #3b82f6;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem;
  }
  .price-card .label { font-size: 0.70rem; color: #93c5fd; text-transform: uppercase; letter-spacing: 0.05em; font-family: 'Inter', sans-serif; }
  .price-card .value { font-size: 1.7rem; font-weight: 800; color: #e0f2fe; font-family: 'Inter', sans-serif; margin-top: 0.1rem; }
  .price-card .delta { font-size: 0.85rem; margin-top: 0.2rem; font-weight: 600; }

  /* Zero Gamma card */
  .flip-card {
    background: linear-gradient(135deg, #0f1f0f 0%, #1a2235 100%);
    border: 1px solid #166534;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
  }
  .flip-card .label { font-size: 0.70rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-family: 'Inter', sans-serif; }
  .flip-card .value { font-size: 1.45rem; font-weight: 700; color: #4ade80; font-family: 'Inter', sans-serif; margin-top: 0.15rem; }
  .flip-card .sub { font-size: 0.72rem; color: #94a3b8; margin-top: 0.2rem; font-family: 'Inter', sans-serif; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #2d3f55; padding-bottom: 2px; }
  .stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0; background: #111827; color: #94a3b8;
    border: 1px solid #2d3f55; font-family: 'Inter', sans-serif; font-size: 0.85rem; padding: 0.6rem 1.4rem;
  }
  .stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #93c5fd !important; border-bottom-color: #1e3a5f !important; font-weight: 600; }
  .stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0.5rem 1rem 0.5rem; }

  /* Sidebar */
  div[data-testid="stSidebar"] { background: #080b11; border-right: 1px solid #2d3f55; }
  .sidebar-header { font-family: 'Inter', sans-serif; font-size: 1rem; font-weight: 800; color: #93c5fd; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.75rem; }

  /* Dataframe */
  .dataframe thead th { background: #111827 !important; color: #93c5fd !important; font-size: 0.75rem; font-family: 'Inter', sans-serif; }
  .dataframe tbody td { color: #e2e8f0 !important; font-size: 0.80rem; }
  .dataframe tbody tr:nth-child(even) { background: #0d1117 !important; }
  .dataframe tbody tr:hover { background: #1e3a5f !important; }

  /* Botón */
  .stButton > button { background: linear-gradient(90deg, #1d4ed8, #3b82f6); color: #fff; border: none; border-radius: 6px; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.85rem; padding: 0.45rem 1rem; }
  .stButton > button:hover { opacity: 0.85; }

  /* Info / warn boxes */
  .info-box { background: #0c1a2e; border-left: 3px solid #3b82f6; border-radius: 4px; padding: 0.9rem 1rem; font-size: 0.85rem; color: #cbd5e1; margin: 0.5rem 0 1.2rem 0; line-height: 1.55; font-family: 'Inter', sans-serif; }
  .info-box strong { color: #93c5fd; }
  .warn-box { background: #1a1200; border-left: 3px solid #f59e0b; border-radius: 4px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #fcd34d; margin: 0.5rem 0; font-family: 'Inter', sans-serif; }
  .err-box { background: #1a0505; border-left: 3px solid #f87171; border-radius: 4px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #fca5a5; margin: 0.5rem 0; font-family: 'Inter', sans-serif; }

  /* Títulos de sección dentro de tabs */
  .section-title { font-family: 'Inter', sans-serif; font-size: 1.05rem; font-weight: 700; color: #e2e8f0; margin: 1rem 0 0.4rem 0; padding-bottom: 0.3rem; border-bottom: 1px solid #2d3f55; }

  /* Labels de selectbox/radio */
  label, .st-emotion-cache-1inwz65 { color: #cbd5e1 !important; font-size: 0.85rem !important; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# Escala adaptativa: formatea valores en la escala correcta
def _fmt(val, signed=False):
    if pd.isna(val) or val == 0: return ""
    sign = "+" if signed and val > 0 else ("-" if signed and val < 0 else "")
    v = abs(val)
    if v >= 1e9: return f"{sign}{v/1e9:.2f}B"
    if v >= 1e6: return f"{sign}{v/1e6:.2f}M"
    if v >= 1e3: return f"{sign}{v/1e3:.1f}K"
    return f"{sign}{v:.1f}"

def _auto_dtick(strikes):
    """Calcula el dtick óptimo del eje Y según la densidad de strikes."""
    if len(strikes) < 2: return 1
    spread = max(strikes) - min(strikes)
    # Queremos ~25 etiquetas visibles como máximo
    raw = spread / 25
    for step in [0.5, 1, 2, 2.5, 5, 10, 25, 50, 100]:
        if step >= raw: return step
    return round(raw, -1)

PLOTLY_TEMPLATE = dict(
    paper_bgcolor="#0a0d14", plot_bgcolor="#0d1117",
    font=dict(family="Roboto Mono, monospace", color="#e2e8f0", size=11),
    xaxis=dict(gridcolor="#1a2a3a", zerolinecolor="#2d3f55", linecolor="#2d3f55",
               tickfont=dict(color="#cbd5e1", size=11),
               title_font=dict(color="#94a3b8")),
    yaxis=dict(gridcolor="#1a2a3a", zerolinecolor="#2d3f55", linecolor="#2d3f55",
               tickfont=dict(color="#cbd5e1", size=11),
               title_font=dict(color="#94a3b8")),
    title_font=dict(color="#f1f5f9", size=14, family="Inter, sans-serif"),
    colorway=["#38bdf8", "#4ade80", "#f87171", "#fbbf24", "#a78bfa"],
    margin=dict(l=55, r=25, t=50, b=45),
    legend=dict(font=dict(color="#cbd5e1")),
)


# =============================================================================
# BLOQUE 1 – EXTRACCIÓN DE DATOS
# =============================================================================

@st.cache_data(ttl=900, show_spinner=False)
def fetch_spot_price(ticker):
    if not YF_AVAILABLE: return None
    try:
        tk = yf.Ticker(ticker)
        try:
            p = tk.fast_info.last_price
            if p and p > 0: return round(float(p), 4)
        except Exception: pass
        h = tk.history(period="5d", auto_adjust=True)
        if not h.empty: return round(float(h["Close"].iloc[-1]), 4)
        return None
    except Exception: return None

@st.cache_data(ttl=900, show_spinner=False)
def fetch_day_change(ticker):
    """Devuelve (precio_cierre_anterior, variacion_$, variacion_%) o (None,None,None)."""
    if not YF_AVAILABLE: return None, None, None
    try:
        tk   = yf.Ticker(ticker)
        hist = tk.history(period="5d", auto_adjust=True)
        if len(hist) < 2: return None, None, None
        prev  = float(hist["Close"].iloc[-2])
        close = float(hist["Close"].iloc[-1])
        chg   = close - prev
        pct   = chg / prev * 100
        return round(prev, 4), round(chg, 4), round(pct, 2)
    except Exception: return None, None, None

@st.cache_data(ttl=900, show_spinner=False)
def fetch_option_chain(ticker, min_dte, max_dte):
    if not YF_AVAILABLE: return pd.DataFrame()
    today = date.today()
    exp_min = today + timedelta(days=min_dte)
    exp_max = today + timedelta(days=max_dte)
    try:
        tk = yf.Ticker(ticker)
        expirations = tk.options
    except Exception: return pd.DataFrame()
    if not expirations: return pd.DataFrame()

    all_records = []
    for exp_str in expirations:
        try: exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
        except ValueError: continue
        if not (exp_min <= exp_date <= exp_max): continue
        try: chain = tk.option_chain(exp_str)
        except Exception: continue
        for df_raw, right_label in [(chain.calls, "C"), (chain.puts, "P")]:
            if df_raw is None or df_raw.empty: continue
            df = df_raw.copy()
            df = df.rename(columns={"openInterest": "open_interest", "impliedVolatility": "iv"})
            for col in ["strike", "bid", "ask", "volume", "open_interest", "iv"]:
                if col not in df.columns: df[col] = np.nan
            df["expiration"] = exp_date
            df["right"]      = right_label
            df["gamma"]      = np.nan
            df["delta"]      = np.nan
            df["theta"]      = np.nan
            all_records.append(df[["strike","expiration","right",
                                    "bid","ask","volume","open_interest",
                                    "iv","gamma","delta","theta"]])

    if not all_records: return pd.DataFrame()
    out = pd.concat(all_records, ignore_index=True)
    for col in ["strike","bid","ask","volume","open_interest","iv"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out.loc[out["iv"] > 5, "iv"] = np.nan
    out["volume"]        = out["volume"].fillna(0).clip(lower=0)
    out["open_interest"] = out["open_interest"].fillna(0).clip(lower=0)
    out.dropna(subset=["strike"], inplace=True)
    return out.sort_values(["expiration","right","strike"]).reset_index(drop=True)

@st.cache_data(ttl=900, show_spinner=False)
def fetch_stock_history(ticker, days=365):
    if not YF_AVAILABLE: return pd.DataFrame()
    try:
        tk = yf.Ticker(ticker)
        period_map = [(30,"1mo"),(90,"3mo"),(180,"6mo"),(365,"1y"),(730,"2y")]
        period = next((p for d, p in period_map if days <= d), "5y")
        hist = tk.history(period=period, auto_adjust=True)
        if hist.empty: return pd.DataFrame()
        hist = hist.reset_index()
        dc = "Date" if "Date" in hist.columns else "Datetime"
        hist.rename(columns={dc:"date","Open":"open","High":"high",
                              "Low":"low","Close":"close","Volume":"volume"}, inplace=True)
        hist["date"] = pd.to_datetime(hist["date"]).dt.date
        for c in ["open","high","low","close","volume"]:
            hist[c] = pd.to_numeric(hist[c], errors="coerce")
        return hist[["date","open","high","low","close","volume"]].dropna(subset=["close"]).tail(days).reset_index(drop=True)
    except Exception: return pd.DataFrame()


# =============================================================================
# BLOQUE 2 – GRIEGAS BSM (vectorizado)
# =============================================================================

def _bsm_d1d2(S, K, T, r, iv):
    with np.errstate(divide="ignore", invalid="ignore"):
        safe_T  = np.maximum(T, 1e-10)
        safe_K  = np.where(K > 0, K, np.nan)
        d1 = np.where(
            (T > 0) & (iv > 0) & (S > 0) & (K > 0),
            (np.log(S / safe_K) + (r + 0.5 * iv**2) * safe_T) / (iv * np.sqrt(safe_T)),
            np.nan,
        )
    return d1, d1 - iv * np.sqrt(np.maximum(T, 1e-10))

def enrich_greeks(chain, spot, r=0.05):
    if chain.empty or not SCIPY_AVAILABLE: return chain
    chain = chain.copy()
    for col in ["gamma","delta","theta"]:
        if col not in chain.columns: chain[col] = np.nan

    today   = date.today()
    T       = np.array([(e - today).days for e in chain["expiration"]], dtype=float) / 365.0
    K       = chain["strike"].values.astype(float)
    iv      = chain["iv"].fillna(0.4).values.astype(float)
    is_call = (chain["right"] == "C").values
    S       = float(spot)

    d1, d2  = _bsm_d1d2(S, K, T, r, iv)
    safe_T  = np.maximum(T, 1e-10)
    e_rT    = np.exp(-r * safe_T)

    gamma = np.where(np.isfinite(d1),
                     norm.pdf(d1) / (S * iv * np.sqrt(safe_T)), np.nan)
    delta = np.where(np.isfinite(d1),
                     np.where(is_call, norm.cdf(d1), norm.cdf(d1) - 1), np.nan)
    th_c  = (-S * norm.pdf(d1) * iv / (2 * np.sqrt(safe_T))
             - r * K * e_rT * norm.cdf(d2)) / 365.0
    th_p  = (-S * norm.pdf(d1) * iv / (2 * np.sqrt(safe_T))
             + r * K * e_rT * norm.cdf(-d2)) / 365.0
    theta = np.where(np.isfinite(d1),
                     np.where(is_call, th_c, th_p), np.nan)

    chain["gamma"] = gamma
    chain["delta"] = delta
    chain["theta"] = theta
    return chain


# =============================================================================
# BLOQUE 3 – GEX
# =============================================================================

def calculate_gex(chain, spot):
    if chain.empty: return pd.DataFrame()
    df = chain.copy()
    df["gamma"]         = pd.to_numeric(df["gamma"], errors="coerce").fillna(0)
    df["open_interest"] = pd.to_numeric(df["open_interest"], errors="coerce").fillna(0)
    df["gex_raw"]       = df["gamma"] * df["open_interest"] * 100 * spot
    calls = df[df["right"]=="C"].groupby("strike")["gex_raw"].sum().rename("gex_call")
    puts  = df[df["right"]=="P"].groupby("strike")["gex_raw"].sum().rename("gex_put")
    gex   = pd.DataFrame({"gex_call": calls, "gex_put": puts}).fillna(0)
    gex["gex_net"] = gex["gex_call"] - gex["gex_put"]
    return gex.reset_index().sort_values("strike").reset_index(drop=True)

def calculate_gex_heatmap(chain, spot):
    if chain.empty: return pd.DataFrame()
    df = chain.copy()
    df["gamma"]         = pd.to_numeric(df["gamma"], errors="coerce").fillna(0)
    df["open_interest"] = pd.to_numeric(df["open_interest"], errors="coerce").fillna(0)
    df["gex_signed"]    = np.where(
        df["right"]=="C",
         df["gamma"] * df["open_interest"] * 100 * spot,
        -df["gamma"] * df["open_interest"] * 100 * spot,
    )
    return df.groupby(["strike","expiration"])["gex_signed"].sum().unstack("expiration").fillna(0)

def find_zero_gamma(gex):
    """Interpola el precio donde GEX neto cruza cero. Devuelve None si no hay cruce."""
    if gex.empty or "gex_net" not in gex.columns: return None
    df     = gex.sort_values("strike").copy()
    signs  = np.sign(df["gex_net"].values)
    cross  = np.where(np.diff(signs) != 0)[0]
    if len(cross) == 0: return None
    idx    = cross[len(cross) // 2]
    s1, v1 = df.iloc[idx]["strike"],   df.iloc[idx]["gex_net"]
    s2, v2 = df.iloc[idx+1]["strike"], df.iloc[idx+1]["gex_net"]
    if v2 == v1: return float((s1 + s2) / 2)
    return float(s1 - v1 * (s2 - s1) / (v2 - v1))


# =============================================================================
# BLOQUE 4 – VOLUME PROFILE (OHLCV)
# =============================================================================

def compute_volume_profile(hist, n_bins=150):
    if hist.empty or "close" not in hist.columns: return pd.DataFrame()
    df = hist.dropna(subset=["close","volume","high","low"]).copy()
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    min_p, max_p = df["low"].min(), df["high"].max()
    if pd.isna(min_p) or min_p == max_p: return pd.DataFrame()

    bins        = np.linspace(min_p, max_p, n_bins + 1)
    bin_mids    = (bins[:-1] + bins[1:]) / 2
    bin_step    = (max_p - min_p) / n_bins
    vol_profile = np.zeros(n_bins)
    lows   = df["low"].values
    highs  = df["high"].values
    closes = df["close"].values
    vols   = df["volume"].values

    for i in range(len(df)):
        h, l, v = highs[i], lows[i], vols[i]
        if pd.isna(h) or pd.isna(l) or h == l:
            vol_profile[np.abs(bin_mids - closes[i]).argmin()] += v
        else:
            s = max(0, np.searchsorted(bins, l) - 1)
            e = min(n_bins, np.searchsorted(bins, h))
            n = e - s
            if n > 0: vol_profile[s:e] += v / n
            else:     vol_profile[np.abs(bin_mids - (h+l)/2).argmin()] += v

    return pd.DataFrame({"price_mid": bin_mids, "volume": vol_profile,
                          "width": bin_step}).sort_values("price_mid").reset_index(drop=True)


# =============================================================================
# BLOQUE 5 – GRÁFICOS
# =============================================================================

def plot_gex_heatmap(pivot, spot):
    if pivot.empty: return go.Figure()
    z         = pivot.values
    abs_max   = np.nanpercentile(np.abs(z[z != 0]), 95) if z.any() else 1
    text_mat  = np.vectorize(lambda v: _fmt(v, signed=True))(z)
    strikes   = pivot.index.tolist()
    dtick     = _auto_dtick(strikes)

    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in pivot.columns], y=strikes,
        colorscale=[[0,"#f87171"],[0.5,"#111827"],[1,"#4ade80"]],
        zmid=0, zmin=-abs_max, zmax=abs_max,
        text=text_mat, texttemplate="%{text}",
        textfont={"size":10,"family":"Roboto Mono","color":"white"},
        colorbar=dict(title="GEX", tickfont=dict(size=9, color="#cbd5e1"),
                      title_font=dict(color="#94a3b8")),
        hovertemplate="Strike: %{y}<br>Exp: %{x}<br>GEX: %{z:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=spot, line=dict(color="#f59e0b", width=1.5, dash="dot"),
                  annotation_text=f"Spot {spot:.2f}", annotation_font_color="#f59e0b")
    fig.update_layout(title="GEX Heatmap — Strike × Expiración", height=800, **PLOTLY_TEMPLATE)
    fig.update_xaxes(type="category", title_text="Expiración")
    fig.update_yaxes(dtick=dtick, title_text="Strike ($)")
    return fig

def plot_gex_bar(gex, spot, strike_range, zero_gamma=None):
    if gex.empty: return go.Figure()
    df = gex[(gex["strike"] >= strike_range[0]) & (gex["strike"] <= strike_range[1])].copy()
    if df.empty: return go.Figure()

    call_wall = df.loc[df["gex_net"].idxmax(), "strike"]
    put_wall  = df.loc[df["gex_net"].idxmin(), "strike"]
    colors    = ["#4ade80" if v > 0 else "#f87171" for v in df["gex_net"]]
    dtick     = _auto_dtick(df["strike"].tolist())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["gex_net"], y=df["strike"], orientation="h",
        marker_color=colors, opacity=0.85,
        text=df["gex_net"].apply(lambda x: _fmt(x, signed=True)),
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=10, family="Roboto Mono"),
        hovertemplate="Strike %{y}: %{x:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=spot, line=dict(color="#38bdf8", width=1.5, dash="dot"),
                  annotation_text=f"◆ Spot {spot:.2f}", annotation_font_color="#38bdf8")
    fig.add_hline(y=call_wall, line=dict(color="#4ade80", width=1, dash="dash"),
                  annotation_text=f"Call Wall {call_wall}", annotation_font_color="#4ade80")
    fig.add_hline(y=put_wall, line=dict(color="#f87171", width=1, dash="dash"),
                  annotation_text=f"Put Wall {put_wall}", annotation_font_color="#f87171")
    if zero_gamma is not None:
        fig.add_hline(y=zero_gamma,
                      line=dict(color="#f59e0b", width=2, dash="longdash"),
                      annotation_text=f"⚡ Zero Gamma {zero_gamma:.2f}",
                      annotation_font_color="#f59e0b",
                      annotation_position="bottom right")

    max_abs = df["gex_net"].abs().max() * 1.25
    fig.update_layout(
        title="GEX Neto por Strike — Call Wall · Put Wall · Zero Gamma",
        xaxis_title="Net GEX", yaxis_title="Strike", height=850, bargap=0.2,
        **PLOTLY_TEMPLATE,
    )
    fig.update_xaxes(range=[-max_abs, max_abs], showgrid=True)
    fig.update_yaxes(dtick=dtick)
    return fig

def plot_open_interest(chain, spot, strike_range):
    if chain.empty: return go.Figure()
    df    = chain[(chain["strike"] >= strike_range[0]) & (chain["strike"] <= strike_range[1])].copy()
    calls = df[df["right"]=="C"].groupby("strike")["open_interest"].sum()
    puts  = df[df["right"]=="P"].groupby("strike")["open_interest"].sum()
    all_s = sorted(set(calls.index) | set(puts.index))
    dtick = _auto_dtick(all_s)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=calls.reindex(all_s, fill_value=0).values, y=all_s,
                         orientation="h", name="Calls OI", marker_color="#4ade80", opacity=0.8))
    fig.add_trace(go.Bar(x=-puts.reindex(all_s, fill_value=0).values, y=all_s,
                         orientation="h", name="Puts OI", marker_color="#f87171", opacity=0.8))
    fig.add_vline(x=0, line=dict(color="#334155", width=1))
    fig.add_hline(y=spot, line=dict(color="#f59e0b", width=1.5, dash="dot"),
                  annotation_text=f"Spot {spot:.2f}", annotation_font_color="#f59e0b")
    fig.update_layout(title="Open Interest por Strike — Calls vs Puts",
                      barmode="overlay", height=800,
                      xaxis_title="Open Interest", yaxis_title="Strike", **PLOTLY_TEMPLATE)
    fig.update_yaxes(dtick=dtick)
    return fig

def plot_tv_volume_profile(vp, spot, hist, agg="D"):
    if vp.empty or hist.empty: return go.Figure()
    if agg != "D":
        h = hist.copy()
        h["date"] = pd.to_datetime(h["date"])
        h = (h.set_index("date")
              .resample(agg)
              .agg({"open":"first","high":"max","low":"min","close":"last","volume":"sum"})
              .dropna(subset=["close"])
              .reset_index())
        h["date"] = h["date"].dt.date
    else:
        h = hist.copy()

    fig = make_subplots(rows=1, cols=2, column_widths=[0.8, 0.2],
                        shared_yaxes=True, horizontal_spacing=0)
    fig.add_trace(go.Candlestick(
        x=h["date"], open=h["open"], high=h["high"], low=h["low"], close=h["close"],
        name="Precio", increasing_line_color="#4ade80", decreasing_line_color="#f87171",
    ), row=1, col=1)

    hvn_thr    = vp["volume"].quantile(0.75)
    bar_colors = ["#38bdf8" if v >= hvn_thr else "rgba(148,163,184,0.25)" for v in vp["volume"]]
    fig.add_trace(go.Bar(
        x=vp["volume"], y=vp["price_mid"], orientation="h",
        width=vp["width"], marker_color=bar_colors, marker_line_width=0,
        showlegend=False,
        hovertemplate="Precio: %{y:.2f}<br>Vol: %{x:,.0f}<extra></extra>",
    ), row=1, col=2)

    fig.add_hline(y=spot, line=dict(color="#f59e0b", width=1.5, dash="dot"),
                  annotation_text=f"Spot ${spot:.2f}", annotation_font_color="#f59e0b")
    fig.update_layout(
        title="Precio + Volume Profile (HVN azul = imanes macro)",
        xaxis_rangeslider_visible=False, barmode="overlay",
        height=800, bargap=0, bargroupgap=0, **PLOTLY_TEMPLATE,
    )
    fig.update_xaxes(showgrid=True, title="Fecha", row=1, col=1,
                     tickfont=dict(color="#cbd5e1"), title_font=dict(color="#94a3b8"))
    fig.update_xaxes(autorange="reversed", showgrid=False, title="Volumen", row=1, col=2,
                     tickfont=dict(color="#cbd5e1"), title_font=dict(color="#94a3b8"))
    fig.update_yaxes(showgrid=True, title="Precio ($)", row=1, col=1,
                     tickfont=dict(color="#cbd5e1"), title_font=dict(color="#94a3b8"))
    return fig


# =============================================================================
# BLOQUE 6 – ESCÁNER WHEEL
# =============================================================================

def _vp_support_level(vp, spot, pct=0.02):
    if vp.empty: return spot * 0.90
    below = vp[vp["price_mid"] < spot * (1 - pct)]
    return float(below.loc[below["volume"].idxmax(), "price_mid"]) if not below.empty else float(vp.iloc[0]["price_mid"])

def _vp_resistance_level(vp, spot, pct=0.01):
    if vp.empty: return spot * 1.05
    above = vp[vp["price_mid"] > spot * (1 + pct)]
    return float(above.loc[above["volume"].idxmax(), "price_mid"]) if not above.empty else float(vp.iloc[-1]["price_mid"])

def scan_wheel_opportunities(chain, spot, vp, ticker,
                              min_iv, min_oi, min_prem,
                              min_dte, max_dte, max_delta, use_vp):
    if chain.empty: return pd.DataFrame()
    today = date.today()
    df = chain.copy()
    df["dte"]          = df["expiration"].apply(lambda e: max((e - today).days, 0))
    df["mid"]          = ((df["bid"] + df["ask"]) / 2).clip(lower=0)
    df["iv_pct"]       = (df["iv"] * 100).round(1)
    df["annual_yield"] = np.where(df["dte"] > 0, df["mid"] / spot * 365 / df["dte"] * 100, 0).clip(0, 500)
    df["spread_pct"]   = np.where(df["mid"] > 0, (df["ask"]-df["bid"]).clip(lower=0)/df["mid"]*100, 999)
    df["delta"]        = pd.to_numeric(df["delta"], errors="coerce")
    df["theta"]        = pd.to_numeric(df["theta"], errors="coerce")

    df = df[
        (df["dte"] >= min_dte) & (df["dte"] <= max_dte) &
        (df["open_interest"] >= min_oi) & (df["spread_pct"] <= 40) &
        (df["delta"].abs() <= max_delta)
    ]

    if use_vp:
        sup = _vp_support_level(vp, spot)
        res = _vp_resistance_level(vp, spot)
        csp = (df["right"]=="P") & (df["iv"]>=min_iv) & (df["mid"]>=min_prem) & (df["strike"]<=sup)
        cc  = (df["right"]=="C") & (df["mid"]>=min_prem) & (df["strike"]>=res)
    else:
        csp = (df["right"]=="P") & (df["iv"]>=min_iv) & (df["mid"]>=min_prem) & (df["strike"]<spot)
        cc  = (df["right"]=="C") & (df["mid"]>=min_prem) & (df["strike"]>spot)

    valid = df[csp | cc].copy()
    if valid.empty: return pd.DataFrame()

    valid["Estrategia"] = np.where(valid["right"]=="P", "Venta Put (CSP)", "Covered Call (CC)")
    valid = valid.sort_values("annual_yield", ascending=False).head(50)

    out = valid[[
        "Estrategia","strike","expiration","dte","right",
        "bid","ask","mid","delta","theta","iv_pct",
        "open_interest","annual_yield","spread_pct",
    ]].rename(columns={
        "strike":"Strike","expiration":"Expiración","dte":"DTE","right":"Tipo",
        "bid":"Bid","ask":"Ask","mid":"Mid","delta":"Delta","theta":"Theta/día",
        "iv_pct":"IV (%)","open_interest":"OI",
        "annual_yield":"Yield Anual (%)","spread_pct":"Spread (%)",
    }).copy()

    out["Ticker"]          = ticker
    out["Bid"]             = out["Bid"].apply(lambda x: f"${x:.2f}")
    out["Ask"]             = out["Ask"].apply(lambda x: f"${x:.2f}")
    out["Mid"]             = out["Mid"].apply(lambda x: f"${x:.2f}")
    out["Delta"]           = out["Delta"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    out["Theta/día"]       = out["Theta/día"].apply(lambda x: f"${x:.3f}" if pd.notna(x) else "N/A")
    out["Yield Anual (%)"] = out["Yield Anual (%)"].apply(lambda x: f"{x:.1f}%")
    out["Spread (%)"]      = out["Spread (%)"].apply(lambda x: f"{x:.1f}%")
    out["IV (%)"]          = out["IV (%)"].apply(lambda x: f"{x:.1f}%")
    out["Expiración"]      = out["Expiración"].astype(str)
    return out.reset_index(drop=True)


# =============================================================================
# BLOQUE 7 – DATOS DEMO
# =============================================================================

def generate_demo_chain(ticker, spot, exp_dates, n_strikes=20):
    np.random.seed(abs(hash(ticker)) % (2**31))
    records = []
    strikes = np.round(np.linspace(spot * 0.75, spot * 1.25, n_strikes), 1)
    for exp in exp_dates:
        dte = max((exp - date.today()).days, 1)
        T   = dte / 365.0
        biv = np.random.uniform(0.35, 0.75)
        for strike in strikes:
            iv  = biv * (1 + 0.3 * abs(strike/spot - 1))
            oi  = int(np.random.lognormal(7, 1.5))
            for right in ["C","P"]:
                itr = max(0, spot-strike) if right=="C" else max(0, strike-spot)
                mid = round(itr + iv*spot*np.sqrt(T)*0.4, 2)
                spd = round(mid*0.08+0.05, 2)
                records.append({
                    "strike":float(strike),"expiration":exp,"right":right,
                    "bid":round(max(0,mid-spd/2),2),"ask":round(mid+spd/2,2),
                    "volume":int(oi*0.1),"open_interest":oi,
                    "gamma":np.nan,"delta":np.nan,"theta":np.nan,"iv":round(iv,4),
                })
    return pd.DataFrame(records).sort_values(["expiration","strike"]).reset_index(drop=True)

def generate_demo_history(spot, days=365):
    np.random.seed(int(spot*10) % 1000)
    dates  = [date.today()-timedelta(days=i) for i in range(days, 0, -1)]
    closes = [spot]
    for _ in range(days-1): closes.append(closes[-1]*(1+np.random.normal(0,0.018)))
    return pd.DataFrame({
        "date":dates,"close":closes,
        "volume":np.random.lognormal(15,0.5,days).astype(int),
        "high":[p*(1+abs(np.random.normal(0,0.008))) for p in closes],
        "low": [p*(1-abs(np.random.normal(0,0.008))) for p in closes],
        "open":closes,
    })


# =============================================================================
# BLOQUE 8 – UI HELPERS
# =============================================================================

def metric_card(label, value, delta="", positive=True):
    d_cls  = "pos" if positive else "neg"
    d_html = f'<div class="delta {d_cls}">{delta}</div>' if delta else ""
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'{d_html}</div>',
        unsafe_allow_html=True,
    )

def price_card(spot, chg, pct):
    """Tarjeta destacada para el precio actual + variación del día."""
    if chg is None:
        delta_html = ""
    else:
        sign  = "+" if chg >= 0 else ""
        color = "#4ade80" if chg >= 0 else "#f87171"
        arrow = "▲" if chg >= 0 else "▼"
        delta_html = (
            f'<div class="delta" style="color:{color}; font-size:0.9rem; font-weight:600;">'
            f'{arrow} {sign}{chg:.2f} ({sign}{pct:.2f}%) hoy'
            f'</div>'
        )
    st.markdown(
        f'<div class="price-card">'
        f'<div class="label">💹 Precio Actual</div>'
        f'<div class="value">${spot:,.2f}</div>'
        f'{delta_html}</div>',
        unsafe_allow_html=True,
    )

def zero_gamma_card(zg, spot):
    if zg is None:
        st.markdown(
            '<div class="flip-card"><div class="label">⚡ Zero Gamma</div>'
            '<div class="value" style="color:#64748b;">N/D</div>'
            '<div class="sub">Sin cruce de signo en el rango</div></div>',
            unsafe_allow_html=True,
        )
        return
    above = spot > zg
    col   = "#4ade80" if above else "#f87171"
    reg   = "Régimen POSITIVO · Mean-Reversion" if above else "Régimen NEGATIVO · Trending"
    dist  = abs((spot - zg) / spot * 100)
    st.markdown(
        f'<div class="flip-card" style="border-color:{col}55;">'
        f'<div class="label">⚡ Zero Gamma</div>'
        f'<div class="value" style="color:{col};">${zg:.2f}</div>'
        f'<div class="sub">{reg} · {dist:.1f}% del flip</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def show_status_banner(yf_ok, demo_mode):
    if not yf_ok:
        st.markdown('<div class="err-box">❌ <b>yfinance no instalado.</b> '
                    'Ejecuta: <code>pip install yfinance</code></div>', unsafe_allow_html=True)
    elif demo_mode:
        st.markdown('<div class="warn-box">⚠️ <b>MODO DEMO</b> — '
                    'Fallo de conexión o ticker inválido. Datos sintéticos.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box" style="margin:0 0 0.75rem 0; padding:0.5rem 1rem;">'
                    '✅ <b>Yahoo Finance</b> — Conectado (~15 min delay en sesión).</div>',
                    unsafe_allow_html=True)


# =============================================================================
# BLOQUE 9 – APP PRINCIPAL
# =============================================================================

def main():
    st.markdown("""
    <div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:0.75rem;">
      <h1 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#f1f5f9;margin:0;letter-spacing:-0.03em;">GEX Wheel</h1>
      <span style="font-family:'DM Mono',monospace;font-size:0.9rem;
                   color:#93c5fd;letter-spacing:0.05em;">DASHBOARD</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-header">⚙ Ticker y Rango</div>', unsafe_allow_html=True)
        ticker = st.text_input("Ticker", value="IREN").upper().strip()

        c1, c2 = st.columns(2)
        with c1: min_dte = st.number_input("DTE Mín.", min_value=1,  max_value=90,  value=4,  step=1)
        with c2: max_dte = st.number_input("DTE Máx.", min_value=7,  max_value=365, value=30, step=1)
        strike_pct    = st.slider("Strikes ± % spot", 5, 40, 20, 1)
        vp_days       = st.slider("Días Histórico (VP)", 30, 730, 365, 30)
        n_exp_heatmap = st.slider("Expiraciones en Heatmap", 2, 12, 5, 1)

        st.markdown("---")
        st.markdown('<div class="sidebar-header">🎯 Escáner</div>', unsafe_allow_html=True)
        use_vp         = st.checkbox("Exigir Muro de Volumen (VP)", value=False)
        scan_max_delta = st.slider("Delta Abs. Máxima", 0.05, 0.50, 0.35, 0.01)
        scan_min_iv    = st.slider("IV Mínima (%)", 10, 200, 90, 5) / 100
        scan_min_oi    = st.number_input("OI Mínimo", min_value=0, value=500, step=10)
        scan_min_prem  = st.number_input("Prima Mínima ($)", min_value=0.01, value=0.90, step=0.05)

        st.markdown("---")
        load_btn = st.button("🔄 Cargar Datos", use_container_width=True)

    # ── Estado de sesión ─────────────────────────────────────────────────────
    defaults = dict(chain=pd.DataFrame(), hist=pd.DataFrame(), vp=pd.DataFrame(),
                    spot=None, chg=None, pct=None,
                    ticker="", loaded=False, demo_mode=False)
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    # ── Carga ─────────────────────────────────────────────────────────────────
    if load_btn or (ticker != st.session_state.ticker) or not st.session_state.loaded:
        demo_mode = False
        with st.spinner(f"Descargando **{ticker}**…"):
            spot = fetch_spot_price(ticker) if YF_AVAILABLE else None
            _, chg, pct = fetch_day_change(ticker) if YF_AVAILABLE else (None, None, None)

            if spot is None:
                demo_mode = True
                spot = {"IREN":12.5,"KEEL":4.8,"NBIS":22.3}.get(ticker, 50.0)
                chg, pct = None, None
                exp_d = [date.today()+timedelta(days=d)
                         for d in range(min_dte, max_dte+1)
                         if (date.today()+timedelta(days=d)).weekday()==4]
                if not exp_d: exp_d = [date.today()+timedelta(days=max_dte)]
                chain = generate_demo_chain(ticker, spot, exp_d)
                hist  = generate_demo_history(spot, vp_days)
            else:
                chain = fetch_option_chain(ticker, min_dte, max_dte)
                hist  = fetch_stock_history(ticker, vp_days)
                if not chain.empty:
                    with st.spinner("Calculando Griegas…"):
                        chain = enrich_greeks(chain, spot)

        vp = compute_volume_profile(hist, n_bins=150) if not hist.empty else pd.DataFrame()
        st.session_state.update(chain=chain, hist=hist, vp=vp,
                                spot=spot, chg=chg, pct=pct,
                                ticker=ticker, loaded=True, demo_mode=demo_mode)

    chain     = st.session_state.chain
    hist      = st.session_state.hist
    vp        = st.session_state.vp
    spot      = st.session_state.spot
    chg       = st.session_state.chg
    pct       = st.session_state.pct
    demo_mode = st.session_state.demo_mode

    show_status_banner(YF_AVAILABLE, demo_mode)
    if not st.session_state.loaded or spot is None:
        st.info("Introduce un ticker y pulsa Cargar Datos.")
        return

    # ── Rango de strikes ──────────────────────────────────────────────────────
    strike_lo    = spot * (1 - strike_pct/100)
    strike_hi    = spot * (1 + strike_pct/100)
    strike_range = (strike_lo, strike_hi)
    chain_f = chain[(chain["strike"]>=strike_lo)&(chain["strike"]<=strike_hi)] if not chain.empty else chain

    # ── Métricas de cabecera ──────────────────────────────────────────────────
    gex_all    = calculate_gex(chain_f, spot)
    zero_gamma = find_zero_gamma(gex_all)
    c_oi = int(chain_f[chain_f["right"]=="C"]["open_interest"].sum()) if not chain_f.empty else 0
    p_oi = int(chain_f[chain_f["right"]=="P"]["open_interest"].sum()) if not chain_f.empty else 0
    pcr  = p_oi / c_oi if c_oi > 0 else float("nan")
    gex_tot = gex_all["gex_net"].sum() if not gex_all.empty else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: price_card(spot, chg, pct)
    with col2: metric_card("Call OI Total", f"{c_oi:,}", positive=True)
    with col3: metric_card("Put OI Total",  f"{p_oi:,}", positive=False)
    with col4:
        metric_card("Put/Call Ratio",
                    f"{pcr:.2f}" if not np.isnan(pcr) else "N/D",
                    positive=(pcr < 0.8) if not np.isnan(pcr) else True)
    with col5:
        metric_card("GEX Neto", _fmt(gex_tot, signed=True) or "0",
                    positive=(gex_tot >= 0))
    with col6:
        zero_gamma_card(zero_gamma, spot)

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_gex, tab_oi, tab_vp, tab_wheel = st.tabs([
        "📊  GEX Analysis",
        "📈  Open Interest",
        "🗺  Volume Profile",
        "🎯  Escáner Wheel",
    ])

    # ── TAB GEX ───────────────────────────────────────────────────────────────
    with tab_gex:
        st.markdown("""
        <div class="info-box">
            <strong>🧠 Cómo interpretar el GEX:</strong><br>
            • <strong>Call Wall (barra verde mayor):</strong> Techo/Resistencia. Los MM venden el subyacente para frenar la subida.<br>
            • <strong>Put Wall (barra roja mayor):</strong> Suelo/Soporte. Los MM compran para frenar la caída.<br>
            • <strong>⚡ Zero Gamma (línea naranja):</strong> Nivel crítico. Por encima → régimen tranquilo (mean-reversion). Por debajo → régimen volátil (trending acelerado).<br>
            • <strong>Verde:</strong> El precio tiende a lateralizar o rebotar. <strong>Rojo:</strong> Movimientos se aceleran.
        </div>
        """, unsafe_allow_html=True)

        if not chain_f.empty:
            pivot = calculate_gex_heatmap(chain_f, spot)
            if not pivot.empty:
                st.plotly_chart(plot_gex_heatmap(pivot.iloc[:, :n_exp_heatmap], spot),
                                use_container_width=True)

            st.markdown('<div class="section-title">GEX Neto por Strike</div>', unsafe_allow_html=True)
            exp_opts = ["Todas las Fechas"] + sorted(chain_f["expiration"].unique().tolist())
            sel_exp  = st.selectbox("Filtrar por Vencimiento:", exp_opts,
                                    index=1 if len(exp_opts) > 1 else 0, key="sel_gex")
            ch_gex   = chain_f if sel_exp == "Todas las Fechas" else chain_f[chain_f["expiration"]==sel_exp]
            gex_f    = calculate_gex(ch_gex, spot)
            zg_f     = find_zero_gamma(gex_f)
            st.plotly_chart(plot_gex_bar(gex_f, spot, strike_range, zero_gamma=zg_f),
                            use_container_width=True)

    # ── TAB OI ────────────────────────────────────────────────────────────────
    with tab_oi:
        st.markdown("""
        <div class="info-box">
            <strong>👀 Cómo interpretar el Open Interest:</strong><br>
            • El OI indica <strong>compromiso a medio plazo</strong>, no actividad intradiaria.<br>
            • Strikes con gran OI actúan como <strong>imanes</strong>. Las manos fuertes los defenderán, especialmente cerca de OpEx.
        </div>
        """, unsafe_allow_html=True)

        if not chain_f.empty:
            exp_opts_oi = ["Todas las Fechas"] + sorted(chain_f["expiration"].unique().tolist())
            sel_oi      = st.selectbox("Filtrar por Vencimiento:", exp_opts_oi,
                                       index=1 if len(exp_opts_oi) > 1 else 0, key="sel_oi")
            ch_oi = chain_f if sel_oi == "Todas las Fechas" else chain_f[chain_f["expiration"]==sel_oi]
            st.plotly_chart(plot_open_interest(ch_oi, spot, strike_range), use_container_width=True)

    # ── TAB VP ────────────────────────────────────────────────────────────────
    with tab_vp:
        st.markdown("""
        <div class="info-box">
            <strong>🗺️ Cómo interpretar el Volume Profile:</strong><br>
            • <strong>HVN — barras azules:</strong> Zonas de gran aceptación. Potentes imanes y muros de soporte/resistencia.<br>
            • <strong>LVN — barras grises:</strong> Zonas de rechazo. El precio las atraviesa rápido hasta el siguiente HVN.<br>
            • Método OHLCV: el volumen de cada vela se distribuye proporcionalmente entre todos los niveles que toca.
        </div>
        """, unsafe_allow_html=True)

        if not hist.empty:
            agg_opt = st.radio("Resolución:", ["Diario","Semanal","Mensual"], horizontal=True, index=0)
            agg_map = {"Diario":"D","Semanal":"W","Mensual":"ME"}
            st.plotly_chart(plot_tv_volume_profile(vp, spot, hist, agg=agg_map[agg_opt]),
                            use_container_width=True)

    # ── TAB WHEEL ─────────────────────────────────────────────────────────────
    with tab_wheel:
        st.markdown("""
        <div class="info-box">
            <strong>🎯 Cómo usar el Escáner Wheel:</strong><br>
            • <strong>Venta de Puts (CSP):</strong> Strikes por debajo del precio. Cobras la prima asumiendo comprar la acción más barata si cae.<br>
            • <strong>Covered Calls (CC):</strong> Strikes por encima. Cobras por vender tus acciones a mayor precio.<br>
            • <strong>Delta:</strong> Probabilidad de asignación. <strong>Theta/día:</strong> $ que ganas cada día por decaimiento.
        </div>
        """, unsafe_allow_html=True)

        res = scan_wheel_opportunities(
            chain=st.session_state.chain, spot=spot, vp=vp, ticker=ticker,
            min_iv=scan_min_iv, min_oi=scan_min_oi, min_prem=scan_min_prem,
            min_dte=min_dte, max_dte=max_dte, max_delta=scan_max_delta, use_vp=use_vp,
        )

        if not res.empty:
            csp_res = res[res["Estrategia"]=="Venta Put (CSP)"]
            cc_res  = res[res["Estrategia"]=="Covered Call (CC)"]

            # Altura de tabla fija igual para ambas (basada en la más larga → puts)
            n_rows    = max(len(csp_res), len(cc_res), 1)
            row_h     = 35
            header_h  = 38
            tbl_h     = min(header_h + n_rows * row_h, 600)

            drop_cols = ["Ticker","Estrategia"]

            st.markdown(f'<div class="section-title">🔻 Ventas de Put — CSP ({len(csp_res)} contratos)</div>',
                        unsafe_allow_html=True)
            if not csp_res.empty:
                st.dataframe(csp_res.drop(columns=drop_cols, errors="ignore"),
                             use_container_width=True, hide_index=True, height=tbl_h)
            else:
                st.info("Sin puts que cumplan los criterios.")

            st.markdown(f'<div class="section-title">🔺 Covered Calls — CC ({len(cc_res)} contratos)</div>',
                        unsafe_allow_html=True)
            if not cc_res.empty:
                st.dataframe(cc_res.drop(columns=drop_cols, errors="ignore"),
                             use_container_width=True, hide_index=True, height=tbl_h)
            else:
                st.info("Sin calls que cumplan los criterios.")

            try:
                best_yield = res["Yield Anual (%)"].str.replace("%","",regex=False).astype(float).max()
            except Exception:
                best_yield = float("nan")

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            with m1: metric_card("Oportunidades CSP", str(len(csp_res)), positive=True)
            with m2: metric_card("Oportunidades CC",  str(len(cc_res)),  positive=True)
            with m3: metric_card("Mejor Yield Anual",
                                 f"{best_yield:.1f}%" if not np.isnan(best_yield) else "N/D",
                                 positive=True)
        else:
            st.info("Ningún contrato cumple los criterios. "
                    "Reduce Prima mínima / OI mínimo o desactiva el filtro VP.")

        st.markdown("""
        <div class="warn-box">
          ⚠️ <strong>Aviso de riesgo:</strong> Herramienta puramente informativa.
          La venta de opciones implica riesgo de pérdida significativa.
          Opera siempre dentro de tu perfil de riesgo.
        </div>""", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center;color:#334155;font-size:0.7rem;font-family:DM Mono,monospace;">'
        f'GEX Wheel Dashboard · Yahoo Finance · Streamlit · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}'
        f'{"  ·  MODO DEMO" if demo_mode else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()