# Auditoria metodológica e conclusões — bicicletas

Escopo somente leitura: README.md, README-2.MD, fontes e saídas textuais do notebook via nbformat, tests/test_analise.py. Células abaixo numeradas a partir de zero. Não executado o notebook nem alterado o projeto; ajustes diagnósticos em memória com statsmodels, sem exportações. O revisor numérico independente cobre a recomputação integral.

## Parecer

Pronto no escopo metodológico, com as ressalvas já documentadas. Não identifiquei defeito metodológico demonstrado que torne os resultados apresentados incorretos. As escolhas são simples e limitadas, mas a documentação evita as principais extrapolações indevidas.

## Verificações e evidências de correção

- Fonte, DOI, ano e licença: a página primária UCI confirma Fanaee-T (2013), DOI 10.24432/C5W894, CC BY 4.0, registros diários/horários Capital Bikeshare 2011–2012. Os 17.389 registros da página referem-se à escala horária; não contradizem 731 registros diários. URL: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset . Confiança alta.
- Temperatura: células 0, 19, 24, 25, 34 e 40 identificam explicitamente a escala normalizada. Simples interpreta 0,1 unidade como 610,9 aluguéis/dia; múltiplo interpreta 0,1 como 368,3, IC [221,2;515,3]. Nenhum trecho lido converte isso indevidamente em 1 °C. Não é necessário impor conversão em Celsius para a análise ser válida. Confiança alta.
- Perguntas: as perguntas iniciais do README são refinadas no roadmap e notebook como coeficientes ajustados de workingday e temp. O teste de workingday não é de diferença bruta de médias; essa distinção está explícita nas células 14, 16, 32 e 34. Confiança alta.
- Temporalidade: ajuste simples/múltiplo e HAC usam somente os 547 dias até 30/06/2012. Teste contém os 184 dias seguintes, sem reajuste. Células 23, 25, 27, 33, 36. Sem casual/registered como preditoras; t_anos é calendário conhecido antecipadamente, não vazamento da resposta. Confiança alta.
- HAC/t: células 32–34 usam HAC maxlags=7, use_correction=True, use_t=True; Bartlett é padrão no statsmodels. 547 - (intercepto + 11 dummies mensais + temp + workingday + t_anos) = 532 graus de liberdade. Documentação identifica aproximação t, não exatidão em amostra finita. URL primária: https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html . Confiança alta.
- Hipóteses: workingday p=0,7994 e IC [-160,2;207,8] corretamente levam a não rejeitar H0; não dizem que médias são iguais. Temp p=1,153e-06, IC positivo, corretamente rejeita H0. Célula 33 mostra p arredondado como 0,0000 na tabela, mas célula 34 apresenta notação científica correta; não é um erro dos cálculos. Confiança alta.
- Referência: constante é média do treino, 3986,7971. Média do teste só é usada no denominador de R². Nenhum indício de usar resposta futura como previsão. MAE/RMSE menores e R² negativo da referência são coerentes com crescimento da demanda. Células 35–38. Confiança alta.
- Evolução temporal, célula 18: diagnóstico independente da média mensal confirma que TODOS os 12 meses de 2012 superam seus correspondentes de 2011. Jan/2011=1231,9; jun/2011=4783,7; dez/2011=2816,9. Jan/2012=3120,8; set/2012=7285,8; dez/2012=3990,7. A frase de menor uso no início/fim e maior nos meses intermediários é uma descrição qualitativa adequada, sem alegar monotonicidade. Confiança alta.
- Recomendações, células 40–41: explicitamente restritas à janela histórica, planejamento agregado, revisão operacional, novas validações e previsões meteorológicas prévias. Não quantificam benefício não medido; não confundem aluguéis com frota nem com pessoas. Associação não causal está registrada. Confiança alta.
- Testes automatizados: verificam em diretório temporário o split, exógenas, exportação, fórmulas das métricas e resultado HAC da biblioteca. Não substituem exame científico independente; consistência é o que verificam. Não executei novamente a suíte nesta subtarefa para evitar duplicar validação do outro revisor.

## Limitações e melhorias; não classificar como defeitos confirmados

### L1 — Uma janela e referência fraca

Severidade: baixa como melhoria; não bloqueante no escopo acadêmico. Confiança alta na limitação, nenhuma evidência de resultado errado.

A referência média de todo o treino ignora crescimento e sazonalidade, tornando a comparação relativamente fácil. Contudo ela é simples, válida, explicitamente especificada no README/roadmap e não usa dados futuros. O notebook limita a superioridade à janela histórica. Melhorar, se houver ampliação de escopo, com referência sazonal ou último valor disponível e validação temporal em múltiplas janelas, mantendo um teste final sem uso para seleção.

### L2 — Degradação treino/teste merece destaque, mas não foi ocultada por uma afirmação falsa

Severidade: baixa; oportunidade de contextualização. Confiança alta nos diagnósticos; não prova sobreajuste nem mudança estrutural.

Ajuste múltiplo recomputado em memória: treino MAE=641,9167, RMSE=847,9419, R²=0,754134; teste MAE=1032,2017, RMSE=1381,6635, R²=0,370289. Erro absoluto cresce ~60,8%, e teste não sustenta alegar desempenho igual ao ajuste. O notebook NÃO faz essa alegação: seção 6 diz explicitamente que desempenho preditivo vem na seção 8, que fornece as métricas corretas. Média cnt treino=3986,7971 vs teste=6042,9402. Viés médio observado-predito do múltiplo no teste=56,7101, portanto não há evidência de subestimação média grande do múltiplo. A queda pode refletir generalização, diferenças de período e distribuição, não demonstravelmente um erro. Acrescentar tabela treino/teste seria útil para defesa; não confundir comparação entre janelas diferentes com prova causal de sobreajuste.

### L3 — Exploração da série completa antes do split

Severidade: baixa, ressalva de rigor. Confiança alta no fato; baixa para afirmar influência indevida na especificação.

Células 12–21 exploram os 731 dias antes de definir o split. Célula 22 reconhece expressamente exploração retrospectiva e afirma que modelos/testes usam treino. Isso não é vazamento direto de resposta na matriz do ajuste. Pode haver seleção informada pelo teste se as escolhas foram modificadas após examinar o futuro, mas o repositório não prova essa sequência histórica. Não reportar vazamento confirmado. Para avaliação mais rigorosa futura, selecionar especificação com treino/validação temporal e guardar novo período externo.

### L4 — HAC não é reparo da especificação

Severidade: limitação já documentada; não um defeito. Confiança alta.

Autocorrelação residual de um dia=0,353; DW=1,287. Há omissões meteorológicas, possível não linearidade, pequena cobertura histórica e a escolha de sete lags não foi contrastada com alternativas. Tudo isso limita inferência/modelagem, mas o notebook alerta para relação não linear (célula 21), dependência residual (31), escolha inicial semanal e aproximação HAC/t (32), não causalidade e inadequação da fórmula (40). Ausência de teste formal de normalidade não invalida automaticamente OLS/HAC; t é aproximada e foi rotulada assim. Melhorias futuras: sensibilidade de lags, diagnósticos de heterocedasticidade, estabilidade temporal e modelos alternativos, sem escolher usando o mesmo teste final.

### L5 — Sem intervalos preditivos

Severidade: limitação já documentada; não erro. Confiança alta.

Célula 35 informa que previsões são pontuais e sem intervalos; célula 38 avisa que MAE não é intervalo nem limite diário. Não confundir IC de coeficiente com intervalo da demanda. Intervalos de previsão temporalmente calibrados seriam desejáveis antes de decisões operacionais mais exigentes.

## Conclusão para integração

Não promover melhorias de modelo ou ressalvas já escritas a bugs. Não usar apenas R² do treino, baseline negativo, coeficiente normalizado alto, t com HAC ou média mensal de 2012 maior como evidência de resultado incorreto. Os pontos demonstrados são limitações de alcance/generalização, que estão em grande parte explicitadas. O diagnóstico adicional de treino/teste enriquece a defesa e não contradiz os números publicados.
