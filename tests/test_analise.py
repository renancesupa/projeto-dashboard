import contextlib
import io
import os
from pathlib import Path
import shutil
import tempfile
import tokenize
import unittest
from unittest.mock import patch

import nbformat
import numpy as np
import pandas as pd
import plotly.basedatatypes
import statsmodels.formula.api as smf


RAIZ = Path(__file__).resolve().parents[1]


class AnaliseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporario.cleanup)
        cls.raiz = Path(cls.temporario.name)
        (cls.raiz / "notebooks").mkdir()
        (cls.raiz / "dados/brutos").mkdir(parents=True)
        (cls.raiz / "dados/tratados").mkdir()
        shutil.copy(RAIZ / "dados/brutos/day.csv", cls.raiz / "dados/brutos/day.csv")
        cls.notebook = nbformat.read(RAIZ / "notebooks/analise_bicicletas.ipynb", as_version=4)
        cls.contexto = {"__name__": "__main__"}
        anterior = Path.cwd()
        try:
            os.chdir(cls.raiz / "notebooks")
            with patch.object(plotly.basedatatypes.BaseFigure, "show"), contextlib.redirect_stdout(io.StringIO()):
                for indice, celula in enumerate(cls.notebook.cells):
                    if celula.cell_type == "code":
                        exec(compile(celula.source, f"celula_{indice + 1}", "exec"), cls.contexto)
        finally:
            os.chdir(anterior)

    def test_auditoria_nao_inventa_dias_ausentes(self):
        self.assertEqual(self.contexto["auditoria"]["dias_sem_registro"], 0)

    def test_codigo_sem_comentarios(self):
        comentarios = []
        for indice, celula in enumerate(self.notebook.cells):
            if celula.cell_type == "code":
                for token in tokenize.generate_tokens(io.StringIO(celula.source).readline):
                    if token.type == tokenize.COMMENT:
                        comentarios.append(indice + 1)
        self.assertEqual(comentarios, [], "Mover explicações para Markdown")

    def test_modelos_usam_somente_passado_sem_componentes_da_resposta(self):
        treino, teste = self.contexto["treino"], self.contexto["teste"]
        self.assertEqual((len(treino), len(teste)), (547, 184))
        self.assertLess(treino.dteday.max(), teste.dteday.min())
        for nome in ["modelo_simples", "modelo_multiplo"]:
            modelo = self.contexto[nome]
            self.assertEqual(modelo.nobs, 547)
            self.assertFalse({"casual", "registered", "cnt"} & set(modelo.model.exog_names))

    def test_exporta_previsoes_e_metricas_recalculaveis_no_teste(self):
        pasta = self.raiz / "resultados"
        self.assertTrue((pasta / "previsoes.csv").exists(), "Exportação de previsões ausente")
        previsoes = pd.read_csv(pasta / "previsoes.csv", parse_dates=["dteday"])
        metricas = pd.read_csv(pasta / "metricas_modelos.csv")
        self.assertEqual(len(previsoes), 184)
        self.assertEqual(previsoes.dteday.min(), pd.Timestamp("2012-07-01"))
        self.assertEqual(previsoes.dteday.max(), pd.Timestamp("2012-12-31"))
        for nome, coluna in [("Simples", "previsto_simples"), ("Múltiplo", "previsto_multiplo"), ("Média do treino", "previsto_referencia")]:
            linha = metricas.set_index("modelo").loc[nome]
            erro = previsoes.cnt - previsoes[coluna]
            self.assertAlmostEqual(linha.mae, erro.abs().mean())
            self.assertAlmostEqual(linha.rmse, np.sqrt((erro ** 2).mean()))
            self.assertAlmostEqual(linha.r2, 1 - (erro ** 2).sum() / ((previsoes.cnt - previsoes.cnt.mean()) ** 2).sum())
            self.assertEqual(linha.dias, 184)
        np.testing.assert_allclose(previsoes.previsto_referencia, self.contexto["treino"].cnt.mean())
        np.testing.assert_allclose(previsoes.previsto_simples, self.contexto["modelo_simples"].predict(self.contexto["teste"]))
        np.testing.assert_allclose(previsoes.previsto_multiplo, self.contexto["modelo_multiplo"].predict(self.contexto["teste"]))

    def test_testes_exportados_usam_hac_no_treino(self):
        arquivo = self.raiz / "resultados/testes_hipoteses.csv"
        self.assertTrue(arquivo.exists(), "Tabela de testes ausente")
        tabela = pd.read_csv(arquivo).set_index("variavel")
        esperado = smf.ols("cnt ~ temp + workingday + C(mnth) + t_anos", data=self.contexto["treino"]).fit(
            cov_type="HAC", cov_kwds={"maxlags": 7, "use_correction": True}, use_t=True
        )
        self.assertEqual(set(tabela.index), {"temp", "workingday"})
        for variavel, linha in tabela.iterrows():
            self.assertAlmostEqual(linha.estimativa, esperado.params[variavel])
            self.assertAlmostEqual(linha.p_valor, esperado.pvalues[variavel])
            np.testing.assert_allclose([linha.ic_inferior, linha.ic_superior], esperado.conf_int().loc[variavel])
            self.assertEqual(linha.graus_liberdade, 532)
            self.assertEqual(linha.dias, 547)


if __name__ == "__main__":
    unittest.main()
