"""
=============================================================
  Trading Logboek & Portfolio Tracker — Streamlit versie
  Mobiel-vriendelijk | Dark theme | yfinance | GitHub ready
=============================================================
"""

import math
import datetime
import io

import pandas as pd
import yfinance as yf
import streamlit as st

# ─────────────────────────────────────────────
#  PAGINA-CONFIGURATIE (moet als allereerste)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📈 Trading Logboek",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CONSTANTEN
# ─────────────────────────────────────────────
KOLOMMEN_CSV   = ["Ticker", "Aantal", "Instap_Prijs", "Stop_Loss", "Take_Profit", "Datum_Instap"]
DOEL_BEDRAG    = 200_000.0
WEEKRENDEMENT  = 0.02534
CSV_KEY        = "posities_csv"          # Streamlit session-state sleutel

# ─────────────────────────────────────────────
#  DARK THEME CSS — mobiel-first
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Basis donker thema ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Consolas', 'Courier New', monospace !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}

/* Verberg Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* ── Stat-kaarten ── */
.stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 16px 12px 16px;
    margin-bottom: 8px;
    min-height: 72px;
}
.stat-label {
    font-size: 10px;
    color: #7d8590;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.stat-value {
    font-size: 20px;
    font-weight: bold;
    line-height: 1.1;
}
.stat-sub {
    font-size: 10px;
    color: #7d8590;
    margin-top: 3px;
}

/* ── Voortgangsbalk ── */
.prog-outer {
    background: #21262d;
    border-radius: 4px;
    height: 8px;
    width: 100%;
    margin: 4px 0 2px 0;
    overflow: hidden;
}
.prog-inner {
    height: 8px;
    border-radius: 4px;
    transition: width 0.4s ease;
}
.prog-labels {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #7d8590;
    margin-bottom: 12px;
}

/* ── Positie-kaarten (mobiel) ── */
.pos-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.pos-ticker {
    font-size: 18px;
    font-weight: bold;
    color: #58a6ff;
    display: inline-block;
}
.pos-markt {
    font-size: 11px;
    margin-left: 8px;
    vertical-align: middle;
}
.pos-row {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 13px;
}
.pos-key { color: #7d8590; }
.pos-val { font-weight: bold; }
.pos-status {
    margin-top: 8px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    background: #21262d;
    display: inline-block;
}
.clr-green  { color: #3fb950; }
.clr-red    { color: #f85149; }
.clr-orange { color: #d29922; }
.clr-yellow { color: #e3b341; }
.clr-blue   { color: #58a6ff; }
.clr-purple { color: #bc8cff; }
.clr-muted  { color: #7d8590; }

/* ── Formulier styling ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-family: 'Consolas', monospace !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 2px rgba(88,166,255,0.15) !important;
}

/* Label kleuren */
label, [data-testid="stWidgetLabel"] p {
    color: #7d8590 !important;
    font-size: 11px !important;
    font-family: 'Consolas', monospace !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* Knoppen */
[data-testid="stButton"] button {
    background-color: #238636 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Consolas', monospace !important;
    font-weight: bold !important;
    width: 100% !important;
    padding: 10px !important;
}
[data-testid="stButton"] button:hover {
    background-color: #2ea043 !important;
}

/* Divider */
hr { border-color: #30363d !important; }

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    background: #161b22;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent !important;
    color: #7d8590 !important;
    border-radius: 6px !important;
    font-family: 'Consolas', monospace !important;
    font-size: 13px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #21262d !important;
    color: #e6edf3 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] > div > div {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
}

/* Verberg index in dataframe */
[data-testid="stDataFrame"] th:first-child,
[data-testid="stDataFrame"] td:first-child { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE INITIALISATIE
# ─────────────────────────────────────────────
def init_state():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=KOLOMMEN_CSV)
    if "koersen" not in st.session_state:
        st.session_state.koersen = {}
    if "laatste_update" not in st.session_state:
        st.session_state.laatste_update = None
    if "update_status" not in st.session_state:
        st.session_state.update_status = ""

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
        "Ticker":       ticker.upper().strip(),
        "Aantal":       float(aantal),
        "Instap_Prijs": float(instap),
        "Stop_Loss":    float(sl),
        "Take_Profit":  float(tp),
        "Datum_Instap": str(datum),
    }
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([rij])], ignore_index=True
    )


def verwijder_rij(idx: int):
    st.session_state.df = st.session_state.df.drop(index=idx).reset_index(drop=True)


# ─────────────────────────────────────────────
#  KOERS SERVICE
# ─────────────────────────────────────────────
def haal_koersen(tickers: list) -> dict:
    if not tickers:
        return {}
    unieke = list(set(t.upper().strip() for t in tickers if t))
    resultaat = {}
    for ticker in unieke:
        try:
            obj = yf.Ticker(ticker)
            prijs = slotkoers = None
            fase, label = "GESLOTEN", "🔒 Sluit"
            try:
                inf = obj.info or {}
                markt_staat = str(inf.get("marketState", "")).upper()
                reg  = inf.get("regularMarketPrice") or inf.get("currentPrice")
                pre  = inf.get("preMarketPrice")
                post = inf.get("postMarketPrice")
                if reg:
                    slotkoers = float(reg)
                if markt_staat in ("REGULAR", "OPEN") and reg:
                    prijs, fase, label = float(reg), "OPEN", "🟢 Live"
                elif markt_staat in ("PRE", "PREPRE") and pre:
                    prijs, fase, label = float(pre), "PRE", f"🌅 Pre ({float(pre):,.2f})"
                elif markt_staat in ("POST", "POSTPOST") and post:
                    prijs, fase, label = float(post), "POST", f"🌙 After ({float(post):,.2f})"
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
                resultaat[ticker] = {
                    "prijs":     prijs,
                    "slotkoers": slotkoers or prijs,
                    "fase":      fase,
                    "label":     label,
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
#  KOERSEN OPHALEN (gecached per 60s)
# ─────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def gecachte_koersen(tickers_tuple: tuple) -> dict:
    return haal_koersen(list(tickers_tuple))


# ─────────────────────────────────────────────
#  PORTFOLIO BEREKENINGEN
# ─────────────────────────────────────────────
def bereken_portfolio(df: pd.DataFrame, koersen: dict) -> dict:
    totaal_inv = totaal_waarde = 0.0
    for _, r in df.iterrows():
        try:
            instap = float(r["Instap_Prijs"])
            aantal = float(r["Aantal"])
            ticker = str(r["Ticker"]).upper().strip()
            inv    = instap * aantal
            totaal_inv += inv
            ki = koersen.get(ticker)
            totaal_waarde += (ki["prijs"] * aantal) if ki else inv
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
    if pct < 25:   return "#f85149"
    if pct < 50:   return "#d29922"
    if pct < 75:   return "#e3b341"
    return "#3fb950"

def stat_kaart(label: str, waarde: str, kleur: str, sub: str = "") -> str:
    sub_html = f'<div class="stat-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value" style="color:{kleur}">{waarde}</div>
        {sub_html}
    </div>"""

def rendement_kleur(pct: float) -> str:
    return "#3fb950" if pct >= 0 else "#f85149"


# ─────────────────────────────────────────────
#  HOOFD APP
# ─────────────────────────────────────────────

# ── Titel ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;margin-top:-16px">
  <span style="font-size:26px;font-weight:bold;color:#58a6ff;font-family:Consolas">
    📈 Trading Logboek
  </span>
</div>
<div style="color:#7d8590;font-size:11px;font-family:Consolas;margin-bottom:16px">
  Portfolio Tracker · yfinance · Sneeuwbal Doel
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────
tab_portfolio, tab_toevoegen, tab_data = st.tabs([
    "📊 Portfolio", "➕ Toevoegen", "💾 Data"
])


# ══════════════════════════════════════════════
#  TAB 1 — PORTFOLIO
# ══════════════════════════════════════════════
with tab_portfolio:

    df = st.session_state.df
    tickers = list(df["Ticker"].dropna().unique()) if not df.empty else []

    # ── Koersen ophalen ──
    col_refresh, col_status = st.columns([1, 3])
    with col_refresh:
        if st.button("♻️ Ververs koersen", key="refresh"):
            st.cache_data.clear()

    if tickers:
        with st.spinner("Koersen ophalen..."):
            koersen = gecachte_koersen(tuple(tickers))
        st.session_state.koersen = koersen
        nu = datetime.datetime.now().strftime("%H:%M:%S")
        with col_status:
            fases = [v["label"] for v in koersen.values()]
            st.markdown(
                f'<div style="color:#7d8590;font-size:11px;padding-top:10px">'
                f'✅ Bijgewerkt: {nu} &nbsp;|&nbsp; {" · ".join(fases)}</div>',
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

    # ── Portfolio statistieken ──
    stats = bereken_portfolio(df, koersen)
    pnl_teken = "+" if stats["pnl"] >= 0 else ""
    pnl_kleur = "#3fb950" if stats["pnl"] >= 0 else "#f85149"
    waarde_kleur = "#3fb950" if stats["waarde"] >= stats["investering"] else "#f85149"
    prog_kleur = kleur_voor_pct(stats["doel_pct"])

    # Rij 1: 3 kolommen
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(stat_kaart("Posities", str(len(df)), "#58a6ff"), unsafe_allow_html=True)
    with k2:
        st.markdown(stat_kaart("Investering", f"€ {stats['investering']:,.0f}", "#e6edf3"), unsafe_allow_html=True)
    with k3:
        st.markdown(stat_kaart("Actuele Waarde", f"€ {stats['waarde']:,.0f}", waarde_kleur), unsafe_allow_html=True)

    # Rij 2: 3 kolommen
    k4, k5, k6 = st.columns(3)
    with k4:
        st.markdown(stat_kaart(
            "Portfolio P&L",
            f"{pnl_teken}€ {stats['pnl']:,.2f}",
            pnl_kleur,
        ), unsafe_allow_html=True)
    with k5:
        st.markdown(stat_kaart(
            "🎯 Doel Reis",
            f"{stats['doel_pct']:.1f}%",
            prog_kleur,
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

    # ── Positie kaarten ──
    st.markdown('<div style="color:#7d8590;font-size:11px;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">Openstaande Posities</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div style="color:#7d8590;text-align:center;padding:32px;font-family:Consolas">Geen posities. Ga naar ➕ Toevoegen.</div>', unsafe_allow_html=True)
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
                    koers     = ki["prijs"]
                    slot      = ki["slotkoers"]
                    markt_lbl = ki["label"]
                    fase      = ki["fase"]
                    rendement = ((koers - instap) / instap) * 100
                    rend_kleur = rendement_kleur(rendement)
                    rend_str  = f"{'+' if rendement >= 0 else ''}{rendement:.2f}%"
                    status_txt, status_cls = bepaal_status(koers, instap, sl, tp)
                    koers_str = f"{koers:,.4f}"
                    if fase in ("PRE", "POST") and slot and slot != koers:
                        koers_str += f" <span class='clr-muted' style='font-size:10px'>(slot {slot:,.4f})</span>"
                else:
                    koers = rendement = None
                    markt_lbl = "—"
                    rend_str  = "—"
                    rend_kleur = "#7d8590"
                    status_txt, status_cls = "⏳ Laden...", "clr-muted"
                    koers_str = "—"

                pnl_pos = ((koers - instap) * aantal) if koers else None
                pnl_str = (f"{'+' if pnl_pos >= 0 else ''}€ {pnl_pos:,.2f}") if pnl_pos is not None else "—"
                pnl_kleur_pos = rendement_kleur(pnl_pos) if pnl_pos is not None else "#7d8590"

                st.markdown(f"""
                <div class="pos-card">
                  <div>
                    <span class="pos-ticker">{ticker}</span>
                    <span class="pos-markt clr-muted">{markt_lbl}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Huidig</span>
                    <span class="pos-val">{koers_str}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Instap</span>
                    <span class="pos-val clr-blue">{instap:,.4f}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Rendement</span>
                    <span class="pos-val" style="color:{rend_kleur}">{rend_str}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">P&L</span>
                    <span class="pos-val" style="color:{pnl_kleur_pos}">{pnl_str}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Aantal</span>
                    <span class="pos-val">{aantal:g}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Stop Loss</span>
                    <span class="pos-val clr-red">{sl:,.4f}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Take Profit</span>
                    <span class="pos-val clr-green">{tp:,.4f}</span>
                  </div>
                  <div class="pos-row">
                    <span class="pos-key">Datum</span>
                    <span class="pos-val clr-muted">{datum}</span>
                  </div>
                  <div style="margin-top:8px">
                    <span class="pos-status {status_cls}">{status_txt}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Verwijder knop per positie
                if st.button(f"🗑️ Verwijder {ticker}", key=f"del_{i}_{ticker}"):
                    verwijder_rij(i)
                    st.rerun()

            except Exception:
                pass


# ══════════════════════════════════════════════
#  TAB 2 — TOEVOEGEN
# ══════════════════════════════════════════════
with tab_toevoegen:
    st.markdown('<div style="color:#7d8590;font-size:11px;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px">Nieuwe Positie</div>', unsafe_allow_html=True)

    with st.form("nieuw_formulier", clear_on_submit=True):
        ticker_in = st.text_input("Ticker", placeholder="bijv. AAPL of UNA.AS").upper().strip()
        col_a, col_b = st.columns(2)
        with col_a:
            aantal_in = st.number_input("Aantal", min_value=0.0, step=0.01, format="%.4f")
            instap_in = st.number_input("Instap Prijs", min_value=0.0, step=0.01, format="%.4f")
        with col_b:
            sl_in = st.number_input("Stop Loss", min_value=0.0, step=0.01, format="%.4f")
            tp_in = st.number_input("Take Profit", min_value=0.0, step=0.01, format="%.4f")

        datum_in = st.date_input("Aankoopdatum", value=datetime.date.today())
        ingediend = st.form_submit_button("➕ Voeg toe aan Logboek")

    if ingediend:
        fout = None
        if not ticker_in:
            fout = "Voer een ticker in."
        elif aantal_in <= 0:
            fout = "Aantal moet groter zijn dan 0."
        elif instap_in <= 0:
            fout = "Instap Prijs moet groter zijn dan 0."
        elif sl_in <= 0 or sl_in >= instap_in:
            fout = "Stop Loss moet groter dan 0 en kleiner dan Instap Prijs zijn."
        elif tp_in <= instap_in:
            fout = "Take Profit moet groter zijn dan Instap Prijs."

        if fout:
            st.error(fout)
        else:
            voeg_toe(ticker_in, aantal_in, instap_in, sl_in, tp_in, datum_in)
            st.success(f"✅ {ticker_in} toegevoegd!")
            st.cache_data.clear()
            st.rerun()

    # Toon huidige posities als kleine tabel
    if not st.session_state.df.empty:
        st.markdown("---")
        st.markdown('<div style="color:#7d8590;font-size:11px;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">Huidige Posities</div>', unsafe_allow_html=True)
        st.dataframe(
            st.session_state.df[["Ticker", "Aantal", "Instap_Prijs", "Stop_Loss", "Take_Profit", "Datum_Instap"]],
            use_container_width=True,
            hide_index=True,
        )


# ══════════════════════════════════════════════
#  TAB 3 — DATA (import/export)
# ══════════════════════════════════════════════
with tab_data:
    st.markdown('<div style="color:#7d8590;font-size:11px;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px">Data Beheer</div>', unsafe_allow_html=True)

    # ── Export ──
    st.markdown("#### 📤 Exporteer naar CSV")
    st.markdown('<div style="color:#7d8590;font-size:12px;margin-bottom:8px">Download je posities als CSV-bestand om lokaal te bewaren of te importeren op een ander apparaat.</div>', unsafe_allow_html=True)

    if not st.session_state.df.empty:
        csv_bytes = df_naar_csv_bytes(st.session_state.df)
        st.download_button(
            label="⬇️ Download mijn_posities.csv",
            data=csv_bytes,
            file_name="mijn_posities.csv",
            mime="text/csv",
        )
    else:
        st.markdown('<div style="color:#7d8590;font-size:12px">Geen posities om te exporteren.</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Import ──
    st.markdown("#### 📥 Importeer CSV")
    st.markdown('<div style="color:#7d8590;font-size:12px;margin-bottom:8px">Upload een eerder gedownloade <code>mijn_posities.csv</code> om je posities te herstellen.</div>', unsafe_allow_html=True)

    geupload = st.file_uploader("Kies CSV bestand", type=["csv"], label_visibility="collapsed")
    if geupload is not None:
        try:
            nieuw_df = lees_df_uit_upload(geupload)
            st.markdown(f'<div style="color:#3fb950;font-size:12px">✅ {len(nieuw_df)} posities gevonden in bestand.</div>', unsafe_allow_html=True)
            st.dataframe(nieuw_df, use_container_width=True, hide_index=True)
            if st.button("📥 Laad deze posities in"):
                st.session_state.df = nieuw_df
                st.cache_data.clear()
                st.success("Posities geladen!")
                st.rerun()
        except Exception as e:
            st.error(f"Fout bij inlezen: {e}")

    st.markdown("---")

    # ── Wis alles ──
    st.markdown("#### 🗑️ Wis alle posities")
    st.markdown('<div style="color:#7d8590;font-size:12px;margin-bottom:8px">Let op: dit verwijdert alle posities uit de huidige sessie. Download eerst een backup!</div>', unsafe_allow_html=True)
    if st.button("🗑️ Wis alle posities", key="wis_alles"):
        st.session_state.df = pd.DataFrame(columns=KOLOMMEN_CSV)
        st.session_state.koersen = {}
        st.cache_data.clear()
        st.rerun()
