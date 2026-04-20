# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt   # install dependencies
streamlit run app.py              # start the app (opens in browser)
```

## Architecture

Single-file Streamlit dashboard (`app.py`) for Brazilian stock price analysis in 2026.

**Data flow:**
1. `carregar_dados()` — fetches OHLCV data from Yahoo Finance via `yfinance`, cached 1 hour with `@st.cache_data`
2. `calcular_performance()` — re-indexes closing prices to 100 on 2026-01-01 for relative comparison
3. Streamlit renders a sidebar (stock selectors), summary metrics row, and two Plotly charts (relative performance + absolute price in R$)

**Stocks tracked:** PETR4 (Petrobras), ITUB4 (Itaú), VALE3 (Vale) — Yahoo Finance suffixes these as `PETR4.SA`, etc.

**Dependencies:** `streamlit`, `yfinance`, `pandas`, `plotly`
