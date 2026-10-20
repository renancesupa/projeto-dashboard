# Auditoria do projeto — 19/10/2026

**Parecer: compartilhar com ressalvas.** Não foram encontrados erros materiais nos cálculos dos resultados atuais. Foi corrigida uma apresentação enganosa do valor-p no notebook. A revisão numérica, de dados e de comportamento foi concluída no escopo abaixo; a inspeção visual completa permanece parcial. A branch auditada é `correcao/pessoa2-previsoes-dashboard`; não houve push nem merge.

## Achados prioritários e correções

1. **P1 — Valor-p apresentado como zero na seção 7 do notebook. Corrigido.** O arredondamento geral `round(4)` transformava o valor-p da temperatura, aproximadamente **1,15294 × 10⁻⁶**, em **0,0000**. Os cálculos, o CSV, a interpretação seguinte e a configuração da tabela do dashboard já preservavam o valor correto. A tabela do notebook agora usa quatro algarismos significativos para valor-p, exibindo **1,153e-06**, sem arredondar os dados exportados. Um teste que falhava antes passou após a execução em kernel limpo. [Evidência anterior](2026-10-19-tabela-antes.html), [teste de regressão](../../tests/test_apresentacao_notebook.py).

2. **P2 — Escopo e cronograma divergentes nos documentos. Correção proposta.** O README inicial menciona entrega em 13/10, filtro meteorológico e exploração de umidade/vento; `README-2.MD` define o mínimo para 16/10, com dois filtros e modelos mais simples. A implementação corresponde ao mínimo. Consolidar um documento de escopo e marcar explicitamente o outro como histórico. Isso não altera as métricas calculadas; a conformidade com exigências adicionais da disciplina depende do enunciado oficial, não fornecido nesta auditoria.

3. **Limitação do modelo, sem erro demonstrado de cálculo.** No múltiplo, MAE de treino é **641,92**, contra **1.032,20 aluguéis/dia** no teste; R² passa de **0,754** no treino para **0,370** no teste. O modelo tem utilidade limitada à avaliação apresentada e não sustenta uma promessa de alta precisão operacional. Uma única janela e a comparação com a média histórica do treino não demonstram superioridade geral. Para aprofundar, usar validação temporal e referências sazonais dentro de uma nova estratégia de avaliação, sem reutilizar o mesmo teste para escolher ajustes. As previsões atuais são pontuais, sem intervalos, e usam o clima observado retrospectivamente; essas limitações já estão documentadas.

## Resultados recalculados

Treino: **01/01/2011 a 30/06/2012 — 547 dias**. Teste: **01/07 a 31/12/2012 — 184 dias**.

| Modelo | MAE (aluguéis/dia) | RMSE (aluguéis/dia) | R² no teste |
|---|---:|---:|---:|
| Simples | 1.923,789094 | 2.174,872619 | −0,560286 |
| Múltiplo | 1.032,201670 | 1.381,663536 | 0,370289 |
| Média do treino | 2.452,640301 | 2.694,302464 | −1,394579 |

| Variável | Estimativa ajustada | Erro padrão HAC | IC 95% | Valor-p |
|---|---:|---:|---:|---:|
| `workingday` | 23,812091 | 93,675558 | [−160,207279; 207,831460] | 0,799441 |
| `temp` | 3.682,753092 | 748,454164 | [2.212,464936; 5.153,041249] | 1,15294 × 10⁻⁶ |

A inferência usa kernel Bartlett, sete defasagens, correção amostral `547/532` e distribuição t aproximada com 532 graus de liberdade. Temperatura é normalizada. Os dados tratados e todos os registros dos três CSVs de resultados conferem com a recomputação independente.

### Números que podem parecer contraditórios

- **R² negativo é válido.** Significa que a soma dos erros quadráticos excede a soma dos desvios em torno da média do próprio teste. Não é erro de sinal nem exige elevar outra correlação ao quadrado. A referência publicada usa a média do **treino**, por isso seu R² no teste não precisa ser zero. [Definição oficial de R²](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html).
- **3.682,75 e 368,28 não são resultados diferentes para a mesma unidade.** O primeiro é por uma unidade de temperatura normalizada; o segundo, por **0,1 unidade**. Nenhum é automaticamente a variação por 1 °C. O coeficiente da regressão simples é diferente porque não controla mês, tipo de dia e tendência.
- **Diferença descritiva e coeficiente ajustado respondem a perguntas diferentes.** Na série completa, a média de dias úteis supera a de dias não úteis em aproximadamente 254,65 aluguéis/dia. O coeficiente de `workingday`, 23,81, usa somente o treino e controla as outras variáveis. Seu IC inclui zero e p≈0,7994; não rejeitar H₀ não comprova igualdade.
- **MAE não é limite diário nem intervalo de previsão.** Erros individuais podem exceder o MAE. Melhores métricas que uma referência simples não garantem precisão suficiente para qualquer uso operacional.

## Fonte e qualidade dos dados

O arquivo `dados/brutos/day.csv` é **idêntico, byte a byte**, ao `day.csv` do ZIP oficial da [UCI](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). SHA-256 de ambos: `a6bcf826782d3c0fbfdcbeead17cd0884185a0dafe8ff10cd48a874ee7ba18be`.

Foram conferidos os 731 registros e 16 campos originais: continuidade diária, ausência de nulos e duplicatas, domínios, datas versus mês/ano/dia da semana, tipo de dia, contagens não negativas e `casual + registered = cnt`. A base tratada preserva todos os campos originais e acrescenta corretamente `tipo_dia` e `t_anos`. Nenhuma linha foi excluída; `casual` e `registered` não entram nas preditoras.

A documentação histórica do ZIP e a página atual da UCI apresentam diferenças em algumas descrições de normalização/estações. A análise atual evita esse conflito: não converte temperatura em °C e não usa rótulos de estação nos modelos nem nos filtros. Não foi atribuído significado adicional aos códigos sem evidência.

## Cobertura de qualidade e usabilidade

Os denominadores abaixo são unidades do inventário do escopo, não uma porcentagem de acurácia. **0/N significa que nenhum defeito remanescente foi observado; não significa inspeção visual integral.** Categorias se sobrepõem e não devem ser somadas.

| Categoria | Defeitos observados | Avaliação |
|---|---|---|
| Utilidade e completude | 0 / 4 | O mínimo definido no roadmap está presente: descrição, comparação das previsões, métricas e inferência. |
| Clareza analítica | 1 / 15 | Períodos, unidades e método identificados. Permanece divergência entre o escopo e a data do README inicial e o roadmap mínimo. |
| Consistência visual e interação | 0 / 8 | Valores e estados conferidos por AppTest. Inspeção visual parcial: tela inicial em 512 px e após fechar a emulação; seções inferiores e desktop completo não concluídos por noWindowsAvailable. Sete componentes/controles não tiveram inspeção visual completa; ver registro de cobertura. |

## Cobertura de correção analítica e robustez

| Categoria | Defeitos observados | Avaliação |
|---|---|---|
| Autoridade e confiança da fonte | 0 / 21 | day.csv é idêntico, byte a byte, ao arquivo oficial da UCI; cálculos associados têm evidência reproduzível. |
| Exatidão dos valores | 0 / 21 | Recalculo independente com matriz manual OLS/HAC, dados e metadados reconciliados; valor-p pequeno agora preservado na tabela do notebook. |
| Concordância em cada gráfico | 0 / 10 | Todos os valores dos sete gráficos salvos no notebook e dos três gráficos do dashboard conferidos contra dados e cálculos independentes; não equivale a aceitação visual completa. |
| Detalhamento das fontes | 0 / 13 | Bindings de sete gráficos do notebook e seis componentes do dashboard recuperáveis em código, CSVs, fonte e definições; sem consulta SQL. |
| Consistência entre artefatos | 0 / 4 | Descrição, previsões, métricas e hipóteses reconciliadas entre notebook, CSVs e painel. |
| Controles de qualidade dos dados | 0 / 7 | Bruto, tratado, previsões, métricas e hipóteses: datas, domínios, ausência de duplicatas/ausências, contagens, calendário, período e consistência validados. |
| Suporte às conclusões | 0 / 7 | Sete interpretações/recomendações verificadas; superioridade do múltiplo limitada à janela histórica. Sem inferência causal ou promessa operacional. |

## Método e evidências reproduzíveis

O recálculo não se limita a executar os mesmos testes ou chamar o mesmo ajuste do statsmodels. A matriz inclui explicitamente intercepto, temperatura, tipo de dia, onze indicadores mensais e tendência. OLS foi recalculado com `numpy.linalg.lstsq`; a covariância HAC foi construída por somas matriciais e pesos Bartlett. Valores-p t foram obtidos pela função beta incompleta e o crítico do IC por busca de raiz.

As diferenças máximas observadas contra os CSVs são da ordem de **10⁻¹¹**, compatíveis com precisão de ponto flutuante. Também foram comparados os valores efetivamente salvos nos sete gráficos do notebook, os três gráficos do dashboard e suas tabelas em seis estados: série completa, janeiro em dias úteis, um dia isolado, período sem correspondências, nenhum tipo de dia e data incompleta. Não apenas a presença dos componentes foi testada.

```bash
.venv/bin/python docs/auditoria/recalculo_independente.py
.venv/bin/python docs/auditoria/verificar_componentes.py
.venv/bin/python -m unittest discover -s tests -v
```

- [Recomposição independente dos números e hashes](2026-10-19-numeros.json).
- [Verificação das séries, tabelas e estados](2026-10-19-componentes.json).
- [Comparação com a fonte oficial](2026-10-19-fonte-uci.json).
- [Notas metodológicas independentes, anteriores à correção da tabela](2026-10-19-metodologia.md).
- [Inventário de cobertura e lacunas](2026-10-19-cobertura.json).

A execução integral do notebook após a correção concluiu 20 células sem erro. A suíte atual concluiu dez testes com sucesso, incluindo a regressão do valor-p. Os testes são evidência de comportamentos específicos; não certificam adequação científica para todo uso futuro.

## Limites da inspeção

Foi possível abrir o dashboard no Chrome nativo e observar a tela inicial em emulação de 512 px e depois de fechar a emulação. A inspeção visual das seções inferiores e do desktop completo foi interrompida quando a ferramenta retornou `noWindowsAvailable`. Não se afirma ausência de recortes, sobreposições ou problemas visuais em todos os tamanhos. Os valores das seções e os controles foram verificados por AppTest e pelos dados serializados dos gráficos.

Não foram recebidos os números específicos apontados pelo colega. Portanto, este parecer cobre os arquivos atuais locais, não versões antigas, prints externos, uma avaliação final da disciplina ou desempenho em novos períodos. Não foi demonstrado vazamento de resposta no ajuste atual; a exploração retrospectiva de toda a série antes da definição do corte permanece uma ressalva para futuras avaliações mais rigorosas.

As fontes primárias consultadas para o método foram a [documentação de covariância robusta do statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html), a [definição de R²](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html) e a [fonte UCI](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). Não foram alteradas as fórmulas, as métricas exportadas ou a especificação dos modelos para melhorar artificialmente o resultado.
