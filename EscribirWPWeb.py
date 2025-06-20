from openpyxl.pivot.fields import Boolean
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

from Actions import type_in_input_by_placeholder, click_button_by_aria_label, click_element_by_title, \
    click_contact_by_internal_text_match, find_number_span_match, click_first_contact_after_header, enviar_imagen, \
    type_in_input_by_placeholder2, click_first_contact_after_header2, find_number_span_match2, \
    existe_mensaje_no_resultados, click_boton_atras
from actions_excel import get_excel_cell, update_cell_excel_by_column_name, save_error_to_log
from variables import inicializar_variables, ruta_excel_base

options = Options()

# Chrome oficial
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Perfil limpio exclusivo
options.add_argument("user-data-dir=C:/Users/Raul/AppData/Local/Google/Chrome/User Data/SeleniumProfile")

# Estabilidad
options.add_argument("--remote-debugging-port=9223")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")


def iniciar_busqueda_envio(numero_tel, texto, ruta_imagen_adjuntar, flag = False):
    # msg, estado = type_in_input_by_placeholder(driver, "Homero", "Buscar un chat o iniciar uno nuevo")
    # if estado:
    #    print("✅ Éxito:", msg)
    # else:
    #    print("❌ Fallo:", msg)

    msg, estado = click_button_by_aria_label(driver, "Nuevo chat")
    if estado:
        print("✅ Éxito:", msg)
    else:
        print("❌ Fallo:", msg)
        return msg, estado

    msg, estado = type_in_input_by_placeholder(driver, numero_tel, "Buscar un nombre o número")
    if estado:
        print("✅ Éxito:", msg)
    else:
        print("❌ Fallo:", msg)
        return msg, estado

    time.sleep(1)

    msg, estado = click_first_contact_after_header2(driver, 3)
    if estado:
        print("✅ Éxito:", msg)
    else:
        print("❌ Fallo:", msg)
        return msg, estado

    time.sleep(0.5)

    msg, estado = click_element_by_title(driver, "Detalles del perfil")
    if estado:
        print("✅ Éxito:", msg)
    else:
        print("❌ Fallo:", msg)
        return msg, estado

    msg, estado, span = find_number_span_match2(driver, numero_tel)

    if estado:
        print("✅ Éxito:", msg)
    else:
        print("❌ Fallo:", msg)
        if flag == False:
            iniciar_busqueda_envio(numero_tel.replace("+52", "+521"), texto, ruta_imagen_adjuntar, True)
            return "mensaje enviado", True

    if ruta_imagen_adjuntar != None:
        msg, estado = enviar_imagen(driver, ruta_imagen_adjuntar)
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            return msg, estado

        msg, estado = type_in_input_by_placeholder2(driver, texto, "Añade un comentario", True)
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            return msg, estado


    else:
        msg, estado = type_in_input_by_placeholder(driver, texto, "Escribe un mensaje", True)
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            return msg, estado





    return "mensaje enviado", True


def reemplazar_datos_plantilla(nombre, variable, plantilla):
    if variable == "<<name>>":
        return plantilla.replace(variable, nombre)


if __name__ == "__main__":
    count = 0

    # inicializar variables
    inicializar_variables()

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get("https://web.whatsapp.com/")

    while True:
        count = count + 1
        msg, est, estado = get_excel_cell("ExcelBase1", count, "current status")
        if estado:
            print("✅ Éxito:", msg)
            if estado != "ACTIVO":
                continue
            elif estado == None:
                break
        else:
            print("❌ Fallo:", msg)
            break

        msg, est, numero = get_excel_cell("ExcelBase1", count, "phone_internacional")
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            continue

        msg, est, nombre = get_excel_cell("ExcelBase1", count, "name")
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            continue

        msg, est, plantilla = get_excel_cell("ExcelBase1", count, "Plantilla")
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            continue

        msg, est, ruta_imagen_adjuntar = get_excel_cell("Plantillas", 2, plantilla)
        if estado:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            continue


        msg, est, plantilla_data = get_excel_cell("Plantillas", 1, plantilla)
        if est:
            print("✅ Éxito:", msg)
        else:
            print("❌ Fallo:", msg)
            continue
        plantilla_data = reemplazar_datos_plantilla(nombre, "<<name>>", plantilla_data)

        msg, est = iniciar_busqueda_envio(numero, plantilla_data, ruta_imagen_adjuntar)
        if est:
            print("✅ Éxito:", msg)
            update_cell_excel_by_column_name(ruta_excel_base(), "Base Inicial", "current status", count, "INACTIVO")
            update_cell_excel_by_column_name(ruta_excel_base(), "Base Inicial", "comment", count, f"Mensaje enviado {plantilla}: f{msg}")
            update_cell_excel_by_column_name(ruta_excel_base(), "Base Inicial", "last date update", count, time.time())
            save_error_to_log(f"Fila:{count}:Numero:{numero}:Estado:INACTIVO:comment:Mensaje enviado {plantilla}: f{msg}")
        else:
            print("❌ Fallo:", msg)
            update_cell_excel_by_column_name(ruta_excel_base(), "Base Inicial", "current status", count, "ERROR")
            update_cell_excel_by_column_name(ruta_excel_base(), "Base Inicial", "comment", count,f"Mensaje no enviado {plantilla}: {msg}")
            update_cell_excel_by_column_name(ruta_excel_base(), "Base Inicial", "last date update", count, time.time())
            save_error_to_log(f"Fila:{count}:Numero:{numero}:Estado:ERROR:comment:Mensaje no enviado :{msg}")
            msg, est = existe_mensaje_no_resultados(driver)
            if est:
                print("✅ Éxito:", msg)
                click_boton_atras(driver, 1)
                time.sleep(1)
                continue
            else:
                print("❌ Fallo:", msg)
                driver.get("https://web.whatsapp.com/")
            continue
    input("🔒 Presiona ENTER para cerrar el navegador manualmente...")
