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

## GitHub Integration

The repo is version-controlled with git. A PostToolUse hook in `.claude/settings.json` auto-commits and pushes to GitHub after every Write/Edit. For this to work, the GitHub remote must be configured.

**One-time setup (required):** Install `gh` CLI and create the remote repo:

```bash
# Install gh CLI (requires Homebrew — install from https://brew.sh if missing)
brew install gh

# Authenticate
gh auth login

# Create the GitHub repo and push
gh repo create ProjetoClaudeCode --public --source=. --remote=origin --push
```

After that, every file edit by Claude Code will automatically commit and push to GitHub.
