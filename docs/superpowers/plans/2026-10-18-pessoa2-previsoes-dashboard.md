# Correções e avanço da análise de bicicletas

**Objetivo:** corrigir o notebook do PR #1 e concluir o fluxo local de previsões e dashboard descrito em README-2.MD.

**Arquitetura:** notebook reproduzível lê dados brutos, prepara e exporta a base e resultados. O dashboard Streamlit consome os CSVs; filtros alteram somente a exploração descritiva. Modelos, métricas e testes conservam seus períodos originais.

**Tecnologias:** Python, pandas, NumPy, SciPy, statsmodels, Plotly, Streamlit e nbclient. Sem serviços externos.

**Restrições:** manter alterações locais do kernel, arquivos brutos intactos, explicações em Markdown e código sem comentários. Treino até 30/06/2012 e teste de 01/07 a 31/12/2012; nenhuma preditora derivada da resposta. HAC com sete defasagens e IC de 95%; informar método e limitações. Dashboard sem textos que antecipem conclusões.

- [x] Criar testes de regressão que reproduzam a auditoria incorreta e verifiquem ausência de vazamento temporal, exportações e inferência HAC. Executar com `.venv/bin/python -m unittest discover -s tests -v` e confirmar falhas esperadas.
- [x] Corrigir conversão e ordenação das datas antes da auditoria, retirar comentários das células e atualizar documentação. Ordenar temperatura para desenhar a reta de regressão; acrescentar ACF dos resíduos e interpretação.
- [x] Concluir inferência dos dois coeficientes, previsões no teste, MAE/RMSE/R² e referência igual à média do treino. Exportar `previsoes.csv`, `metricas_modelos.csv`, `testes_hipoteses.csv` em `resultados/` e base com separador ponto e vírgula em `dados/tratados/day_tratado.csv`.
- [x] Implementar `dashboard/app.py`: filtros de datas e tipo de dia; evolução temporal, dispersão e observado versus previsto; tabelas por tipo de dia, métricas e testes; estados vazios e resultados fixos explicitamente identificados.
- [x] Documentar instalação, execução do notebook e dashboard no README. Executar testes, notebook integral em kernel limpo e AppTest do Streamlit, incluindo filtros e estados vazios. Inspecionar gráficos renderizados se houver navegador disponível.

Não fazer merge ou publicar como parte desta etapa. A branch parte de pessoa2 para preservar as alterações do PR e receber as correções.

## Verificação

- Execução em kernel limpo concluída: 20 células, nenhum erro, sete gráficos com saídas salvas.
- Nove testes unittest/AppTest passaram, incluindo auditoria, inferência, métricas, filtros, seleção vazia e arquivos ausentes.
- Servidor local Streamlit iniciado em 127.0.0.1:8501. Inspeção visual pendente: não há navegador disponível no ambiente; o CLI agent-browser não está instalado e a listagem CUA de navegadores está vazia. A prévia HTML do notebook foi gerada em diretório temporário para inspeção manual.
- Metadados locais do kernel preservados; dados brutos e branch pessoa2 preservados. Nenhum push ou merge realizado.
