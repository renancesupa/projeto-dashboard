from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient


def main():
    raiz = Path(__file__).resolve().parents[1]
    arquivo = raiz / "notebooks/analise_bicicletas.ipynb"
    notebook = nbformat.read(arquivo, as_version=4)
    cliente = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(arquivo.parent)}},
        store_widget_state=False,
    )
    gerenciador = cliente.create_kernel_manager()
    gerenciador.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    cliente.execute()
    nbformat.validate(notebook)
    temporario = arquivo.with_suffix(".ipynb.tmp")
    nbformat.write(notebook, temporario)
    temporario.replace(arquivo)
    print(f"Notebook executado: {cliente.code_cells_executed} células de código, sem erros.")
    print(f"Resultados: {raiz / 'resultados'}")


if __name__ == "__main__":
    main()
