from datetime import date
from pathlib import Path
import shutil
import tempfile
import unittest

from streamlit.testing.v1 import AppTest


RAIZ = Path(__file__).resolve().parents[1]


class DashboardTest(unittest.TestCase):
    def carregar(self):
        arquivo = RAIZ / "dashboard/app.py"
        self.assertTrue(arquivo.exists(), "Dashboard ainda não implementado")
        app = AppTest.from_file(str(arquivo), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_tres_graficos_e_tabelas(self):
        app = self.carregar()
        self.assertEqual(len(app.get("plotly_chart")), 3)
        self.assertEqual(len(app.dataframe), 3)
        self.assertEqual(int(app.dataframe[0].value["dias_observados"].sum()), 731)

    def test_filtros_afetam_descricao_e_preservam_metricas_e_testes(self):
        app = self.carregar()
        metricas = app.dataframe[1].value.copy()
        testes = app.dataframe[2].value.copy()
        app.date_input[0].set_value((date(2011, 1, 1), date(2011, 1, 7)))
        app.multiselect[0].set_value(["Dia útil"]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(int(app.dataframe[0].value["dias_observados"].sum()), 5)
        self.assertTrue(app.dataframe[1].value.equals(metricas))
        self.assertTrue(app.dataframe[2].value.equals(testes))

    def test_selecao_vazia_nao_quebra_resultados_fixos(self):
        app = self.carregar()
        metricas = app.dataframe[1].value.copy()
        app.multiselect[0].set_value([]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertGreater(len(app.info), 0)
        self.assertEqual(len(app.get("plotly_chart")), 1)
        self.assertTrue(app.dataframe[0].value.equals(metricas))

    def test_ausencia_de_arquivos_informa_como_gerar(self):
        arquivo = RAIZ / "dashboard/app.py"
        self.assertTrue(arquivo.exists(), "Dashboard ainda não implementado")
        with tempfile.TemporaryDirectory() as temporario:
            destino = Path(temporario) / "dashboard"
            destino.mkdir()
            shutil.copy(arquivo, destino / "app.py")
            app = AppTest.from_file(str(destino / "app.py"), default_timeout=20).run()
            self.assertEqual(len(app.exception), 0)
            self.assertGreater(len(app.warning), 0)
            self.assertIn("executar_notebook.py", app.warning[0].value)


if __name__ == "__main__":
    unittest.main()
