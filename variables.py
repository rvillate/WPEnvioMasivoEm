import os
import sys

from actions_excel import load_excel_data_to_memory

# Base de la ruta del proyecto (raíz donde está este .py)
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


def ruta_excel_base():
    return BASE_DIR + "\\data\\" + "Base.xlsx"


def inicializar_variables():
    load_excel_data_to_memory(ruta_excel_base(), "Base Inicial", "ExcelBase1")
    load_excel_data_to_memory(ruta_excel_base(), "Plantillas", "Plantillas")
    print("")
