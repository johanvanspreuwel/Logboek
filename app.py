"""
=============================================================
  Trading Logboek & Portfolio Tracker — Streamlit versie
  Mobiel-vriendelijk | Dark theme | yfinance | Multi-valuta
=============================================================
"""

import math
import datetime
import os

import pandas as pd
import yfinance as yf
import streamlit as st

# ─────────────────────────────────────────────
#  PAGINA-CONFIGURATIE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📈 Trading Logboek",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Zorg dat unsafe_allow_html werkt door een test te doen
# (Streamlit Cloud ondersteunt dit standaard, maar sommige versies niet)
_HTML_TEST = True

# ─────────────────────────────────────────────
#  CONSTANTEN
# ─────────────────────────────────────────────
KOLOMMEN_CSV  = ["Ticker", "Aantal", "Instap_Prijs", "Stop_Loss", "Take_Profit", "Datum_Instap"]
CSV_PAD       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mijn_posities.csv")
DOEL_BEDRAG   = 200_000.0
WEEKRENDEMENT = 0.02534

# Valuta → symbool mapping
VALUTA_SYMBOOL = {
    "EUR": "€", "USD": "$", "GBP": "£", "JPY": "¥",
    "CHF": "Fr", "CAD": "C$", "AUD": "A$", "HKD": "HK$",
    "SEK": "kr", "NOK": "kr", "DKK": "kr", "SGD": "S$",
    "CNY": "¥", "KRW": "₩", "INR": "₹", "BRL": "R$",
    "MXN": "MX$", "ZAR": "R", "TRY": "₺", "PLN": "zł",
}

# ─────────────────────────────────────────────
#  DARK THEME CSS — mobiel-first
# ─────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Consolas', 'Courier New', monospace !important;
}
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
#MainMenu, footer, header { visibility: hidden; }

.stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 16px 12px 16px;
    margin-bottom: 8px;
    min-height: 72px;
}
.stat-label {
    font-size: 10px; color: #7d8590;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px;
}
.stat-value { font-size: 20px; font-weight: bold; line-height: 1.1; }
.stat-sub   { font-size: 10px; color: #7d8590; margin-top: 3px; }

.prog-outer {
    background: #21262d; border-radius: 4px;
    height: 8px; width: 100%;
    margin: 4px 0 2px 0; overflow: hidden;
}
.prog-inner { height: 8px; border-radius: 4px; transition: width 0.4s ease; }
.prog-labels {
    display: flex; justify-content: space-between;
    font-size: 10px; color: #7d8590; margin-bottom: 12px;
}

.pos-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
}
.pos-ticker { font-size: 18px; font-weight: bold; color: #58a6ff; display: inline-block; }
.pos-markt  { font-size: 11px; margin-left: 8px; vertical-align: middle; }
.pos-row    { display: flex; justify-content: space-between; margin-top: 6px; font-size: 13px; }
.pos-key    { color: #7d8590; }
.pos-val    { font-weight: bold; }
.pos-valuta { font-size: 10px; color: #7d8590; margin-left: 4px; vertical-align: middle; }
.pos-status {
    margin-top: 8px; padding: 4px 10px;
    border-radius: 6px; font-size: 12px; font-weight: bold;
    background: #21262d; display: inline-block;
}
.clr-green  { color: #3fb950; }
.clr-red    { color: #f85149; }
.clr-orange { color: #d29922; }
.clr-yellow { color: #e3b341; }
.clr-blue   { color: #58a6ff; }
.clr-purple { color: #bc8cff; }
.clr-muted  { color: #7d8590; }

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background-color: #21262d !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 6px !important;
    font-family: 'Consolas', monospace !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 2px rgba(88,166,255,0.15) !important;
}
label, [data-testid="stWidgetLabel"] p {
    color: #7d8590 !important; font-size: 11px !important;
    font-family: 'Consolas', monospace !important;
    letter-spacing: 0.5px !important; text-transform: uppercase !important;
}
[data-testid="stButton"] button {
    background-color: #238636 !important; color: #ffffff !important;
    border: none !important; border-radius: 6px !important;
    font-family: 'Consolas', monospace !important;
    font-weight: bold !important; width: 100% !important; padding: 10px !important;
}
[data-testid="stButton"] button:hover { background-color: #2ea043 !important; }
hr { border-color: #30363d !important; }
[data-testid="stTabs"] [role="tablist"] {
    background: #161b22; border-radius: 8px; padding: 4px; gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent !important; color: #7d8590 !important;
    border-radius: 6px !important; font-family: 'Consolas', monospace !important;
    font-size: 13px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #21262d !important; color: #e6edf3 !important;
}
[data-testid="stDataFrame"] th:first-child,
[data-testid="stDataFrame"] td:first-child { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def laad_csv() -> pd.DataFrame:
    """Leest mijn_posities.csv uit de app-map. Maakt lege DataFrame als bestand ontbreekt."""
    if os.path.exists(CSV_PAD):
        try:
            df = pd.read_csv(CSV_PAD, dtype={"Ticker": str})
            for col in ["Aantal", "Instap_Prijs", "Stop_Loss", "Take_Profit"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            for k in KOLOMMEN_CSV:
                if k not in df.columns:
                    df[k] = ""
            return df[KOLOMMEN_CSV].copy()
        except Exception:
            pass
    return pd.DataFrame(columns=KOLOMMEN_CSV)

def sla_csv_op(df: pd.DataFrame):
    """Schrijft DataFrame direct naar mijn_posities.csv naast app.py."""
    try:
        df.to_csv(CSV_PAD, index=False)
    except Exception:
        pass

def init_state():
    if "df" not in st.session_state:
        st.session_state.df = laad_csv()   # ← persistent: leest bestaande data
    if "koersen" not in st.session_state:
        st.session_state.koersen = {}

init_state()


# ─────────────────────────────────────────────
#  DATA HULPFUNCTIES
# ─────────────────────────────────────────────
def lees_df_uit_upload(bestand) -> pd.DataFrame:
    df = pd.read_csv(bestand, dtype={"Ticker": str})
    for col in ["Aantal", "Instap_Prijs", "Stop_Loss", "Take_Profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for k in KOLOMMEN_CSV:
        if k not in df.columns:
            df[k] = ""
    return df[KOLOMMEN_CSV].copy()

def df_naar_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def voeg_toe(ticker, aantal, instap, sl, tp, datum):
    rij = {
        "Ticker": ticker.upper().strip(), "Aantal": float(aantal),
        "Instap_Prijs": float(instap), "Stop_Loss": float(sl),
        "Take_Profit": float(tp), "Datum_Instap": str(datum),
    }
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([rij])], ignore_index=True)
    sla_csv_op(st.session_state.df)   # ← direct persisteren

def verwijder_rij(idx: int):
    st.session_state.df = st.session_state.df.drop(index=idx).reset_index(drop=True)
    sla_csv_op(st.session_state.df)   # ← direct persisteren


# ─────────────────────────────────────────────
#  VALUTA HELPERS
# ─────────────────────────────────────────────
def symbool(valuta: str) -> str:
    """Geeft valutasymbool terug, bijv. 'USD' → '$'."""
    return VALUTA_SYMBOOL.get(str(valuta).upper(), str(valuta).upper() + " ")

def fmt_koers(prijs: float, valuta: str, decimalen: int = 4) -> str:
    """Formatteert koers met juist valutasymbool."""
    sym = symbool(valuta)
    return f"{sym}{prijs:,.{decimalen}f}"

def fmt_pnl(bedrag_eur: float) -> str:
    """Formatteert P&L altijd in euro's met teken."""
    teken = "+" if bedrag_eur >= 0 else ""
    return f"{teken}€ {bedrag_eur:,.2f}"


# ─────────────────────────────────────────────
#  WISSELKOERS SERVICE (gecached 1 uur)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def haal_wisselkoers_naar_eur(valuta: str) -> float:
    """Haalt wisselkoers op: hoeveel EUR is 1 eenheid van valuta?
       Bijv. USD → EUR: als EURUSD = 1.08, dan is 1 USD = 1/1.08 EUR."""
    valuta = valuta.upper()
    if valuta == "EUR":
        return 1.0
    try:
        # Probeer directe pair: USDEUR=X
        ticker = f"{valuta}EUR=X"
        obj = yf.Ticker(ticker)
        inf = obj.info or {}
        prijs = inf.get("regularMarketPrice") or inf.get("currentPrice")
        if prijs and float(prijs) > 0:
            return float(prijs)
        # Fallback: history
        hist = obj.history(period="5d", interval="1d")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
    except Exception:
        pass
    # Noodval: EURUSD omgekeerd
    try:
        obj2 = yf.Ticker(f"EUR{valuta}=X")
        inf2 = obj2.info or {}
        prijs2 = inf2.get("regularMarketPrice") or inf2.get("currentPrice")
        if prijs2 and float(prijs2) > 0:
            return 1.0 / float(prijs2)
    except Exception:
        pass
    return 1.0  # onbekend: geen conversie


# ─────────────────────────────────────────────
#  KOERS SERVICE — inclusief valuta
# ─────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def gecachte_koersen(tickers_tuple: tuple) -> dict:
    """Haalt koersen op en voegt valuta + wisselkoers naar EUR toe."""
    tickers = list(tickers_tuple)
    if not tickers:
        return {}
    unieke = list(set(t.upper().strip() for t in tickers if t))
    resultaat = {}

    for ticker in unieke:
        try:
            obj = yf.Ticker(ticker)
            prijs = slotkoers = None
            fase, label = "GESLOTEN", "🔒 Sluit"
            valuta = "EUR"  # standaard

            try:
                inf = obj.info or {}
                valuta = str(inf.get("currency", "EUR")).upper()
                markt_staat = str(inf.get("marketState", "")).upper()
                reg  = inf.get("regularMarketPrice") or inf.get("currentPrice")
                pre  = inf.get("preMarketPrice")
                post = inf.get("postMarketPrice")
                if reg:
                    slotkoers = float(reg)
                if markt_staat in ("REGULAR", "OPEN") and reg:
                    prijs, fase, label = float(reg), "OPEN", "🟢 Live"
                elif markt_staat in ("PRE", "PREPRE") and pre:
                    prijs, fase, label = float(pre), "PRE", "🌅 Pre-market"
                elif markt_staat in ("POST", "POSTPOST") and post:
                    prijs, fase, label = float(post), "POST", "🌙 After-hours"
                elif reg:
                    prijs, fase, label = float(reg), "GESLOTEN", "🔒 Sluit"
            except Exception:
                pass

            if prijs is None:
                hist = obj.history(period="1d", interval="1m", prepost=True)
                if hist.empty:
                    hist = obj.history(period="5d", interval="1d")
                if not hist.empty:
                    prijs = float(hist["Close"].dropna().iloc[-1])
                    slotkoers = prijs

            if prijs is not None:
                # Wisselkoers ophalen (gecached)
                koers_naar_eur = haal_wisselkoers_naar_eur(valuta)
                resultaat[ticker] = {
                    "prijs":          prijs,
                    "slotkoers":      slotkoers or prijs,
                    "fase":           fase,
                    "label":          label,
                    "valuta":         valuta,
                    "koers_naar_eur": koers_naar_eur,
                }
        except Exception:
            pass

    return resultaat


def bepaal_status(huidig, instap, sl, tp):
    if huidig <= sl:
        return "🚨 SL GETRIGGERD", "clr-red"
    if huidig >= tp:
        return "🎯 TARGET BEREIKT", "clr-green"
    if sl > 0 and ((huidig - sl) / sl) * 100 <= 2.0:
        return "⚠️ SL HEEL DICHTBIJ!", "clr-orange"
    if tp > 0 and ((tp - huidig) / tp) * 100 <= 2.0:
        return "🔥 BIJNA TARGET!", "clr-yellow"
    return "🟢 In vlucht", "clr-green"


# ─────────────────────────────────────────────
#  PORTFOLIO BEREKENINGEN (alles → EUR)
# ─────────────────────────────────────────────
def bereken_portfolio(df: pd.DataFrame, koersen: dict) -> dict:
    """Rekent alle posities om naar EUR voor totalen."""
    totaal_inv = totaal_waarde = 0.0
    for _, r in df.iterrows():
        try:
            instap = float(r["Instap_Prijs"])
            aantal = float(r["Aantal"])
            ticker = str(r["Ticker"]).upper().strip()
            ki = koersen.get(ticker)
            fx = ki["koers_naar_eur"] if ki else 1.0
            # Investering: instap is al in lokale valuta → omrekenen naar EUR
            totaal_inv   += instap * aantal * fx
            # Actuele waarde
            totaal_waarde += (ki["prijs"] * aantal * fx) if ki else (instap * aantal * fx)
        except Exception:
            pass
    pnl = totaal_waarde - totaal_inv
    doel_pct = min((totaal_waarde / DOEL_BEDRAG) * 100, 100) if DOEL_BEDRAG > 0 else 0
    try:
        weken = math.log(DOEL_BEDRAG / totaal_waarde) / math.log(1 + WEEKRENDEMENT) if totaal_waarde > 0 else 0
    except Exception:
        weken = 0
    return {
        "investering": totaal_inv,
        "waarde":      totaal_waarde,
        "pnl":         pnl,
        "doel_pct":    doel_pct,
        "weken":       weken,
    }


# ─────────────────────────────────────────────
#  HTML HELPERS
# ─────────────────────────────────────────────
def kleur_voor_pct(pct: float) -> str:
    if pct < 25:  return "#f85149"
    if pct < 50:  return "#d29922"
    if pct < 75:  return "#e3b341"
    return "#3fb950"

def stat_kaart(label: str, waarde: str, kleur: str, sub: str = "") -> str:
    sub_html = f'<div class="stat-sub">{sub}</div>' if sub else ""
    return f"""<div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value" style="color:{kleur}">{waarde}</div>
        {sub_html}
    </div>"""

def rendement_kleur(pct: float) -> str:
    return "#3fb950" if pct >= 0 else "#f85149"


# ─────────────────────────────────────────────
#  HOOFD APP
# ─────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;margin-top:-16px">
  <span style="font-size:26px;font-weight:bold;color:#58a6ff;font-family:Consolas">
    📈 Trading Logboek
  </span>
</div>
<div style="color:#7d8590;font-size:11px;font-family:Consolas;margin-bottom:16px">
  Portfolio Tracker · Multi-valuta · Sneeuwbal Doel
</div>
""", unsafe_allow_html=True)

tab_portfolio, tab_toevoegen, tab_data = st.tabs([
    "📊 Portfolio", "➕ Toevoegen", "💾 Data"
])


# ══════════════════════════════════════════════
#  TAB 1 — PORTFOLIO
# ══════════════════════════════════════════════
with tab_portfolio:

    df = st.session_state.df
    tickers = list(df["Ticker"].dropna().unique()) if not df.empty else []

    # ── Refresh knop + status ──
    col_refresh, col_status = st.columns([1, 3])
    with col_refresh:
        if st.button("♻️ Ververs koersen", key="refresh"):
            st.cache_data.clear()

    if tickers:
        with st.spinner("Koersen ophalen..."):
            koersen = gecachte_koersen(tuple(tickers))
        st.session_state.koersen = koersen
        nu = datetime.datetime.now().strftime("%H:%M:%S")
        fases = [v["label"] for v in koersen.values()]
        valuta_set = list(set(v["valuta"] for v in koersen.values()))
        with col_status:
            st.markdown(
                f'<div style="color:#7d8590;font-size:11px;padding-top:10px">'
                f'✅ {nu} · {" · ".join(fases)}'
                f'{"  |  valuta: " + ", ".join(valuta_set) if valuta_set else ""}</div>',
                unsafe_allow_html=True,
            )
    else:
        koersen = {}
        with col_status:
            st.markdown(
                '<div style="color:#7d8590;font-size:11px;padding-top:10px">'
                'Nog geen posities — voeg een ticker toe via ➕ Toevoegen</div>',
                unsafe_allow_html=True,
            )

    # ── Stats berekenen ──
    stats = bereken_portfolio(df, koersen)
    pnl_teken  = "+" if stats["pnl"] >= 0 else ""
    pnl_kleur  = "#3fb950" if stats["pnl"] >= 0 else "#f85149"
    waarde_kleur = "#3fb950" if stats["waarde"] >= stats["investering"] else "#f85149"
    prog_kleur = kleur_voor_pct(stats["doel_pct"])

    # ── Rij 1: 3 kaarten ──
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(stat_kaart("Posities", str(len(df)), "#58a6ff", "open posities"), unsafe_allow_html=True)
    with k2:
        st.markdown(stat_kaart("Investering", f"€ {stats['investering']:,.0f}", "#e6edf3", "in EUR"), unsafe_allow_html=True)
    with k3:
        st.markdown(stat_kaart("Actuele Waarde", f"€ {stats['waarde']:,.0f}", waarde_kleur, "in EUR"), unsafe_allow_html=True)

    # ── Rij 2: 3 kaarten ──
    k4, k5, k6 = st.columns(3)
    with k4:
        st.markdown(stat_kaart("Portfolio P&L", f"{pnl_teken}€ {stats['pnl']:,.2f}", pnl_kleur, "in EUR"), unsafe_allow_html=True)
    with k5:
        st.markdown(stat_kaart(
            "🎯 Doel Reis", f"{stats['doel_pct']:.1f}%", prog_kleur,
            f"nog € {max(0, DOEL_BEDRAG - stats['waarde']):,.0f} te gaan",
        ), unsafe_allow_html=True)
    with k6:
        jaren = stats["weken"] / 52
        st.markdown(stat_kaart(
            "⏱ Tempo Tot Doel",
            f"{stats['weken']:.0f} wkn" if stats["weken"] > 0 else "🏆 Bereikt!",
            "#bc8cff",
            f"≈ {jaren:.1f} jaar bij 2.534%/wk" if stats["weken"] > 0 else "",
        ), unsafe_allow_html=True)

    # ── Voortgangsbalk ──
    pct_w = min(stats["doel_pct"], 100)
    st.markdown(f"""
    <div class="prog-outer">
      <div class="prog-inner" style="width:{pct_w:.2f}%;background:{prog_kleur}"></div>
    </div>
    <div class="prog-labels">
      <span>€ 0</span>
      <span style="color:{prog_kleur};font-weight:bold">{pct_w:.1f}% van € {DOEL_BEDRAG:,.0f}</span>
      <span>€ {DOEL_BEDRAG:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Positie-kaarten ──
    st.markdown(
        '<div style="color:#7d8590;font-size:11px;letter-spacing:1px;'
        'text-transform:uppercase;margin-bottom:8px">Openstaande Posities</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.markdown(
            '<div style="color:#7d8590;text-align:center;padding:32px;font-family:Consolas">'
            'Geen posities. Ga naar ➕ Toevoegen.</div>',
            unsafe_allow_html=True,
        )
    else:
        for i, rij in df.iterrows():
            try:
                ticker = str(rij["Ticker"]).upper().strip()
                instap = float(rij["Instap_Prijs"])
                aantal = float(rij["Aantal"])
                sl     = float(rij["Stop_Loss"])
                tp     = float(rij["Take_Profit"])
                datum  = str(rij["Datum_Instap"])

                ki = koersen.get(ticker)

                if ki:
                    koers          = ki["prijs"]
                    slot           = ki["slotkoers"]
                    markt_lbl      = ki["label"]
                    fase           = ki["fase"]
                    valuta         = ki["valuta"]
                    fx             = ki["koers_naar_eur"]
                    sym            = symbool(valuta)

                    rendement      = ((koers - instap) / instap) * 100
                    rend_kleur     = rendement_kleur(rendement)
                    rend_str       = f"{'+' if rendement >= 0 else ''}{rendement:.2f}%"

                    status_txt, status_cls = bepaal_status(koers, instap, sl, tp)

                    # Koers in lokale valuta
                    koers_str = f"{sym}{koers:,.4f}"
                    if fase in ("PRE", "POST") and slot and slot != koers:
                        koers_str += f" <span class='clr-muted' style='font-size:10px'>(slot {sym}{slot:,.4f})</span>"

                    # Instap / SL / TP in lokale valuta
                    instap_str = f"{sym}{instap:,.4f}"
                    sl_str     = f"{sym}{sl:,.4f}"
                    tp_str     = f"{sym}{tp:,.4f}"

                    # P&L in lokale valuta én in EUR
                    pnl_lokaal = (koers - instap) * aantal
                    pnl_eur    = pnl_lokaal * fx
                    pnl_kleur_pos = rendement_kleur(pnl_eur)

                    if valuta == "EUR":
                        # Geen conversie nodig: toon alleen EUR
                        pnl_str = fmt_pnl(pnl_eur)
                        pnl_sub = ""
                    else:
                        # Toon lokaal + EUR
                        teken = "+" if pnl_lokaal >= 0 else ""
                        pnl_str = fmt_pnl(pnl_eur)
                        pnl_sub = f'<span class="clr-muted" style="font-size:10px">&nbsp;({teken}{sym}{pnl_lokaal:,.2f} {valuta})</span>'

                    # Valuta badge voor niet-EUR
                    valuta_badge = (
                        f'<span style="background:#21262d;color:#7d8590;font-size:9px;'
                        f'padding:1px 5px;border-radius:4px;margin-left:6px;'
                        f'vertical-align:middle">{valuta}</span>'
                        if valuta != "EUR" else ""
                    )
                    # FX info subtekst
                    fx_info = (
                        f'<div style="color:#7d8590;font-size:10px;margin-top:2px">'
                        f'1 {valuta} = € {fx:.4f}</div>'
                        if valuta != "EUR" else ""
                    )

                else:
                    # Geen koersdata
                    valuta = "—"; sym = ""
                    koers = rendement = None
                    markt_lbl  = "—"; rend_str = "—"; rend_kleur = "#7d8590"
                    status_txt, status_cls = "⏳ Laden...", "clr-muted"
                    koers_str  = "—"; instap_str = f"{instap:,.4f}"
                    sl_str     = f"{sl:,.4f}"; tp_str = f"{tp:,.4f}"
                    pnl_str    = "—"; pnl_sub = ""; pnl_kleur_pos = "#7d8590"
                    valuta_badge = ""; fx_info = ""

                # Bouw kaart op als losse rijen — betrouwbaarder dan één grote HTML blob
                header_html = (
                    f'<div style="background:#161b22;border:1px solid #30363d;'
                    f'border-radius:10px;padding:14px 16px 4px 16px;margin-bottom:2px">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
                    f'<span style="font-size:18px;font-weight:bold;color:#58a6ff">{ticker}</span>'
                    f'{"<span style=\"background:#21262d;color:#7d8590;font-size:9px;padding:1px 5px;border-radius:4px\">" + valuta + "</span>" if valuta not in ("EUR","—") else ""}'
                    f'<span style="font-size:11px;color:#7d8590">{markt_lbl}</span>'
                    f'</div>'
                    f'{"<div style=\"color:#7d8590;font-size:10px;margin-bottom:6px\">1 " + valuta + " = &#8364; " + f"{fx:.4f}" + "</div>" if valuta not in ("EUR","—") else ""}'
                    f'</div>'
                )
                rijen_html = ""
                for _k, _v, _kleur in [
                    ("Huidig",      koers_str,    "#e6edf3"),
                    ("Instap",      instap_str,   "#58a6ff"),
                    ("Rendement",   rend_str,     rend_kleur),
                    ("P&amp;L (EUR)", pnl_str + pnl_sub, pnl_kleur_pos),
                    ("Aantal",      f"{aantal:g}", "#e6edf3"),
                    ("Stop Loss",   sl_str,       "#f85149"),
                    ("Take Profit", tp_str,       "#3fb950"),
                    ("Datum",       datum,        "#7d8590"),
                ]:
                    rijen_html += (
                        f'<div style="display:flex;justify-content:space-between;'
                        f'margin-top:6px;font-size:13px;padding:0 16px">'
                        f'<span style="color:#7d8590">{_k}</span>'
                        f'<span style="font-weight:bold;color:{_kleur}">{_v}</span>'
                        f'</div>'
                    )
                voet_html = (
                    f'<div style="padding:10px 16px 14px 16px">'
                    f'<span style="background:#21262d;padding:4px 10px;border-radius:6px;'
                    f'font-size:12px;font-weight:bold;color:'
                    f'{"#f85149" if "SL" in status_txt else "#e3b341" if "BIJNA" in status_txt or "DICHTBIJ" in status_txt else "#3fb950"}">'
                    f'{status_txt}</span></div>'
                )
                wrapper = (
                    f'<div style="background:#161b22;border:1px solid #30363d;'
                    f'border-radius:10px;margin-bottom:10px;overflow:hidden">'
                    f'{header_html}{rijen_html}{voet_html}</div>'
                )
                st.markdown(wrapper, unsafe_allow_html=True)

                if st.button(f"🗑️ Verwijder {ticker}", key=f"del_{i}_{ticker}"):
                    verwijder_rij(i)
                    st.rerun()

            except Exception:
                pass


# ══════════════════════════════════════════════
#  TAB 2 — TOEVOEGEN
# ══════════════════════════════════════════════
with tab_toevoegen:
    st.markdown(
        '<div style="color:#7d8590;font-size:11px;letter-spacing:1px;'
        'text-transform:uppercase;margin-bottom:12px">Nieuwe Positie</div>',
        unsafe_allow_html=True,
    )

    with st.form("nieuw_formulier", clear_on_submit=True):
        ticker_in = st.text_input("Ticker", placeholder="bijv. AAPL of UNA.AS").upper().strip()
        col_a, col_b = st.columns(2)
        with col_a:
            aantal_in = st.number_input("Aantal", min_value=0.0, step=0.01, format="%.4f")
            instap_in = st.number_input("Instap Prijs (in lokale valuta)", min_value=0.0, step=0.01, format="%.4f")
        with col_b:
            sl_in = st.number_input("Stop Loss (in lokale valuta)", min_value=0.0, step=0.01, format="%.4f")
            tp_in = st.number_input("Take Profit (in lokale valuta)", min_value=0.0, step=0.01, format="%.4f")
        datum_in  = st.date_input("Aankoopdatum", value=datetime.date.today())
        ingediend = st.form_submit_button("➕ Voeg toe aan Logboek")

    if ingediend:
        fout = None
        if not ticker_in:               fout = "Voer een ticker in."
        elif aantal_in <= 0:            fout = "Aantal moet groter zijn dan 0."
        elif instap_in <= 0:            fout = "Instap Prijs moet groter zijn dan 0."
        elif sl_in <= 0 or sl_in >= instap_in: fout = "Stop Loss moet groter dan 0 en kleiner dan Instap Prijs zijn."
        elif tp_in <= instap_in:        fout = "Take Profit moet groter zijn dan Instap Prijs."

        if fout:
            st.error(fout)
        else:
            voeg_toe(ticker_in, aantal_in, instap_in, sl_in, tp_in, datum_in)
            st.success(f"✅ {ticker_in} toegevoegd! Koers en valuta worden automatisch opgehaald.")
            st.cache_data.clear()
            st.rerun()

    if not st.session_state.df.empty:
        st.markdown("---")
        st.markdown(
            '<div style="color:#7d8590;font-size:11px;letter-spacing:1px;'
            'text-transform:uppercase;margin-bottom:8px">Huidige Posities</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            st.session_state.df[["Ticker", "Aantal", "Instap_Prijs", "Stop_Loss", "Take_Profit", "Datum_Instap"]],
            use_container_width=True, hide_index=True,
        )


# ══════════════════════════════════════════════
#  TAB 3 — DATA
# ══════════════════════════════════════════════
with tab_data:
    st.markdown(
        '<div style="color:#7d8590;font-size:11px;letter-spacing:1px;'
        'text-transform:uppercase;margin-bottom:12px">Data Beheer</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 📤 Exporteer naar CSV")
    st.markdown('<div style="color:#7d8590;font-size:12px;margin-bottom:8px">Download je posities als CSV om lokaal te bewaren.</div>', unsafe_allow_html=True)
    if not st.session_state.df.empty:
        st.download_button(
            label="⬇️ Download mijn_posities.csv",
            data=df_naar_csv_bytes(st.session_state.df),
            file_name="mijn_posities.csv", mime="text/csv",
        )
    else:
        st.markdown('<div style="color:#7d8590;font-size:12px">Geen posities om te exporteren.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📥 Importeer CSV")
    st.markdown('<div style="color:#7d8590;font-size:12px;margin-bottom:8px">Upload een eerder gedownloade <code>mijn_posities.csv</code>.</div>', unsafe_allow_html=True)
    geupload = st.file_uploader("Kies CSV bestand", type=["csv"], label_visibility="collapsed")
    if geupload is not None:
        try:
            nieuw_df = lees_df_uit_upload(geupload)
            st.markdown(f'<div style="color:#3fb950;font-size:12px">✅ {len(nieuw_df)} posities gevonden.</div>', unsafe_allow_html=True)
            st.dataframe(nieuw_df, use_container_width=True, hide_index=True)
            if st.button("📥 Laad deze posities in"):
                st.session_state.df = nieuw_df
                sla_csv_op(nieuw_df)          # ← ook persisteren na import
                st.cache_data.clear()
                st.success("Posities geladen!")
                st.rerun()
        except Exception as e:
            st.error(f"Fout bij inlezen: {e}")

    st.markdown("---")
    st.markdown("#### 🗑️ Wis alle posities")
    st.markdown('<div style="color:#7d8590;font-size:12px;margin-bottom:8px">Download eerst een backup!</div>', unsafe_allow_html=True)
    if st.button("🗑️ Wis alle posities", key="wis_alles"):
        st.session_state.df = pd.DataFrame(columns=KOLOMMEN_CSV)
        st.session_state.koersen = {}
        sla_csv_op(st.session_state.df)   # ← lege CSV opslaan
        st.cache_data.clear()
        st.rerun()
