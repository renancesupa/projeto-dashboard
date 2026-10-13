# Roadmap mínimo — entrega sexta-feira, 16/10

## O que entregar

**Notebook:**

- Fonte, objetivo e significado das variáveis utilizadas.
- Conferência de ausências, duplicidades e tipos.
- Análise descritiva básica.
- Regressão simples e múltipla.
- Dois testes de hipóteses com intervalos de confiança.
- Previsões para o período posterior ao treino.
- Avaliação do desempenho.
- Recomendações e limitações.

**Dashboard:**

- Dois filtros: período e tipo de dia.
- Três gráficos.
- Tabelas de médias, métricas e testes.
- Sem textos que antecipem conclusões.

**Defesa:** ambos precisam explicar o trabalho completo. Ela vale 80% da nota.

## Divisão

- **Pessoa 1:** preparação, descrição, testes e documentação.
- **Pessoa 2:** regressão, previsões e dashboard.
- **Ambos:** interpretação, revisão e defesa.

Trabalhar em notebooks separados até quinta-feira evita conflitos.

## Segunda, 12/10 — Base e primeira regressão

| Pessoa | Tarefa específica | Resultado |
|---|---|---|
| **1 — aproximadamente 75 min** | Ler `day.csv`; converter e ordenar datas; conferir ausências, duplicidades e `casual + registered = cnt`; criar `t_anos`, tempo desde 01/01/2011 em anos; salvar a base preparada; escrever a auditoria em Markdown | Base pronta e preparação documentada |
| **2 — aproximadamente 75 min** | Ler a base preparada assim que disponível; separar treino até 30/06/2012 e teste a partir de 01/07/2012; ajustar regressão simples `cnt ~ temp` | Primeiro modelo executando |
| **Ambos — 15 min** | Conferir a divisão temporal e explicar por que `casual` e `registered` não entram como preditoras | Decisões compreendidas pelos dois |

**Não fazer:** imputação, exclusão automática de extremos ou transformações desnecessárias. A base conferida não possui ausências nem duplicidades; documentar isso cumpre essa parte da preparação.

## Terça, 13/10 — Descrição e modelo múltiplo

| Pessoa | Tarefa específica | Resultado |
|---|---|---|
| **1 — 75 min** | Calcular média, mediana, desvio-padrão e quartis de `cnt`; criar série temporal e dispersão temperatura × demanda; calcular média e quantidade de dias por `workingday`; explicar o objetivo de cada gráfico | Descrição e gráficos prontos |
| **2 — 75 min** | Ajustar `cnt ~ temp + workingday + C(mnth) + t_anos`; examinar resíduos versus previsto e autocorrelação dos resíduos; registrar limitações | Modelo múltiplo e diagnóstico básico |
| **Ambos — 15 min** | Explicar os coeficientes e fechar as duas hipóteses abaixo | Modelo e perguntas definidos |

**Hipóteses:**

1. O coeficiente de `workingday` é diferente de zero, controlando temperatura, mês e tendência?
2. O coeficiente de `temp` é diferente de zero, controlando as demais variáveis?

Nas duas: **H₀ = coeficiente zero; H₁ = coeficiente diferente de zero**.

Usar significância de 5% e intervalos de confiança de 95%. Como surgiram de uma análise exploratória, apresentar os testes como evidência exploratória.

## Quarta, 14/10 — Testes, previsões e dashboard inicial

| Pessoa | Tarefa específica | Resultado |
|---|---|---|
| **1 — 75 min** | Obter testes e intervalos dos dois coeficientes usando erros-padrão HAC com sete defasagens; registrar estimativa, IC, p-valor e graus de liberdade; escrever a interpretação | Tabela dos testes pronta |
| **2 — 75 min** | Prever os dias de julho a dezembro com os dois modelos; calcular MAE e R² no teste; exportar resultados; iniciar dashboard em Streamlit | Previsões, métricas e aplicação inicial |
| **Ambos — 15 min** | Conferir interpretação dos intervalos, p-valores e erros de previsão | Resultados compreendidos |

**Previsões:** os dias do teste são posteriores ao período utilizado no ajuste. Isso demonstra a previsão exigida sem precisar criar um simulador.

Explicar que o clima observado do teste é conhecido retrospectivamente. Para prever antecipadamente, seria necessário fornecer previsão meteorológica ou um cenário.

## Quinta, 15/10 — Fechar os entregáveis

| Pessoa | Tarefa específica | Resultado |
|---|---|---|
| **1 — 75 min** | Integrar os notebooks; colocar justificativas em Markdown; escrever duas recomendações e as limitações; conferir ausência de comentários nas células de código | Notebook completo |
| **2 — 75 min** | Finalizar filtros, gráficos e tabelas; conferir números contra o notebook; registrar dependências e instruções de execução | Dashboard completo |
| **Ambos — 15 min** | Cada um explica uma parte feita pelo colega | Revisão cruzada |

**Dashboard mínimo:**

| Elemento | Finalidade |
|---|---|
| Demanda ao longo do tempo | Explorar evolução temporal |
| Temperatura × demanda | Explorar a relação entre variáveis |
| Observado × previsto no teste | Examinar acertos e erros da previsão |
| Tabela por tipo de dia | Comparar média e quantidade de observações |
| Tabela de MAE e R² | Mostrar desempenho de cada modelo |
| Tabela dos testes e intervalos | Mostrar magnitude e incerteza das associações |

Os filtros alteram a exploração descritiva. As métricas e os testes permanecem identificados com seus períodos originais.

**Recomendações:** escrever somente o que os resultados sustentarem. Para cada proposta, indicar evidência, ação de planejamento, benefício esperado e limitação. Não inventar economia ou aumento de demanda.

## Sexta, 16/10 — Conferir e entregar

| Pessoa | Tarefa específica | Resultado |
|---|---|---|
| **1 — aproximadamente 45 min** | Reiniciar e executar o notebook inteiro; conferir resultados, textos e fonte | Notebook reproduzível |
| **2 — aproximadamente 45 min** | Abrir o dashboard; testar filtros; conferir arquivos e instruções; preparar entrega | Pacote funcionando |
| **Ambos — 20 min** | Fazer perguntas um ao outro e conferir o envio | Defesa preparada e entrega verificada |

Não implementar funcionalidades novas na sexta-feira.

## Códigos necessários e motivo de cada escolha

| Código ou recurso | Por que usar |
|---|---|
| `pd.read_csv(..., parse_dates=["dteday"])` | Ler dados e reconhecer datas |
| `sort_values("dteday")` | Preservar a ordem temporal |
| `isna()` e `duplicated()` | Verificar e documentar problemas na base |
| Criação de `t_anos` | Representar tendência temporal de maneira explícita |
| `describe()` e `groupby().agg()` | Produzir estatísticas descritivas e comparações básicas |
| Separação por data | Avaliar em dias posteriores ao treino, evitando embaralhar passado e futuro |
| `smf.ols("cnt ~ temp", ...)` | Criar uma regressão simples, fácil de interpretar |
| `smf.ols("cnt ~ temp + workingday + C(mnth) + t_anos", ...)` | Considerar temperatura, tipo de dia, sazonalidade e tendência conjuntamente |
| `C(mnth)` | Tratar meses como categorias, sem supor uma relação crescente de janeiro a dezembro |
| Ajuste com `cov_type="HAC"` e `maxlags=7` | Considerar possível heterocedasticidade e dependência entre dias na inferência |
| `t_test()` e `conf_int()` | Testar as duas hipóteses e quantificar incerteza |
| Resíduos versus previsto e autocorrelação | Conferir limitações do modelo |
| `predict(teste)` | Gerar previsões sem ajustar o modelo nos dias reservados |
| MAE e R² | Mostrar erro em aluguéis/dia e desempenho relativo à variabilidade do teste |
| `to_csv()` | Compartilhar os mesmos resultados entre notebook e dashboard |
| Streamlit e Plotly | Construir filtros, tabelas e gráficos interativos usando Python |

**Por que sete defasagens no HAC?** É um ponto de partida ligado ao ciclo semanal. Explicar essa escolha e sua limitação: HAC ajusta a incerteza, mas não corrige uma relação mal especificada nem garante previsões melhores.

## Documentação mínima do notebook

Antes de cada bloco, escrever duas ou três frases em Markdown:

1. O que será feito.
2. Por que o método foi escolhido.
3. Qual pressuposto ou cuidado importa.

Depois, interpretar o resultado real. O código fica sem comentários.

## Limitações que precisam aparecer

- Associação não demonstra causalidade.
- `cnt` é uma contagem; a regressão linear pode produzir valores negativos.
- A temperatura está normalizada: o coeficiente não representa automaticamente 1 °C.
- A previsão antecipada depende de informações meteorológicas.
- Os dados não permitem planejar redistribuição por estação.
- Aluguéis por dia não equivalem ao número necessário de bicicletas.
- Os resultados históricos de Washington não se transferem automaticamente para outras cidades ou para o presente.

## Perguntas essenciais para a defesa

Os dois devem conseguir explicar:

- Por que escolheram essas variáveis?
- Por que excluíram `casual` e `registered`?
- Por que dividiram os dados por data?
- O que representam os coeficientes?
- O que significam p-valor e intervalo de confiança?
- Por que utilizar HAC?
- O que MAE e R² mostram?
- Qual evidência sustenta cada recomendação?

**Se faltar tempo:** cortar acabamento visual e gráficos extras. Preservar análise correta, notebook executável, dashboard interativo e entendimento individual.