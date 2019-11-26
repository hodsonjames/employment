import sys
import papermill as pm
import nbformat
from nbconvert.exporters import PDFExporter


pm.execute_notebook(
        "Summary Statistics.ipynb",
        sys.argv[1] + ".ipynb",
        parameters=dict(employment_data = sys.argv[2],
			by_year_data = sys.argv[3]),
        report_mode=True,
    )
notebook_filename = sys.argv[1] + ".ipynb"

with open(notebook_filename) as f:
    nb = nbformat.read(f, as_version=4)
pdf_exporter = PDFExporter()
pdf_exporter.exclude_input = True
pdf_data, resources = pdf_exporter.from_notebook_node(nb)

with open(sys.argv[1] + ".pdf", "wb") as f:
    f.write(pdf_data)
    f.close()
