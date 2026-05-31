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
FONT_HEADING = "Inter, sans-serif"
FONT_DATA = "Roboto Mono, monospace"

st.set_page_config(page_title="GEX Wheel Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;800&display=swap');

  /* Definición de Variables CSS */
  :root {
    --font-heading: 'Inter', sans-serif;
    --font-data: 'Roboto Mono', monospace;
  }
            
  /* ── Token system: dark mode (Streamlit default) ── */
  :root {
    --bg-base:        #0a0d14;
    --bg-surface:     #111827;
    --bg-surface-2:   #1a2235;
    --bg-sidebar:     #080b11;
    --border:         #2d3f55;
    --border-strong:  #3b5070;

    --text-primary:   #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted:     #64748b;
    --text-label:     #94a3b8;

    --accent-blue:    #3b82f6;
    --accent-blue-lt: #93c5fd;
    --accent-green:   #4ade80;
    --accent-red:     #f87171;
    --accent-amber:   #f59e0b;

    --card-price-bg:  linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    --card-price-bdr: #3b82f6;
    --card-price-lbl: #93c5fd;
    --card-price-val: #e0f2fe;

    --card-metric-bg: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    --card-flip-bg:   linear-gradient(135deg, #0f1f0f 0%, #1a2235 100%);
    --card-flip-bdr:  #166534;

    --info-bg:        rgba(59,130,246,0.10);
    --info-bdr:       #3b82f6;
    --info-text:      #cbd5e1;
    --info-strong:    #93c5fd;

    --warn-bg:        rgba(245,158,11,0.10);
    --warn-bdr:       #f59e0b;
    --warn-text:      #fcd34d;

    --err-bg:         rgba(248,113,113,0.10);
    --err-bdr:        #f87171;
    --err-text:       #fca5a5;

    --tab-bg:         #111827;
    --tab-text:       #94a3b8;
    --tab-active-bg:  #1e3a5f;
    --tab-active-txt: #93c5fd;

    --wall-call-bg:   rgba(74,222,128,0.12);
    --wall-call-bdr:  #166534;
    --wall-call-txt:  #4ade80;
    --wall-put-bg:    rgba(248,113,113,0.12);
    --wall-put-bdr:   #7f1d1d;
    --wall-put-txt:   #f87171;
  }

  /* ── Token overrides: light mode ── */
  @media (prefers-color-scheme: light) {
    :root {
      --bg-base:        #f8fafc;
      --bg-surface:     #ffffff;
      --bg-surface-2:   #f1f5f9;
      --bg-sidebar:     #f0f4f8;
      --border:         #cbd5e1;
      --border-strong:  #94a3b8;

      --text-primary:   #0f172a;
      --text-secondary: #1e293b;
      --text-muted:     #64748b;
      --text-label:     #475569;

      --accent-blue:    #2563eb;
      --accent-blue-lt: #1d4ed8;
      --accent-green:   #16a34a;
      --accent-red:     #dc2626;
      --accent-amber:   #d97706;

      --card-price-bg:  linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
      --card-price-bdr: #2563eb;
      --card-price-lbl: #1d4ed8;
      --card-price-val: #0f172a;

      --card-metric-bg: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
      --card-flip-bg:   linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
      --card-flip-bdr:  #16a34a;

      --info-bg:        #eff6ff;
      --info-bdr:       #2563eb;
      --info-text:      #1e3a5f;
      --info-strong:    #1d4ed8;

      --warn-bg:        #fffbeb;
      --warn-bdr:       #d97706;
      --warn-text:      #92400e;

      --err-bg:         #fef2f2;
      --err-bdr:        #dc2626;
      --err-text:       #991b1b;

      --tab-bg:         #f1f5f9;
      --tab-text:       #475569;
      --tab-active-bg:  #dbeafe;
      --tab-active-txt: #1d4ed8;

      --wall-call-bg:   #f0fdf4;
      --wall-call-bdr:  #16a34a;
      --wall-call-txt:  #15803d;
      --wall-put-bg:    #fef2f2;
      --wall-put-bdr:   #dc2626;
      --wall-put-txt:   #b91c1c;
    }
  }

  /* Streamlit también expone data-theme en el HTML root cuando el usuario
     cambia desde el menú de la app — cubrimos ambas vías */
  [data-theme="light"] {
    --bg-base:        #f8fafc;
    --bg-surface:     #ffffff;
    --bg-surface-2:   #f1f5f9;
    --bg-sidebar:     #f0f4f8;
    --border:         #cbd5e1;
    --border-strong:  #94a3b8;

    --text-primary:   #0f172a;
    --text-secondary: #1e293b;
    --text-muted:     #64748b;
    --text-label:     #475569;

    --accent-blue:    #2563eb;
    --accent-blue-lt: #1d4ed8;
    --accent-green:   #16a34a;
    --accent-red:     #dc2626;
    --accent-amber:   #d97706;

    --card-price-bg:  linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    --card-price-bdr: #2563eb;
    --card-price-lbl: #1d4ed8;
    --card-price-val: #0f172a;

    --card-metric-bg: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    --card-flip-bg:   linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    --card-flip-bdr:  #16a34a;

    --info-bg:        #eff6ff;
    --info-bdr:       #2563eb;
    --info-text:      #1e3a5f;
    --info-strong:    #1d4ed8;

    --warn-bg:        #fffbeb;
    --warn-bdr:       #d97706;
    --warn-text:      #92400e;

    --err-bg:         #fef2f2;
    --err-bdr:        #dc2626;
    --err-text:       #991b1b;

    --tab-bg:         #f1f5f9;
    --tab-text:       #475569;
    --tab-active-bg:  #dbeafe;
    --tab-active-txt: #1d4ed8;

    --wall-call-bg:   #f0fdf4;
    --wall-call-bdr:  #16a34a;
    --wall-call-txt:  #15803d;
    --wall-put-bg:    #fef2f2;
    --wall-put-bdr:   #dc2626;
    --wall-put-txt:   #b91c1c;
  }

  /* ── Base layout ── */
  html, body, [class*="css"] {
    font-family: var(--font-data);
    background-color: var(--bg-base) !important;
    color: var(--text-secondary) !important;
  }
  .main, .block-container { background-color: var(--bg-base) !important; }
  .block-container { padding-top: 1.5rem; padding-left: 2rem; padding-right: 2rem; }
  h1, h2, h3 {
    font-family: var(--font-heading);
    letter-spacing: -0.02em;
    color: var(--text-primary) !important;
  }
  p, span, li { color: var(--text-secondary); }

  /* ── Metric cards ── */
  .metric-card {
    background: var(--card-metric-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  .metric-card .label {
    font-size: 0.68rem;
    color: var(--text-label);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .metric-card .value {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--text-primary);
    font-family: var(--font-data);
    margin-top: 0.15rem;
  }
  .metric-card .delta { font-size: 0.78rem; margin-top: 0.15rem; }
  .pos { color: var(--accent-green) !important; }
  .neg { color: var(--accent-red)   !important; }

  /* ── Price card ── */
  .price-card {
    background: var(--card-price-bg);
    border: 1px solid var(--card-price-bdr);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 4px rgba(59,130,246,0.15);
  }
  .price-card .label {
    font-size: 0.68rem;
    color: var(--card-price-lbl);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .price-card .value {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--card-price-val);
    font-family: var(--font-heading);
    margin-top: 0.1rem;
  }
  .price-card .delta { font-size: 0.85rem; margin-top: 0.2rem; font-weight: 600; }

  /* ── Zero Gamma / flip card ── */
  .flip-card {
    background: var(--card-flip-bg);
    border: 1px solid var(--card-flip-bdr);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .flip-card .label {
    font-size: 0.68rem;
    color: var(--text-label);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .flip-card .value {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--accent-green);
    font-family: var(--font-heading);
    margin-top: 0.15rem;
  }
  .flip-card .sub { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.2rem; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 2px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0;
    background: var(--tab-bg);
    color: var(--tab-text);
    border: 1px solid var(--border);
    font-family: var(--font-data);
    font-size: 0.85rem;
    padding: 0.6rem 1.4rem;
    transition: background 0.15s, color 0.15s;
  }
  .stTabs [data-baseweb="tab"]:hover {
    background: var(--bg-surface-2) !important;
    color: var(--text-primary) !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--tab-active-bg) !important;
    color: var(--tab-active-txt) !important;
    border-bottom-color: var(--tab-active-bg) !important;
    font-weight: 600;
  }
  .stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0.5rem 1rem 0.5rem;
  }

  /* ── Sidebar ── */
  div[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
  }
  div[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
  .sidebar-header {
    font-family: var(--font-heading);
    font-size: 1rem;
    font-weight: 800;
    color: var(--accent-blue) !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
  }

  /* ── Streamlit native widgets: labels & inputs ── */
  label,
  .stTextInput label,
  .stNumberInput label,
  .stSlider label,
  .stSelectbox label,
  .stRadio label,
  .stCheckbox label {
    color: var(--text-label) !important;
    font-size: 0.82rem !important;
    font-family: var(--font-heading);
  }
  /* Input boxes */
  .stTextInput input,
  .stNumberInput input {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
  }
  /* Selectbox */
  .stSelectbox > div > div {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
  }
  /* Slider track label */
  .stSlider [data-testid="stTickBar"] { color: var(--text-muted) !important; }
  /* Radio */
  .stRadio > div { color: var(--text-secondary) !important; }

  /* ── Divider ── */
  hr { border-color: var(--border) !important; }

  /* ── Button ── */
  .stButton > button {
    background: linear-gradient(90deg, #1d4ed8, #3b82f6);
    color: #fff !important;
    border: none;
    border-radius: 6px;
    font-family: var(--font-data);
    font-size: 0.82rem;
    padding: 0.45rem 1rem;
    box-shadow: 0 2px 6px rgba(59,130,246,0.3);
    transition: opacity 0.15s, box-shadow 0.15s;
  }
  .stButton > button:hover {
    opacity: 0.88;
    box-shadow: 0 4px 12px rgba(59,130,246,0.4);
  }

  /* ── Info / warn / err boxes ── */
  .info-box {
    background: var(--info-bg);
    border-left: 3px solid var(--info-bdr);
    border-radius: 6px;
    padding: 0.9rem 1rem;
    font-size: 0.83rem;
    color: var(--info-text);
    margin: 0.5rem 0 1.2rem 0;
    line-height: 1.6;
  }
  .info-box strong { color: var(--info-strong); }

  .warn-box {
    background: var(--warn-bg);
    border-left: 3px solid var(--warn-bdr);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: var(--warn-text);
    margin: 0.5rem 0;
    line-height: 1.5;
  }
  .warn-box strong { color: var(--warn-text); }

  .err-box {
    background: var(--err-bg);
    border-left: 3px solid var(--err-bdr);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: var(--err-text);
    margin: 0.5rem 0;
  }

  /* ── Section titles ── */
  .section-title {
    font-family: var(--font-heading);
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.2rem 0 0.5rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid var(--border);
  }

  /* ── Wall badges ── */
  .wall-badge {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: var(--font-data);
  }
  .wall-call {
    background: var(--wall-call-bg);
    color: var(--wall-call-txt);
    border: 1px solid var(--wall-call-bdr);
  }
  .wall-put {
    background: var(--wall-put-bg);
    color: var(--wall-put-txt);
    border: 1px solid var(--wall-put-bdr);
  }

  /* ── Dataframe ── */
  .stDataFrame, [data-testid="stDataFrameResizable"] {
    border-radius: 8px !important;
    overflow: hidden;
    border: 1px solid var(--border) !important;
  }

  /* ── Streamlit info/success/warning native boxes ── */
  .stAlert { border-radius: 6px !important; }

  /* ── Footer text ── */
  .of-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.7rem;
    font-family: var(--font-data);
    margin-top: 0.5rem;
  }
</style>
""", unsafe_allow_html=True)


def _fmt(val, signed=False):
    if pd.isna(val) or val == 0: return ""
    sign = "+" if signed and val > 0 else ("-" if signed and val < 0 else "")
    v = abs(val)
    if v >= 1e9: return f"{sign}{v/1e9:.2f}B"
    if v >= 1e6: return f"{sign}{v/1e6:.2f}M"
    if v >= 1e3: return f"{sign}{v/1e3:.1f}K"
    return f"{sign}{v:.1f}"

def _auto_dtick(strikes):
    if len(strikes) < 2: return 1
    spread = max(strikes) - min(strikes)
    raw = spread / 25
    for step in [0.5, 1, 2, 2.5, 5, 10, 25, 50, 100]:
        if step >= raw: return step
    return round(raw, -1)

def _plotly_theme():
    """
    Layout dict minimalista adaptado para Streamlit.
    Al NO forzar colores de fondo ni ejes, Streamlit intercepta el gráfico
    y le aplica su tema nativo (Light o Dark) en tiempo real.
    """
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto Mono, monospace", size=11),
        title_font=dict(family="Inter, sans-serif", size=14),
        margin=dict(l=55, r=25, t=50, b=45)
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

# FIX: min_dte y max_dte forman parte de la cache key para evitar datos rangeados incorrectos
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
        # FIX: control de errores por vencimiento — un fallo no silencia el resto
        try:
            chain = tk.option_chain(exp_str)
        except Exception as e:
            st.warning(f"No se pudo cargar {exp_str}: {e}", icon="⚠️")
            continue
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
def fetch_dividend_yield(ticker):
    """Obtiene el dividend yield anual del ticker para usarlo en BSM."""
    if not YF_AVAILABLE: return 0.0
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        dy = info.get("dividendYield", 0.0) or 0.0
        return float(dy)
    except Exception: return 0.0

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
# BLOQUE 2 – GRIEGAS BSM con dividendos (Merton 1973)
# =============================================================================

def _bsm_d1d2(S, K, T, r, q, iv):
    """d1/d2 con tasa de dividendos continua q (modelo Merton)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        safe_T = np.maximum(T, 1e-10)
        safe_K = np.where(K > 0, K, np.nan)
        d1 = np.where(
            (T > 0) & (iv > 0) & (S > 0) & (K > 0),
            (np.log(S / safe_K) + (r - q + 0.5 * iv**2) * safe_T) / (iv * np.sqrt(safe_T)),
            np.nan,
        )
    return d1, d1 - iv * np.sqrt(np.maximum(T, 1e-10))

def enrich_greeks(chain, spot, r=0.05, q=0.0):
    """
    Calcula gamma, delta y theta con dividendos.
    q: dividend yield anual continuo (ej: 0.02 para 2%).
    FIX: IV faltante → mediana del vencimiento, no 0.4 fijo.
    """
    if chain.empty or not SCIPY_AVAILABLE: return chain
    chain = chain.copy()
    for col in ["gamma","delta","theta"]:
        if col not in chain.columns: chain[col] = np.nan

    # FIX: Imputar IV faltante con mediana por vencimiento (más representativo que 0.4 global)
    chain["iv"] = chain.groupby("expiration")["iv"].transform(
        lambda x: x.fillna(x.median() if x.notna().any() else 0.4)
    )
    chain["iv"] = chain["iv"].fillna(0.4)  # fallback final si algún vencimiento tiene todo NaN

    today   = date.today()
    T       = np.array([(e - today).days for e in chain["expiration"]], dtype=float) / 365.0
    K       = chain["strike"].values.astype(float)
    iv      = chain["iv"].values.astype(float)
    is_call = (chain["right"] == "C").values
    S       = float(spot)

    d1, d2  = _bsm_d1d2(S, K, T, r, q, iv)
    safe_T  = np.maximum(T, 1e-10)
    e_qT    = np.exp(-q * safe_T)
    e_rT    = np.exp(-r * safe_T)

    # Gamma con dividendos
    gamma = np.where(
        np.isfinite(d1),
        e_qT * norm.pdf(d1) / (S * iv * np.sqrt(safe_T)),
        np.nan,
    )
    # Delta con dividendos
    delta = np.where(
        np.isfinite(d1),
        np.where(is_call,
                 e_qT * norm.cdf(d1),
                 e_qT * (norm.cdf(d1) - 1)),
        np.nan,
    )
    # Theta con dividendos
    th_common = -e_qT * S * norm.pdf(d1) * iv / (2 * np.sqrt(safe_T))
    th_c = (th_common
            + q * S * e_qT * norm.cdf(d1)
            - r * K * e_rT * norm.cdf(d2)) / 365.0
    th_p = (th_common
            - q * S * e_qT * norm.cdf(-d1)
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

# ── Muros por expiración (núcleo del escáner mejorado) ───────────────────────

def get_walls_per_expiration(pivot):
    """
    Para cada columna del heatmap (= una expiración) calcula:
      - call_wall: strike con mayor GEX neto positivo → techo
      - put_wall:  strike con menor GEX neto negativo → suelo

    Devuelve un dict  {exp_str: {"call_wall": float, "put_wall": float}}
    """
    walls = {}
    for exp_str in pivot.columns:
        col = pivot[exp_str]
        pos = col[col > 0]
        neg = col[col < 0]
        call_wall = float(pos.idxmax()) if not pos.empty else None
        put_wall  = float(neg.idxmin()) if not neg.empty else None
        walls[str(exp_str)] = {"call_wall": call_wall, "put_wall": put_wall}
    return walls


# =============================================================================
# BLOQUE 4 – VOLUME PROFILE
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
        # 1. CAMBIO: El punto central (0.5) ahora es blanco "#ffffff"
        colorscale=[[0, "#f87171"], [0.5, "#ffffff"], [1, "#4ade80"]],
        zmid=0, zmin=-abs_max, zmax=abs_max,
        text=text_mat, texttemplate="%{text}",
        # 2. CAMBIO: Quitamos el "color":"white" fijo para que Plotly lo adapte
        textfont={"size": 10, "family": "var(--font-data)"}, 
        colorbar=dict(title="GEX", tickfont=dict(size=9, color="#cbd5e1"),
                      title_font=dict(color="#94a3b8")),
        hovertemplate="Strike: %{y}<br>Exp: %{x}<br>GEX: %{z:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=spot, line=dict(color="#f59e0b", width=1.5, dash="dot"),
                  annotation_text=f"Spot {spot:.2f}", annotation_font_color="#f59e0b")
    PT = _plotly_theme()
    fig.update_layout(title="GEX Heatmap — Strike × Expiración", height=800, **PT)
    fig.update_xaxes(type="category", title_text="Expiración")
    fig.update_yaxes(dtick=dtick, title_text="Strike ($)")
    return fig

def plot_gex_bar(gex, spot, strike_range, zero_gamma=None):
    if gex.empty: return go.Figure()
    df = gex[(gex["strike"] >= strike_range[0]) & (gex["strike"] <= strike_range[1])].copy()
    if df.empty: return go.Figure()

    PT        = _plotly_theme()
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
        textfont=dict(size=10, family="Roboto Mono"), # Color automático
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
        **PT,
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
    PT    = _plotly_theme()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=calls.reindex(all_s, fill_value=0).values, y=all_s,
                         orientation="h", name="Calls OI", marker_color="#4ade80", opacity=0.8))
    fig.add_trace(go.Bar(x=-puts.reindex(all_s, fill_value=0).values, y=all_s,
                         orientation="h", name="Puts OI", marker_color="#f87171", opacity=0.8))
    
    fig.add_vline(x=0, line=dict(color="rgba(150,150,150,0.5)", width=1))
    fig.add_hline(y=spot, line=dict(color="#f59e0b", width=1.5, dash="dot"),
                  annotation_text=f"Spot {spot:.2f}", annotation_font_color="#f59e0b")
    
    fig.update_layout(title="Open Interest por Strike — Calls vs Puts",
                      barmode="overlay", height=800,
                      xaxis_title="Open Interest", yaxis_title="Strike", **PT)
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

    PT = _plotly_theme()

    fig = make_subplots(rows=1, cols=2, column_widths=[0.8, 0.2],
                        shared_yaxes=True, horizontal_spacing=0)
    
    fig.add_trace(go.Candlestick(
        x=h["date"], open=h["open"], high=h["high"], low=h["low"], close=h["close"],
        name="Precio", increasing_line_color="#4ade80", decreasing_line_color="#f87171",
    ), row=1, col=1)

    hvn_thr    = vp["volume"].quantile(0.75)
    bar_colors = ["#3b82f6" if v >= hvn_thr else "rgba(148,163,184,0.4)" for v in vp["volume"]]
    
    fig.add_trace(go.Bar(
        x=vp["volume"], y=vp["price_mid"], orientation="h",
        width=vp["width"], marker_color=bar_colors, marker_line_width=0,
        showlegend=False,
        hovertemplate="Precio: %{y:.2f}<br>Vol: %{x:,.0f}<extra></extra>",
    ), row=1, col=2)

    fig.add_hline(y=spot, line=dict(color="#f59e0b", width=1.5, dash="dot"),
                  annotation_text=f"Spot ${spot:.2f}", annotation_font_color="#f59e0b")
    
    fig.update_layout(
        title="Precio + Volume Profile (HVN = imanes macro)",
        xaxis_rangeslider_visible=False, barmode="overlay",
        height=800, bargap=0, bargroupgap=0, **PT,
    )
    
    # Streamlit coloreará los textos y la cuadrícula automáticamente
    fig.update_xaxes(showgrid=True, title="Fecha", row=1, col=1)
    fig.update_xaxes(autorange="reversed", showgrid=False, title="Volumen", row=1, col=2)
    fig.update_yaxes(showgrid=True, title="Precio ($)", row=1, col=1)
    
    return fig


# =============================================================================
# BLOQUE 6 – ESCÁNER WHEEL CON MUROS GEX POR EXPIRACIÓN
# =============================================================================

def _nearest_strike(strikes_arr, target):
    """Devuelve el strike más cercano a target en el array dado."""
    if len(strikes_arr) == 0: return None
    idx = np.abs(np.array(strikes_arr, dtype=float) - target).argmin()
    return float(strikes_arr[idx])

def scan_wheel_opportunities(chain, spot, pivot, ticker,
                              min_iv, min_oi, min_prem,
                              min_dte, max_dte, max_delta,
                              wall_tol_pct=0.05):
    """
    Escáner Wheel mejorado con muros GEX por expiración.

    Lógica de filtrado:
    - CSP (Venta Put): strike dentro de `wall_tol_pct` % por encima del Put Wall
      de esa expiración. El Put Wall es el soporte donde los MM compran.
    - CC (Covered Call): strike dentro de `wall_tol_pct` % por debajo del Call Wall
      de esa expiración. El Call Wall es el techo donde los MM venden.

    Columnas nuevas:
    - Muro GEX ($): nivel del muro relevante para esa expiración
    - Dist. Muro (%): distancia del strike al muro en %
    - Tipo Muro: Call Wall / Put Wall
    """
    if chain.empty: return pd.DataFrame()

    # Precalcular muros por expiración desde el heatmap
    walls_per_exp = get_walls_per_expiration(pivot) if not pivot.empty else {}

    today = date.today()
    df = chain.copy()
    df["dte"]          = df["expiration"].apply(lambda e: max((e - today).days, 0))
    df["mid"]          = ((df["bid"] + df["ask"]) / 2).clip(lower=0)
    df["iv_pct"]       = (df["iv"] * 100).round(1)
    # FIX: annual_yield usa el capital comprometido real (strike × 100) no el spot
    df["capital"]      = df["strike"] * 100
    df["annual_yield"] = np.where(
        (df["dte"] > 0) & (df["capital"] > 0),
        df["mid"] * 100 / df["capital"] * 365 / df["dte"] * 100,
        0,
    ).clip(0, 500)
    df["spread_pct"]   = np.where(df["mid"] > 0, (df["ask"]-df["bid"]).clip(lower=0)/df["mid"]*100, 999)
    df["delta"]        = pd.to_numeric(df["delta"], errors="coerce")
    df["theta"]        = pd.to_numeric(df["theta"], errors="coerce")

    # Filtros base (DTE, OI, spread, delta)
    df = df[
        (df["dte"] >= min_dte) & (df["dte"] <= max_dte) &
        (df["open_interest"] >= min_oi) & (df["spread_pct"] <= 40) &
        (df["delta"].abs() <= max_delta)
    ]
    if df.empty: return pd.DataFrame()

    # ── Enriquecer con datos de muro por expiración ───────────────────────────
    records = []
    for _, row in df.iterrows():
        exp_str  = str(row["expiration"])
        w        = walls_per_exp.get(exp_str, {})
        call_w   = w.get("call_wall")
        put_w    = w.get("put_wall")
        strike   = row["strike"]
        right    = row["right"]

        if right == "P":
            wall_level = put_w
            wall_label = "Put Wall"
            # CSP válida: strike ≥ put_wall y dentro de tolerancia superior
            if put_w is not None:
                valid_wall = (strike >= put_w) and (strike <= put_w * (1 + wall_tol_pct))
            else:
                # Sin datos de heatmap: acepta puts OTM genéricas (comportamiento anterior)
                valid_wall = strike < spot
        else:  # "C"
            wall_level = call_w
            wall_label = "Call Wall"
            # CC válida: strike ≤ call_wall y dentro de tolerancia inferior
            if call_w is not None:
                valid_wall = (strike <= call_w) and (strike >= call_w * (1 - wall_tol_pct))
            else:
                valid_wall = strike > spot

        if not valid_wall: continue

        # Distancia al muro
        dist_muro = abs(strike - wall_level) / wall_level * 100 if wall_level else np.nan

        # Filtros de prima y IV
        if row["iv"] < min_iv: continue
        if row["mid"] < min_prem: continue

        records.append({**row, "wall_level": wall_level, "wall_label": wall_label,
                        "dist_muro": dist_muro})

    if not records: return pd.DataFrame()
    valid = pd.DataFrame(records)

    valid["Estrategia"] = np.where(valid["right"]=="P", "Venta Put (CSP)", "Covered Call (CC)")
    valid = valid.sort_values("annual_yield", ascending=False).head(50)

    out = valid[[
        "Estrategia","strike","expiration","dte","right",
        "bid","ask","mid","delta","theta","iv_pct",
        "open_interest","annual_yield","spread_pct",
        "wall_level","wall_label","dist_muro",
    ]].rename(columns={
        "strike":"Strike","expiration":"Expiración","dte":"DTE","right":"Tipo",
        "bid":"Bid","ask":"Ask","mid":"Mid","delta":"Delta","theta":"Theta/día",
        "iv_pct":"IV (%)","open_interest":"OI",
        "annual_yield":"Yield Anual (%)","spread_pct":"Spread (%)",
        "wall_level":"Muro GEX ($)","wall_label":"Tipo Muro","dist_muro":"Dist. Muro (%)",
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
    out["Muro GEX ($)"]   = out["Muro GEX ($)"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/D")
    out["Dist. Muro (%)"] = out["Dist. Muro (%)"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/D")
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

def show_walls_summary(walls_per_exp, spot):
    """Tabla compacta de muros GEX por expiración en el encabezado del escáner."""
    if not walls_per_exp: return
    rows = []
    for exp_str, w in sorted(walls_per_exp.items()):
        cw = w.get("call_wall")
        pw = w.get("put_wall")
        rows.append({
            "Expiración": exp_str,
            "Call Wall ($)": f"${cw:.2f}" if cw else "N/D",
            "Put Wall ($)":  f"${pw:.2f}" if pw else "N/D",
            "Rango GEX": (
                f"${pw:.2f} → ${cw:.2f}" if (cw and pw)
                else ("Solo Call Wall" if cw else "Solo Put Wall" if pw else "Sin datos")
            ),
            "Spot en rango": (
                "✅" if (cw and pw and pw <= spot <= cw)
                else ("↑ Sobre Call Wall" if (cw and spot > cw)
                      else ("↓ Bajo Put Wall" if (pw and spot < pw) else "—"))
            ),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# =============================================================================
# BLOQUE 9 – APP PRINCIPAL
# =============================================================================

def main():
    st.markdown("""
    <div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:0.75rem;">
      <h1 style="font-family: var(--font-heading);font-size:2rem;font-weight:800;
                 color:#f1f5f9;margin:0;letter-spacing:-0.03em;">GEX WHEEL</h1>
      <span style="font-family: var(--font-data);font-size:0.9rem;
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
        wall_tol_pct   = st.slider("Tolerancia al Muro (%)", 1, 15, 5, 1,
                                    help="Banda alrededor del muro GEX para filtrar contratos. "
                                         "5% = acepta strikes dentro del 5% del Put/Call Wall.") / 100
        scan_max_delta = st.slider("Delta Abs. Máxima", 0.05, 0.50, 0.35, 0.01)
        scan_min_iv    = st.slider("IV Mínima (%)", 10, 200, 90, 5) / 100
        scan_min_oi    = st.number_input("OI Mínimo", min_value=0, value=500, step=10)
        scan_min_prem  = st.number_input("Prima Mínima ($)", min_value=0.01, value=0.90, step=0.05)

        st.markdown("---")
        # FIX: botón separado del trigger por cambio de ticker
        load_btn = st.button("🔄 Cargar Datos", use_container_width=True)

    # ── Estado de sesión ─────────────────────────────────────────────────────
    defaults = dict(chain=pd.DataFrame(), hist=pd.DataFrame(), vp=pd.DataFrame(),
                    pivot=pd.DataFrame(),
                    spot=None, chg=None, pct=None, div_yield=0.0,
                    ticker="", loaded=False, demo_mode=False,
                    _loaded_min_dte=None, _loaded_max_dte=None)
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    # FIX: detectar cambio real de parámetros de carga (ticker, DTE)
    # El cambio de slider DTE sin pulsar el botón NO recarga — requiere acción explícita.
    needs_load = (
        load_btn or
        (ticker != st.session_state.ticker) or
        not st.session_state.loaded
    )

    # ── Carga ─────────────────────────────────────────────────────────────────
    if needs_load:
        demo_mode = False
        with st.spinner(f"Descargando **{ticker}**…"):
            spot      = fetch_spot_price(ticker) if YF_AVAILABLE else None
            _, chg, pct = fetch_day_change(ticker) if YF_AVAILABLE else (None, None, None)
            div_yield = fetch_dividend_yield(ticker) if YF_AVAILABLE else 0.0

            if spot is None:
                demo_mode = True
                spot = {"IREN":12.5,"KEEL":4.8,"NBIS":22.3}.get(ticker, 50.0)
                chg, pct, div_yield = None, None, 0.0
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
                    with st.spinner("Calculando Griegas (con dividendos)…"):
                        chain = enrich_greeks(chain, spot, r=0.05, q=div_yield)

        vp    = compute_volume_profile(hist, n_bins=150) if not hist.empty else pd.DataFrame()
        pivot = calculate_gex_heatmap(chain, spot) if not chain.empty else pd.DataFrame()

        st.session_state.update(
            chain=chain, hist=hist, vp=vp, pivot=pivot,
            spot=spot, chg=chg, pct=pct, div_yield=div_yield,
            ticker=ticker, loaded=True, demo_mode=demo_mode,
            _loaded_min_dte=min_dte, _loaded_max_dte=max_dte,
        )

    chain     = st.session_state.chain
    hist      = st.session_state.hist
    vp        = st.session_state.vp
    pivot     = st.session_state.pivot
    spot      = st.session_state.spot
    chg       = st.session_state.chg
    pct       = st.session_state.pct
    div_yield = st.session_state.div_yield
    demo_mode = st.session_state.demo_mode

    show_status_banner(YF_AVAILABLE, demo_mode)
    if not st.session_state.loaded or spot is None:
        st.info("Introduce un ticker y pulsa Cargar Datos.")
        return

    # Avisar si los sliders DTE difieren de los datos cargados
    if (st.session_state._loaded_min_dte != min_dte or
            st.session_state._loaded_max_dte != max_dte):
        st.markdown(
            '<div class="warn-box">⚠️ Has cambiado el rango DTE. '
            'Pulsa <b>🔄 Cargar Datos</b> para actualizar la cadena de opciones.</div>',
            unsafe_allow_html=True,
        )

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

    # Dividendo en cabecera si es relevante
    if div_yield > 0:
        st.markdown(
            f'<div class="info-box" style="margin:0.3rem 0 0.5rem 0; padding:0.4rem 1rem;">'
            f'📌 <b>Dividend Yield:</b> {div_yield*100:.2f}% — '
            f'incluido en el cálculo de griegas (modelo Merton).</div>',
            unsafe_allow_html=True,
        )

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
            pivot_f = calculate_gex_heatmap(chain_f, spot)
            if not pivot_f.empty:
                st.plotly_chart(plot_gex_heatmap(pivot_f.iloc[:, :n_exp_heatmap], spot),
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
            <strong>🎯 Cómo usa el escáner los muros GEX:</strong><br>
            • <strong>CSP (Venta Put):</strong> Busca strikes cercanos <em>por encima</em> del <strong>Put Wall</strong> de ese vencimiento.
              El Put Wall es donde los MM compran para defender el nivel — vendes la put justo ahí, con soporte institucional real.<br>
            • <strong>Covered Call (CC):</strong> Busca strikes cercanos <em>por debajo</em> del <strong>Call Wall</strong>.
              El Call Wall es el techo donde los MM venden — vendes la call donde la resistencia es más firme.<br>
            • <strong>Tolerancia al Muro (%):</strong> Ajusta la banda de búsqueda alrededor del muro en el sidebar.<br>
            • <strong>Dist. Muro (%):</strong> Cuanto más cerca de 0%, más preciso el alineamiento con el muro.
        </div>
        """, unsafe_allow_html=True)

        # Tabla resumen de muros por expiración
        walls_per_exp = get_walls_per_expiration(pivot) if not pivot.empty else {}
        if walls_per_exp:
            st.markdown('<div class="section-title">📍 Muros GEX por Expiración</div>',
                        unsafe_allow_html=True)
            show_walls_summary(walls_per_exp, spot)

        res = scan_wheel_opportunities(
            chain=st.session_state.chain, spot=spot, pivot=pivot, ticker=ticker,
            min_iv=scan_min_iv, min_oi=scan_min_oi, min_prem=scan_min_prem,
            min_dte=min_dte, max_dte=max_dte, max_delta=scan_max_delta,
            wall_tol_pct=wall_tol_pct,
        )

        if not res.empty:
            csp_res = res[res["Estrategia"]=="Venta Put (CSP)"]
            cc_res  = res[res["Estrategia"]=="Covered Call (CC)"]

            n_rows   = max(len(csp_res), len(cc_res), 1)
            row_h    = 35
            header_h = 38
            tbl_h    = min(header_h + n_rows * row_h, 600)

            # Columnas a mostrar — incluye las nuevas de muro
            show_cols = ["Strike","Expiración","DTE","Tipo",
                         "Bid","Ask","Mid","Delta","Theta/día","IV (%)",
                         "OI","Yield Anual (%)","Spread (%)",
                         "Muro GEX ($)","Tipo Muro","Dist. Muro (%)"]

            st.markdown(f'<div class="section-title">🔻 Ventas de Put — CSP ({len(csp_res)} contratos)</div>',
                        unsafe_allow_html=True)
            if not csp_res.empty:
                st.dataframe(csp_res[show_cols],
                             use_container_width=True, hide_index=True, height=tbl_h)
            else:
                st.info("Sin puts cerca de Put Walls con los criterios actuales. "
                        "Aumenta la Tolerancia al Muro o reduce Prima/OI mínimos.")

            st.markdown(f'<div class="section-title">🔺 Covered Calls — CC ({len(cc_res)} contratos)</div>',
                        unsafe_allow_html=True)
            if not cc_res.empty:
                st.dataframe(cc_res[show_cols],
                             use_container_width=True, hide_index=True, height=tbl_h)
            else:
                st.info("Sin calls cerca de Call Walls con los criterios actuales. "
                        "Aumenta la Tolerancia al Muro o reduce Prima/OI mínimos.")

            try:
                best_yield = res["Yield Anual (%)"].str.replace("%","",regex=False).astype(float).max()
            except Exception:
                best_yield = float("nan")

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            with m1: metric_card("Oportunidades CSP", str(len(csp_res)), positive=True)
            with m2: metric_card("Oportunidades CC",  str(len(cc_res)),  positive=True)
            with m3: metric_card("Mejor Yield Anual",
                                 f"{best_yield:.1f}%" if not np.isnan(best_yield) else "N/D",
                                 positive=True)
            with m4: metric_card("Tolerancia Muro",   f"±{wall_tol_pct*100:.0f}%", positive=True)
        else:
            st.info("Ningún contrato cerca de muros GEX con los criterios actuales. "
                    "Aumenta la Tolerancia al Muro (sidebar) o reduce Prima/OI mínimos.")

        st.markdown("""
        <div class="warn-box">
          ⚠️ <strong>Aviso de riesgo:</strong> Herramienta puramente informativa.
          La venta de opciones implica riesgo de pérdida significativa.
          Opera siempre dentro de tu perfil de riesgo.
        </div>""", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center;color:#334155;font-size:0.7rem;font-family: var(--font-data);">'
        f'GEX Wheel · CarlosCano93 · Yahoo Finance · Streamlit · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}'
        f'{"  ·  MODO DEMO" if demo_mode else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()