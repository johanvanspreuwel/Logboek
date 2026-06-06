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

Streamlit Cloud heeft **geen permanente opslag** per sessie.  
Zo bewaar je je posities:

1. Voeg je posities in via **➕ Toevoegen**
2. Ga naar **💾 Data** → download `mijn_posities.csv`
3. Bewaar dit bestand op je telefoon/PC
4. Bij een nieuwe sessie: upload het terug via **📥 Importeer CSV**

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
