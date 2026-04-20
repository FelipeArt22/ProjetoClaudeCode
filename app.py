import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Análise de Ações 2026", page_icon="📈", layout="wide")

ACOES = {
    "PETR4 — Petrobras": "PETR4.SA",
    "ITUB4 — Itaú Unibanco": "ITUB4.SA",
    "VALE3 — Vale": "VALE3.SA",
    "IVVB11 — iShares S&P 500": "IVVB11.SA",
}

CORES = {
    "PETR4.SA": "#009B3A",
    "ITUB4.SA": "#FF6600",
    "VALE3.SA": "#003087",
    "IVVB11.SA": "#8B0000",
}

@st.cache_data(ttl=3600)
def carregar_dados(tickers: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    hoje = date.today().isoformat()
    raw = yf.download(tickers, start="2026-01-01", end=hoje, auto_adjust=True, progress=False)

    if isinstance(raw.columns, pd.MultiIndex):
        precos = raw["Close"]
        volume = raw["Volume"]
    else:
        precos = raw[["Close"]].rename(columns={"Close": tickers[0]})
        volume = raw[["Volume"]].rename(columns={"Volume": tickers[0]})

    precos.dropna(how="all", inplace=True)
    volume.dropna(how="all", inplace=True)
    return precos, volume


def calcular_performance_pct(df: pd.DataFrame) -> pd.DataFrame:
    primeiro = df.iloc[0]
    return ((df / primeiro - 1) * 100).round(2)


st.title("📈 Análise de Ações 2026")
st.caption("Cotações PETR4, ITUB4, VALE3 e IVVB11 — dados via Yahoo Finance")

with st.sidebar:
    st.header("Configurações")
    st.subheader("Ações")
    selecionadas = [
        ticker
        for nome, ticker in ACOES.items()
        if st.checkbox(nome, value=True)
    ]

if not selecionadas:
    st.warning("Selecione ao menos uma ação na barra lateral.")
    st.stop()

with st.spinner("Carregando dados..."):
    df_precos, df_volume = carregar_dados(selecionadas)

df_precos = df_precos[selecionadas] if len(selecionadas) > 1 else df_precos
df_volume = df_volume[selecionadas] if len(selecionadas) > 1 else df_volume

nomes_inverso = {v: k for k, v in ACOES.items()}

# ── Métricas de resumo ────────────────────────────────────────────────────────
st.subheader("Resumo")
cols = st.columns(len(selecionadas))
for col, ticker in zip(cols, selecionadas):
    serie = df_precos[ticker].dropna()
    if len(serie) < 2:
        continue
    preco_atual = serie.iloc[-1]
    preco_anterior = serie.iloc[-2]
    retorno_ytd = ((serie.iloc[-1] / serie.iloc[0]) - 1) * 100
    variacao_dia = ((preco_atual / preco_anterior) - 1) * 100
    nome_curto = nomes_inverso[ticker].split("—")[0].strip()
    col.metric(
        label=nome_curto,
        value=f"R$ {preco_atual:.2f}",
        delta=f"{variacao_dia:+.2f}% hoje | YTD: {retorno_ytd:+.2f}%",
    )

st.divider()

# ── Performance Acumulada (%) ─────────────────────────────────────────────────
st.subheader("Performance Acumulada (%)")
st.caption("Retorno percentual acumulado desde 01/01/2026.")

df_perf = calcular_performance_pct(df_precos)
df_perf_long = df_perf.reset_index().melt(id_vars="Date", var_name="Ação", value_name="Retorno (%)")

fig_perf = px.line(
    df_perf_long,
    x="Date",
    y="Retorno (%)",
    color="Ação",
    color_discrete_map=CORES,
    labels={"Date": "Data"},
    hover_data={"Retorno (%)": ":.2f"},
)
fig_perf.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, annotation_text="0%")
fig_perf.update_layout(
    hovermode="x unified",
    yaxis_ticksuffix="%",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40),
)
st.plotly_chart(fig_perf, use_container_width=True)

st.divider()

# ── Volume Negociado Mensal ───────────────────────────────────────────────────
st.subheader("Volume Negociado Mensal")
st.caption("Soma do volume diário agrupado por mês.")

df_vol_mensal = df_volume.copy()
df_vol_mensal.index = pd.to_datetime(df_vol_mensal.index)
df_vol_mensal = df_vol_mensal.resample("ME").sum()
df_vol_mensal.index = df_vol_mensal.index.strftime("%b/%Y")

df_vol_long = df_vol_mensal.reset_index().melt(id_vars="Date", var_name="Ação", value_name="Volume")

fig_vol = px.bar(
    df_vol_long,
    x="Date",
    y="Volume",
    color="Ação",
    color_discrete_map=CORES,
    barmode="group",
    labels={"Date": "Mês", "Volume": "Volume"},
)
fig_vol.update_layout(
    yaxis_tickformat=".2s",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40),
)
st.plotly_chart(fig_vol, use_container_width=True)

st.divider()

# ── Resumo do Período ─────────────────────────────────────────────────────────
st.subheader("Resumo do Período")
st.caption("Estatísticas desde 01/01/2026 até o último pregão disponível.")

resumo_rows = []
for ticker in selecionadas:
    serie = df_precos[ticker].dropna()
    if len(serie) < 2:
        continue
    retornos_diarios = serie.pct_change().dropna()
    volatilidade_anual = retornos_diarios.std() * (252 ** 0.5) * 100
    resumo_rows.append({
        "Ativo": nomes_inverso[ticker].split("—")[0].strip(),
        "Abertura (R$)": f"{serie.iloc[0]:.2f}",
        "Atual (R$)": f"{serie.iloc[-1]:.2f}",
        "Mínimo (R$)": f"{serie.min():.2f}",
        "Máximo (R$)": f"{serie.max():.2f}",
        "Retorno YTD": f"{((serie.iloc[-1] / serie.iloc[0]) - 1) * 100:+.2f}%",
        "Volatilidade Anual": f"{volatilidade_anual:.1f}%",
    })

if resumo_rows:
    df_resumo = pd.DataFrame(resumo_rows).set_index("Ativo")
    st.dataframe(df_resumo, use_container_width=True)

st.divider()

# ── Preço de Fechamento Absoluto ──────────────────────────────────────────────
st.subheader("Preço de Fechamento (R$)")

fig_preco = go.Figure()
for ticker in selecionadas:
    serie = df_precos[ticker].dropna()
    nome_curto = nomes_inverso[ticker].split("—")[0].strip()
    fig_preco.add_trace(go.Scatter(
        x=serie.index,
        y=serie.values,
        name=nome_curto,
        line=dict(color=CORES[ticker]),
        hovertemplate=f"<b>{nome_curto}</b><br>Data: %{{x|%d/%m/%Y}}<br>R$ %{{y:.2f}}<extra></extra>",
    ))

fig_preco.update_layout(
    hovermode="x unified",
    yaxis_title="Preço (R$)",
    xaxis_title="Data",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40),
)
st.plotly_chart(fig_preco, use_container_width=True)

st.caption(f"Última atualização: {df_precos.index[-1].strftime('%d/%m/%Y')} | Fonte: Yahoo Finance")
