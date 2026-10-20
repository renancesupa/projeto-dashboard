from html.parser import HTMLParser
from pathlib import Path
import unittest

import nbformat
import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]


class LinhasHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.linhas = []
        self.linha = None
        self.celula = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.linha = []
        if tag in ("td", "th"):
            self.celula = ""

    def handle_data(self, texto):
        if self.celula is not None:
            self.celula += texto

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.linha is not None:
            self.linha.append(self.celula.strip())
            self.celula = None
        if tag == "tr" and self.linha is not None:
            self.linhas.append(self.linha)
            self.linha = None


class ApresentacaoNotebookTest(unittest.TestCase):
    def test_tabela_preserva_valores_p_positivos_pequenos(self):
        notebook = nbformat.read(RAIZ / "notebooks/analise_bicicletas.ipynb", as_version=4)
        celula = next(c for c in notebook.cells if c.cell_type == "code" and "linhas_testes = []" in c.source)
        html = next(o.data["text/html"] for o in celula.outputs if "text/html" in o.get("data", {}))
        parser = LinhasHTML()
        parser.feed(html)
        cabecalho, *linhas = parser.linhas
        coluna_variavel = cabecalho.index("variavel")
        coluna_p = cabecalho.index("p_valor")
        valores = pd.read_csv(RAIZ / "resultados/testes_hipoteses.csv").set_index("variavel")
        for linha in linhas:
            variavel = linha[coluna_variavel]
            exibido = float(linha[coluna_p])
            original = valores.loc[variavel, "p_valor"]
            with self.subTest(variavel=variavel):
                self.assertGreater(exibido, 0, "O arredondamento não pode transformar valor-p positivo em zero")
                self.assertAlmostEqual(exibido / original, 1, delta=0.001)


if __name__ == "__main__":
    unittest.main()
