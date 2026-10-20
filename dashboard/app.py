from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


RAIZ = Path(__file__).resolve().parents[1]
CORES = {"Dia útil": "#176B91", "Fim de semana ou feriado": "#CE6A26"}

st.set_page_config(page_title="Bicicletas compartilhadas", page_icon="🚲", layout="wide")
st.title("Bicicletas compartilhadas")
st.caption("Capital Bikeshare · Washington, DC · 2011–2012 · uma observação por dia")


def carregar_dados():
    base = pd.read_csv(RAIZ / "dados/tratados/day_tratado.csv", sep=";", parse_dates=["dteday"])
    previsoes = pd.read_csv(RAIZ / "resultados/previsoes.csv", parse_dates=["dteday"])
    metricas = pd.read_csv(RAIZ / "resultados/metricas_modelos.csv")
    testes = pd.read_csv(RAIZ / "resultados/testes_hipoteses.csv")
    return base.sort_values("dteday"), previsoes.sort_values("dteday"), metricas, testes


def apresentar(figura):
    figura.update_layout(
        template="plotly_white",
        font=dict(family="Arial", size=14, color="#223447"),
        height=420,
        margin=dict(t=65, b=55, l=55, r=25),
        legend=dict(orientation="h", y=1.14, x=0),
    )
    st.plotly_chart(figura, width="stretch", config={"displaylogo": False})


try:
    base, previsoes, metricas, testes = carregar_dados()
except FileNotFoundError:
    st.warning("Gere os dados antes de abrir o painel: execute `python scripts/executar_notebook.py` na raiz do projeto.")
    st.stop()
except (ValueError, pd.errors.ParserError):
    st.error("Não foi possível ler os resultados. Execute `python scripts/executar_notebook.py` para regenerar os arquivos.")
    st.stop()

with st.sidebar:
    st.header("Explorar dados")
    periodo = st.date_input(
        "Período",
        value=(base.dteday.min().date(), base.dteday.max().date()),
        min_value=base.dteday.min().date(),
        max_value=base.dteday.max().date(),
        format="DD/MM/YYYY",
    )
    tipos = st.multiselect("Tipo de dia", options=list(CORES), default=list(CORES))
    st.caption("Os filtros alteram a exploração descritiva. Previsões, métricas e testes mantêm os períodos indicados.")

st.header("Exploração descritiva")
if len(periodo) != 2:
    st.info("Selecione a data inicial e a data final do período.")
else:
    inicio, fim = map(pd.Timestamp, periodo)
    selecionados = base.loc[base.dteday.between(inicio, fim) & base.tipo_dia.isin(tipos)]
    if selecionados.empty:
        st.info("Nenhum dia corresponde aos filtros. Selecione pelo menos um tipo de dia ou amplie o período.")
    else:
        st.caption(f"{len(selecionados)} dias selecionados · {inicio:%d/%m/%Y} a {fim:%d/%m/%Y} · demanda em aluguéis/dia")
        serie = selecionados.set_index("dteday").reindex(pd.date_range(inicio, fim, name="dteday")).reset_index()
        apresentar(px.line(
            serie, x="dteday", y="cnt",
            title="Demanda diária",
            labels={"dteday": "Data", "cnt": "Aluguéis por dia"},
            color_discrete_sequence=["#176B91"],
        ))
        apresentar(px.scatter(
            selecionados, x="temp", y="cnt", color="tipo_dia", symbol="tipo_dia",
            color_discrete_map=CORES, opacity=0.6,
            hover_data={"dteday": "|%d/%m/%Y"},
            title="Temperatura e demanda diária",
            labels={"temp": "Temperatura normalizada", "cnt": "Aluguéis por dia", "tipo_dia": "Tipo de dia", "dteday": "Data"},
        ))
        resumo = selecionados.groupby("tipo_dia", as_index=False).agg(
            dias_observados=("cnt", "size"),
            media_diaria=("cnt", "mean"),
            mediana_diaria=("cnt", "median"),
            desvio_padrao=("cnt", "std"),
        )
        st.subheader("Demanda por tipo de dia")
        st.dataframe(
            resumo, hide_index=True, width="stretch",
            column_config={
                "tipo_dia": "Tipo de dia", "dias_observados": "Dias observados",
                "media_diaria": st.column_config.NumberColumn("Média (aluguéis/dia)", format="%.2f"),
                "mediana_diaria": st.column_config.NumberColumn("Mediana (aluguéis/dia)", format="%.2f"),
                "desvio_padrao": st.column_config.NumberColumn("Desvio padrão", format="%.2f"),
            },
        )

st.divider()
st.header("Avaliação das previsões")
st.caption("Teste fixo: 01/07 a 31/12/2012 · 184 dias · ajuste até 30/06/2012 · independente dos filtros")
st.caption("Previsões pontuais condicionais ao clima observado. Para uso antecipado, é necessária previsão meteorológica ou cenário.")
figura = go.Figure()
for coluna, nome, cor, tracejado in [
    ("cnt", "Observado", "#223447", "solid"),
    ("previsto_simples", "Simples", "#176B91", "dot"),
    ("previsto_multiplo", "Múltiplo", "#CE6A26", "dash"),
    ("previsto_referencia", "Média do treino", "#626A75", "dashdot"),
]:
    figura.add_trace(go.Scatter(
        x=previsoes.dteday, y=previsoes[coluna], name=nome, mode="lines",
        line=dict(color=cor, dash=tracejado),
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:.1f} aluguéis/dia<extra>%{fullData.name}</extra>",
    ))
figura.update_layout(title="Observado e previsto no teste", xaxis_title="Data", yaxis_title="Aluguéis por dia")
apresentar(figura)
st.subheader("Métricas no teste")
st.caption("MAE e RMSE em aluguéis/dia. R² é adimensional e pode ser negativo. A referência usa a média do treino.")
st.dataframe(
    metricas[["modelo", "mae", "rmse", "r2", "dias", "previsoes_negativas"]],
    hide_index=True, width="stretch",
    column_config={
        "modelo": "Modelo", "mae": st.column_config.NumberColumn("MAE", format="%.2f"),
        "rmse": st.column_config.NumberColumn("RMSE", format="%.2f"),
        "r2": st.column_config.NumberColumn("R²", format="%.3f"),
        "dias": "Dias", "previsoes_negativas": "Previsões negativas",
    },
)

st.header("Testes e intervalos de confiança")
st.caption("Treino fixo: 01/01/2011 a 30/06/2012 · 547 dias · regressão múltipla · independente dos filtros")
st.caption("H₀: coeficiente = 0; H₁: coeficiente ≠ 0. HAC/Bartlett com 7 defasagens e correção amostral; t aproximada; IC 95%; significância de 5%.")
st.caption("Estimativas em aluguéis/dia por unidade da preditora; temperatura normalizada. Associações exploratórias condicionais às demais variáveis.")
st.dataframe(
    testes[["variavel", "estimativa", "erro_padrao", "ic_inferior", "ic_superior", "p_valor", "graus_liberdade"]],
    hide_index=True, width="stretch",
    column_config={
        "variavel": "Variável",
        "estimativa": st.column_config.NumberColumn("Estimativa", format="%.2f"),
        "erro_padrao": st.column_config.NumberColumn("Erro padrão HAC", format="%.2f"),
        "ic_inferior": st.column_config.NumberColumn("IC 95% inferior", format="%.2f"),
        "ic_superior": st.column_config.NumberColumn("IC 95% superior", format="%.2f"),
        "p_valor": st.column_config.NumberColumn("Valor-p", format="%.4g"),
        "graus_liberdade": "Graus de liberdade",
    },
)

with st.expander("Fonte e definições"):
    st.markdown("Fanaee-T, H. (2013). [Bike Sharing — UCI](https://doi.org/10.24432/C5W894). Licença CC BY 4.0.")
    st.write("cnt: total de aluguéis no dia. workingday: 1 para dia útil; 0 para fim de semana ou feriado. temp: temperatura normalizada.")
    st.write("A unidade de observação é um dia. Aluguéis diários não equivalem ao número de bicicletas necessárias. A base não identifica demanda por estação.")
