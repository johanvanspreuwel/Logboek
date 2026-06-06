# 📈 Trading Logboek & Portfolio Tracker

Mobiel-vriendelijke web-versie van het Trading Logboek.  
Gebouwd met Streamlit · yfinance · Dark Theme

---

## 🚀 Online zetten in 5 stappen

### Stap 1 — Maak een GitHub repository aan

1. Ga naar [github.com](https://github.com) en log in
2. Klik rechtsboven op **+** → **New repository**
3. Geef het een naam, bijv. `trading-logboek`
4. Zet op **Public** (vereist voor gratis Streamlit Cloud)
5. Klik **Create repository**

### Stap 2 — Upload de bestanden

In je nieuwe repository:
1. Klik op **Add file** → **Upload files**
2. Sleep deze twee bestanden erheen:
   - `app.py`
   - `requirements.txt`
3. Klik **Commit changes**

### Stap 3 — Verbind met Streamlit Cloud

1. Ga naar [share.streamlit.io](https://share.streamlit.io)
2. Log in met je GitHub account
3. Klik **New app**
4. Kies:
   - **Repository:** jouw `trading-logboek` repo
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Klik **Deploy!**

### Stap 4 — Wacht ~2 minuten

Streamlit installeert automatisch de packages uit `requirements.txt`.  
Je krijgt een publieke URL zoals:  
`https://jouwnaam-trading-logboek-app-xyz123.streamlit.app`

### Stap 5 — Open op je telefoon

Ga naar die URL op je telefoon — werkt direct als een app!  
Tip: voeg hem toe aan je beginscherm via "Delen → Zet op beginscherm".

---

## 💾 Data bewaren tussen sessies

De app slaat je posities automatisch op in `mijn_posities.csv` in dezelfde map als `app.py`.  
Dit bestand wordt bij elke herstart automatisch ingelezen — **je hoeft niets te doen**.

### Hoe werkt het op Streamlit Cloud?
- Je voegt een positie toe → de app schrijft direct naar `mijn_posities.csv` op de server
- Je herstart de app → `init_state()` leest het bestand automatisch in
- Je data blijft bewaard **zolang de app op dezelfde server draait**

### Backup maken (aanbevolen)
Streamlit Cloud kan apps herdeployen bij updates, waardoor de server-CSV gereset wordt.  
Maak daarom regelmatig een backup via **💾 Data → Download mijn_posities.csv**.  
Bij een reset: upload het bestand terug via **📥 Importeer CSV** — dan ben je in 1 klik hersteld.

---

## 📱 Functies

| Functie | Beschrijving |
|---|---|
| 📊 Portfolio | Live koersen, pre/after-market, status-alerts |
| ➕ Toevoegen | Positie toevoegen met validatie |
| 💾 Data | Import/export CSV voor datapersistentie |
| 🎯 Doel Reis | Voortgang richting € 200.000 |
| ⏱ Tempo | Weken tot doel op basis van 2.534%/week |
| ♻️ Refresh | Koersen vernieuwen (gecached 60 seconden) |

---

## 🛠 Lokaal draaien

```bash
pip install streamlit yfinance pandas
streamlit run app.py
```

Ga dan naar `http://localhost:8501` in je browser.
