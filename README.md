# Modelagem Estatística — Demanda por Bicicletas Compartilhadas

Projeto acadêmico desenvolvido por duas pessoas, com entrega prevista para **13 de outubro de 2026 (terça-feira)**.

Este README reúne o escopo e as instruções de execução. O notebook implementa preparação, descrição, regressões, diagnóstico, testes HAC, previsões e avaliação; o dashboard consome os resultados exportados. O cronograma original foi mantido como registro do planejamento.

## Instalação e execução

Ambiente validado: Python 3.14.6. Execute os comandos a partir da raiz do repositório.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/executar_notebook.py
python -m streamlit run dashboard/app.py
```

O script executa o notebook inteiro em um kernel limpo com o Python do ambiente ativo, salva as saídas e regenera:

- `dados/tratados/day_tratado.csv`: 731 dias, separador `;`.
- `resultados/previsoes.csv`: previsões pontuais e observados nos 184 dias de julho a dezembro de 2012.
- `resultados/metricas_modelos.csv`: MAE, RMSE e R² no teste para regressão simples, múltipla e referência igual à média do treino.
- `resultados/testes_hipoteses.csv`: estimativas, erros padrão HAC, IC de 95%, valores-p e graus de liberdade dos dois coeficientes.

Também é possível abrir `notebooks/analise_bicicletas.ipynb` no Jupyter ou VS Code e executar todas as células em ordem. A leitura funciona com diretório de trabalho na raiz ou em `notebooks/`. Os dados brutos não são modificados.

Os filtros do dashboard alteram os gráficos e a tabela descritiva. O gráfico de previsões e as métricas preservam o teste completo; os testes estatísticos preservam o treino. A interface identifica esses períodos e não antecipa conclusões.

Validação automatizada, após gerar os resultados:

```bash
python -m unittest discover -s tests -v
```

Os testes verificam a auditoria, a separação temporal, as preditoras, o cálculo das métricas, a inferência HAC e o funcionamento dos filtros e estados vazios do dashboard.

## Objetivo e pergunta central

Analisar a relação do clima e do calendário com a demanda diária por bicicletas compartilhadas, utilizando análise descritiva, testes de hipóteses, intervalos de confiança e regressão linear.

**Pergunta central:** como as informações de clima e calendário podem ajudar a prever a demanda diária e planejar a disponibilidade de bicicletas?

As recomendações devem tratar do planejamento geral do serviço. A base escolhida não permite estimar a demanda de cada estação nem definir a redistribuição de bicicletas entre estações.

## Dataset

Será utilizada a versão diária do **Bike Sharing**, disponível no UCI Machine Learning Repository. A base contém registros do sistema Capital Bikeshare, em Washington, nos anos de 2011 e 2012.

- **Página oficial:** https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
- **Arquivo de análise:** `day.csv`.
- **Unidade de observação:** um dia.
- **Período:** 01/01/2011 a 31/12/2012.
- **Dimensões verificadas:** 731 registros e 16 colunas.
- **Auditoria inicial:** nenhum valor ausente e nenhuma linha duplicada.
- **Licença:** CC BY 4.0; manter a atribuição da fonte.

**Referência:** Fanaee-T, H. (2013). *Bike Sharing* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5W894.

### Variáveis principais

| Variável | Significado | Uso previsto |
|---|---|---|
| `dteday` | Data do registro | Ordenação temporal, filtros e criação de variáveis |
| `cnt` | Total de aluguéis no dia | Variável dependente da regressão |
| `temp` | Temperatura normalizada | Análise exploratória e candidata a preditora |
| `atemp` | Sensação térmica normalizada | Comparação com temperatura; avaliar redundância |
| `hum` | Umidade normalizada | Análise exploratória e candidata a preditora |
| `windspeed` | Velocidade do vento normalizada | Análise exploratória e candidata a preditora |
| `weathersit` | Categoria das condições meteorológicas | Comparações e candidata a preditora categórica |
| `workingday` | Dia útil, excluindo fins de semana e feriados | Comparações e candidata a preditora |
| `holiday`, `weekday`, `mnth`, `season`, `yr` | Informações de calendário | Exploração e seleção de preditoras |
| `casual`, `registered` | Aluguéis de usuários casuais e cadastrados | Exploração dos perfis de utilização |
| `instant` | Identificador sequencial do registro | Identificação; não usar automaticamente como preditora |

Consultar o `Readme.txt` original para interpretar códigos e normalizações. Variáveis categóricas não devem ser tratadas automaticamente como medidas numéricas contínuas.

## Escopo da análise

### 1. Preparação dos dados

- Preservar os arquivos originais.
- Converter e ordenar as datas.
- Verificar ausências, duplicidades, tipos, categorias e valores inconsistentes.
- Documentar a ausência de valores faltantes; não criar ausências artificiais.
- Preparar variáveis de calendário e a codificação das categorias necessárias ao modelo.
- Justificar os tratamentos realizados e avaliar valores extremos antes de excluir qualquer registro.

### 2. Análise descritiva

- Calcular medidas de posição e dispersão da demanda.
- Examinar a evolução temporal e os padrões de calendário.
- Comparar a distribuição da demanda entre tipos de dia e condições meteorológicas.
- Investigar relações com temperatura, umidade e vento.
- Registrar a pergunta que cada gráfico pretende responder.

### 3. Hipóteses e intervalos de confiança

Perguntas iniciais:

1. A demanda média difere entre dias úteis e dias não úteis?
2. A temperatura está associada à demanda, considerando calendário e tendência temporal?

Para cada análise, formular as hipóteses nula e alternativa, definir o nível de significância, justificar o teste, verificar os pressupostos e apresentar estimativas com intervalos de confiança. Os testes específicos serão escolhidos após a exploração dos dados.

### 4. Regressão e previsões

- Ajustar uma regressão linear simples como ponto de partida.
- Comparar com uma regressão linear múltipla usando clima e calendário.
- Interpretar coeficientes e seus intervalos de confiança.
- Avaliar resíduos, linearidade, variância dos erros, dependência temporal e redundância entre preditoras.
- Reservar o trecho final da série para avaliar previsões, mantendo o treino em datas anteriores.
- Comparar o desempenho com uma previsão simples de referência.
- Apresentar MAE, RMSE e R², identificando o conjunto em que cada métrica foi calculada.
- Demonstrar previsões para datas posteriores ao ajuste e explicitar as informações necessárias para produzi-las.

**Cuidados metodológicos:**

- `casual + registered = cnt`. Portanto, `casual` e `registered` não podem entrar como preditoras do total: isso entregaria a resposta ao modelo.
- Dias consecutivos podem ser dependentes. Não presumir independência nos testes ou nos intervalos de confiança; avaliar ajustes adequados à série temporal.
- Associação estatística não comprova causalidade.
- Previsões que usam clima futuro dependem de previsões meteorológicas ou de cenários explicitamente definidos.
- A demanda é uma contagem. Discutir as limitações da regressão linear, incluindo possíveis previsões negativas.
- Os dados históricos de Washington não sustentam, por si só, conclusões sobre a demanda atual ou sobre outras cidades.

### 5. Dashboard

O dashboard deve integrar a análise descritiva, as previsões e os resultados estatísticos, permitindo a exploração dos dados.

- Filtros por período, tipo de dia e condições meteorológicas.
- Gráfico de demanda ao longo do tempo.
- Comparações entre grupos e relações entre variáveis.
- Comparação de valores observados e previstos.
- Tabelas com métricas, estimativas, intervalos de confiança e resultados dos testes.

Cada visualização deve ter um objetivo claro. **Não incluir textos que antecipem os insights ou as conclusões ao usuário.** Títulos neutros, unidades e explicações sobre filtros e medidas ajudam a leitura sem entregar a interpretação.

## Divisão do trabalho

Substituir “Pessoa 1” e “Pessoa 2” pelos nomes dos integrantes. A divisão define a liderança de execução; ambos devem compreender todo o projeto.

| Responsável | Atividades principais | Saídas esperadas |
|---|---|---|
| Pessoa 1 | Auditoria, preparação, análise descritiva, testes de hipóteses e intervalos de confiança | Base tratada, seções correspondentes do notebook, gráficos e tabela dos testes |
| Pessoa 2 | Regressão, avaliação das previsões e construção do dashboard | Seções de modelagem do notebook, métricas, previsões e aplicação interativa |
| Ambos | Definição das perguntas, interpretação, recomendações, revisão e preparação da defesa | Notebook integrado, recomendações fundamentadas e domínio individual do conteúdo |

### Como integrar as partes

1. Definir juntos as colunas da base tratada, as variáveis candidatas e a divisão temporal de treino e teste.
2. A Pessoa 1 prepara a base; a Pessoa 2 usa essa mesma versão na modelagem.
3. Exportar resultados com nomes de colunas claros para consumo pelo dashboard.
4. Integrar as seções no notebook final, evitando alterações simultâneas no mesmo arquivo. Durante o desenvolvimento, podem ser usados notebooks separados.
5. Cada integrante revisa e explica as decisões tomadas pelo outro.

## Cronograma

| Data | Meta |
|---|---|
| **09/10 — sexta-feira** | Conhecer a base, confirmar o escopo e dividir as atividades |
| **10/10 — sábado** | Preparação, análise descritiva e primeira versão da regressão |
| **11/10 — domingo** | Testes, intervalos de confiança, avaliação do modelo e dashboard |
| **12/10 — segunda-feira** | Integrar e revisar os entregáveis; treinar a defesa individual |
| **13/10 — terça-feira** | Conferência final e entrega |

## Estrutura de pastas planejada

```text
projeto/
├── README.md
├── requirements.txt
├── dados/
│   ├── brutos/
│   │   ├── day.csv
│   │   └── Readme.txt
│   └── tratados/
│       └── day_tratado.csv
├── notebooks/
│   └── analise_bicicletas.ipynb
├── dashboard/
│   └── app.py
├── resultados/
│   ├── metricas_modelos.csv
│   ├── testes_hipoteses.csv
│   ├── previsoes.csv
│   └── figuras/
└── apresentacao/
    └── roteiro_defesa.md
```

**Fluxo:** dados brutos → notebook → dados tratados e resultados → dashboard.

Os arquivos de execução implementados estão descritos acima. `Readme.txt`, figuras exportadas e roteiro de defesa são itens previstos nesta estrutura que não foram adicionados nesta etapa. A atribuição e o significado das variáveis utilizadas estão documentados neste README e no notebook.

## Ferramentas e decisões adotadas

Os integrantes já possuem conhecimento em Python, pandas e SciPy. Python será utilizado no notebook.

- Regressão: statsmodels; dashboard: Streamlit e Plotly.
- Modelo simples: `cnt ~ temp`.
- Modelo múltiplo: `cnt ~ temp + workingday + C(mnth) + t_anos`, com janeiro como mês de referência.
- Treino: até 30/06/2012, 547 dias; teste: 01/07 a 31/12/2012, 184 dias.
- Referência preditiva: média de `cnt` no treino, sem usar contagens futuras.
- Testes bilaterais exploratórios dos coeficientes de `workingday` e `temp`; significância de 5% e IC de 95%.
- Covariância HAC/Bartlett com sete defasagens e correção amostral; distribuição t aproximada com 532 graus de liberdade residuais. [Referência da implementação](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html).
- Previsões condicionais ao clima observado no teste; uso antecipado exige previsão meteorológica ou cenário.

As interpretações e limitações dos resultados ficam no notebook. A preparação para a defesa individual permanece uma responsabilidade dos dois integrantes.

## Entregáveis e avaliação

- **Notebook Python:** processo completo, justificativas, resultados, conclusões, recomendações e limitações. Usar células Markdown para a documentação e manter o código sem comentários, conforme a orientação do projeto.
- **Dashboard interativo:** gráficos, tabelas, cálculos e filtros com propósito definido, sem textos que revelem diretamente os insights.
- **Apresentação e defesa individual:** explicar os conceitos, as escolhas metodológicas e os resultados. Slides são opcionais.

**A defesa oral vale 80% da nota e os entregáveis técnicos, 20%.** Ambos precisam explicar as hipóteses, os intervalos, a regressão, as métricas, o tratamento dos dados e as limitações, inclusive nas partes executadas pelo colega.

## Checklist de conclusão

- [x] Fonte e significado das variáveis documentados.
- [x] Auditoria e preparação dos dados justificadas.
- [x] Gráficos descritivos com perguntas claras.
- [x] Hipóteses, testes e intervalos de confiança apresentados e interpretados.
- [x] Regressão implementada, interpretada e avaliada em dados posteriores ao treino.
- [x] Previsões comparadas com uma referência simples.
- [x] Recomendações fundamentadas e limitações discutidas.
- [x] Dashboard interativo integrado aos resultados.
- [x] Notebook executado do início ao fim, com código sem comentários.
- [x] Dependências e instruções de execução registradas.
- [ ] Ambos preparados para a defesa individual.
