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
    "PETR4.SA": "#009B3A",  # verde Petrobras
    "ITUB4.SA": "#FF6600",  # laranja Itaú
    "VALE3.SA": "#003087",  # azul Vale
    "IVVB11.SA": "#8B0000",  # vermelho escuro iShares
}

@st.cache_data(ttl=3600)
def carregar_dados(tickers: list[str]) -> pd.DataFrame:
    hoje = date.today().isoformat()
    df = yf.download(tickers, start="2026-01-01", end=hoje, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(name=tickers[0])
    df.dropna(how="all", inplace=True)
    return df


def calcular_performance(df: pd.DataFrame) -> pd.DataFrame:
    primeiro = df.iloc[0]
    return (df / primeiro * 100).round(2)


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
    df_precos = carregar_dados(selecionadas)

df_precos = df_precos[selecionadas] if len(selecionadas) > 1 else df_precos

df_perf = calcular_performance(df_precos)

# Métricas de resumo
st.subheader("Resumo")
cols = st.columns(len(selecionadas))
nomes_inverso = {v: k for k, v in ACOES.items()}

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

# Gráfico 1: Performance relativa (base 100)
st.subheader("Performance Relativa (base 100 em 01/01/2026)")
st.caption("Permite comparar o rendimento proporcional independente do preço absoluto.")

df_perf_long = df_perf.reset_index().melt(id_vars="Date", var_name="Ação", value_name="Performance")

fig1 = px.line(
    df_perf_long,
    x="Date",
    y="Performance",
    color="Ação",
    color_discrete_map=CORES,
    labels={"Date": "Data", "Performance": "Performance (base 100)"},
    hover_data={"Performance": ":.2f"},
)
fig1.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5, annotation_text="Base")
fig1.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40),
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# Gráfico 2: Preço de fechamento absoluto (R$)
st.subheader("Preço de Fechamento (R$)")

fig2 = go.Figure()
for ticker in selecionadas:
    serie = df_precos[ticker].dropna()
    nome_curto = nomes_inverso[ticker].split("—")[0].strip()
    fig2.add_trace(go.Scatter(
        x=serie.index,
        y=serie.values,
        name=nome_curto,
        line=dict(color=CORES[ticker]),
        hovertemplate=f"<b>{nome_curto}</b><br>Data: %{{x|%d/%m/%Y}}<br>R$ %{{y:.2f}}<extra></extra>",
    ))

fig2.update_layout(
    hovermode="x unified",
    yaxis_title="Preço (R$)",
    xaxis_title="Data",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40),
)
st.plotly_chart(fig2, use_container_width=True)

st.caption(f"Última atualização: {df_precos.index[-1].strftime('%d/%m/%Y')} | Fonte: Yahoo Finance")
