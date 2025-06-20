import re
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def type_in_input_by_placeholder(driver, text, placeholder, send_enter = False, timeout=10):
    """
    Escribe texto en un campo editable localizado por su aria-placeholder, con resaltado previo.

    Parámetros:
        - driver: instancia del navegador
        - text: texto a escribir
        - placeholder: valor exacto del atributo aria-placeholder
        - timeout: tiempo máximo de espera (segundos), por defecto 10

    Retorna:
        - msg: mensaje de estado
        - estado: True si fue exitoso, False si hubo error
    """
    try:
        # Esperar a que aparezca el campo editable con el placeholder indicado
        input_box = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//div[@contenteditable="true" and @aria-placeholder="{placeholder}"]')
            )
        )

        # Resaltar el campo con borde rojo
        driver.execute_script("arguments[0].style.border='2px solid red';", input_box)
        time.sleep(0.4)
        driver.execute_script("arguments[0].style.border='';", input_box)

        # Escribir el texto
        input_box.click()
        input_box.send_keys(Keys.CONTROL, 'a')
        input_box.send_keys(Keys.BACKSPACE)
        input_box.send_keys(text)

        if send_enter:
            input_box.send_keys(Keys.RETURN)

        return (f'Text "{text}" successfully entered into field with placeholder "{placeholder}".', True)

    except Exception as e:
        return (f'Error while typing in field with placeholder "{placeholder}": {e}', False)

def type_in_input_by_placeholder2(driver, text, placeholder, send_enter=False, timeout=10):
    """
    Escribe texto en un campo contenteditable usando aria-placeholder, compatible con Lexical (Meta/Facebook).

    :param driver: instancia del navegador
    :param text: texto a escribir
    :param placeholder: aria-placeholder del campo
    :param send_enter: si True, envía Enter al final
    :param timeout: espera máxima
    :return: (msg, estado)
    """
    try:
        input_box = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[@contenteditable="true" and @aria-placeholder="{placeholder}"]'))
        )

        # Resaltar para depurar
        driver.execute_script("arguments[0].style.border='2px solid red';", input_box)
        time.sleep(0.4)
        driver.execute_script("arguments[0].style.border='';", input_box)

        # Clic para enfocar
        input_box.click()
        time.sleep(0.2)

        # Simular escritura con ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(input_box)
        actions.click()
        actions.send_keys(text)
        if send_enter:
            actions.send_keys(Keys.RETURN)
        actions.perform()

        return (f'Texto "{text}" escrito correctamente en campo con placeholder "{placeholder}".', True)

    except Exception as e:
        return (f'Error escribiendo en el campo con placeholder "{placeholder}": {e}', False)

def click_button_by_aria_label(driver, label, timeout=10):
    """
    Da clic en un botón usando su aria-label, lo resalta antes de hacer clic.

    Parámetros:
        - driver: instancia del navegador
        - label: texto del atributo aria-label a buscar
        - timeout: tiempo máximo de espera (segundos), por defecto 10

    Retorna:
        - msg: mensaje de estado
        - estado: True si fue exitoso, False si hubo error
    """
    try:
        # Esperar a que el botón esté presente
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f'//button[@aria-label="{label}"]'))
        )

        # Aplicar borde rojo durante 0.4 segundos
        driver.execute_script(
            "arguments[0].style.border='3px solid red';", button
        )
        time.sleep(0.4)
        driver.execute_script(
            "arguments[0].style.border='';", button
        )

        # Hacer clic
        button.click()
        return (f'Button with aria-label "{label}" clicked successfully.', True)

    except Exception as e:
        return (f'Error clicking button with aria-label "{label}": {e}', False)



def click_element_by_title(driver, title, timeout=10):
    """
    Da clic en un elemento con un título específico, asegurándose de que esté actualizado en el DOM.
    """
    try:
        # Esperar que aparezca el elemento
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f'//*[@title="{title}"]'))
        )

        # Obtener el elemento justo antes del clic
        element = driver.find_element(By.XPATH, f'//*[@title="{title}"]')

        # Resaltar el elemento
        driver.execute_script("arguments[0].style.border='3px solid red';", element)
        time.sleep(0.4)
        driver.execute_script("arguments[0].style.border='';", element)

        # Hacer clic
        element.click()

        return (f'✅ Click en el elemento con title="{title}".', True)

    except Exception as e:
        return (f'❌ Error al hacer clic en title="{title}": {e}', False)

def click_contact_by_internal_text_match(driver, match_text, normalize_spaces=True, timeout=10):
    """
    Recorre todos los botones de contacto y da clic al primero que contenga el texto buscado.

    Parámetros:
        - driver: instancia de Selenium
        - match_text: texto que debe coincidir con algún span dentro del botón
        - normalize_spaces: si True, elimina todos los espacios (incluso unicode)
        - timeout: tiempo máximo de espera

    Retorna:
        - msg: mensaje descriptivo
        - estado: True si fue exitoso, False si falló
    """
    try:
        # Esperar a que haya botones disponibles
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@role="button"]'))
        )

        # Obtener todos los divs clickeables
        buttons = driver.find_elements(By.XPATH, '//div[@role="button"]')

        if normalize_spaces:
            match_text_cmp = re.sub(r'\s+', '', match_text)
        else:
            match_text_cmp = match_text

        for i, button in enumerate(buttons):
            spans = button.find_elements(By.XPATH, './/span')
            for span in spans:
                span_text = span.text
                span_cmp = re.sub(r'\s+', '', span_text) if normalize_spaces else span_text

                if match_text_cmp in span_cmp:
                    # Resaltar
                    driver.execute_script("arguments[0].style.border='3px solid red';", button)
                    time.sleep(0.4)
                    driver.execute_script("arguments[0].style.border='';", button)

                    # Click
                    button.click()
                    return (f'Contact "{span_text}" clicked successfully.', True)

        return (f'Text "{match_text}" not found in any button.', False)

    except Exception as e:
        return (f'Error searching contacts: {e}', False)

def find_number_span_match(driver, input_number, normalize_spaces=True, timeout=10):
    """
    Busca un <span> que contenga el número telefónico exacto (con o sin espacios) y lo retorna.

    Parámetros:
        - driver: instancia Selenium
        - input_number: número a buscar (ej. "+5219141205998")
        - normalize_spaces: True para ignorar espacios, False para comparar exacto
        - timeout: tiempo máximo de espera (default 10)

    Retorna:
        - (msg, estado, elemento) ← si se encuentra, devuelve el <span> como tercer valor
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "selectable-text") and contains(@class, "copyable-text")]'))
        )

        spans = driver.find_elements(By.XPATH, '//span[contains(@class, "selectable-text") and contains(@class, "copyable-text")]')

        input_cmp = re.sub(r'\s+', '', input_number) if normalize_spaces else input_number

        for span in spans:
            span_text = span.text
            span_cmp = re.sub(r'\s+', '', span_text) if normalize_spaces else span_text

            if input_cmp == span_cmp:
                return (f'Number "{input_number}" matched span "{span_text}".', True, span)

        return (f'Number "{input_number}" not found in any span.', False, None)

    except Exception as e:
        return (f'Error searching for number span: {e}', False, None)

def find_number_span_match2(driver, input_number, normalize_spaces=True, timeout=10):
    """
    Busca un <span> con el número exacto.

    Parámetros:
        - driver: Selenium WebDriver
        - input_number: número a buscar (ej. "+52 1 872 124 6573")
        - normalize_spaces: si True, ignora espacios en comparación
        - timeout: espera máxima

    Retorna:
        - (mensaje, estado, elemento encontrado o None)
    """
    try:
        xpath = '//span[contains(@class, "selectable-text") and contains(@class, "copyable-text")]'
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )

        spans = driver.find_elements(By.XPATH, xpath)
        input_cmp = re.sub(r'\s+', '', input_number) if normalize_spaces else input_number

        print(f"🔍 Buscando número normalizado: {input_cmp}")
        encontrados = []

        for span in spans:
            span_text = span.text.strip()
            span_cmp = re.sub(r'\s+', '', span_text) if normalize_spaces else span_text

            if span_cmp:
                print(f"👁️ Revisando: '{span_text}' → normalizado: '{span_cmp}'")
                encontrados.append(span_cmp)

            if input_cmp == span_cmp:
                print(f"✅ Coincidencia encontrada: {span_text}")
                return (f'Número "{input_number}" encontrado como "{span_text}"', True, span)

        print(f"❌ Número no encontrado. Vistos: {encontrados}")
        return (f'Número "{input_number}" no se encontró.', False, None)

    except Exception as e:
        return (f'❌ Error buscando el número: {e}', False, None)

def click_first_contact_after_header(driver, timeout=10):
    """
    Busca el encabezado 'Contactos en WhatsApp' y hace clic en el primer contacto que le sigue.

    Parámetros:
        - driver: instancia de Selenium WebDriver
        - timeout: tiempo máximo de espera

    Retorna:
        - msg: mensaje descriptivo del resultado
        - estado: True si fue exitoso, False si hubo error
    """
    try:
        # Esperar a que el encabezado esté presente
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[text()="Usuarios que no están en tus contactos"]'))
        )

        # Obtener todos los elementos con role="listitem"
        items = driver.find_elements(By.XPATH, '//div[@role="listitem"]')

        # Buscar el índice del encabezado
        header_index = -1
        for idx, item in enumerate(items):
            if "Contactos en WhatsApp" in item.text:
                header_index = idx
                break

        if header_index == -1:
            return ("❌ Encabezado 'Contactos en WhatsApp' no encontrado.", False)

        # Verificar que haya un elemento siguiente
        if header_index + 1 >= len(items):
            return ("❌ No hay contacto disponible después del encabezado.", False)

        # Obtener el siguiente y buscar el botón interno
        next_item = items[header_index + 1]
        button = next_item.find_element(By.XPATH, './/div[@role="button"]')

        # Resaltar visualmente y hacer clic
        driver.execute_script("arguments[0].style.border='3px solid green';", button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].style.border='';", button)
        button.click()

        return ("✅ Éxito: Primer contacto después del encabezado clickeado.", True)

    except Exception as e:
        return (f"❌ Error al buscar y hacer clic en el primer contacto: {e}", False)


def click_first_contact_after_header2(driver, timeout=10):
    try:
        print("🔍 Buscando texto 'Usuarios que no están en tus contactos'...")

        # 1. Buscar elemento por texto exacto
        label = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Usuarios que no están en tus contactos"]'))
        )
        print("✅ Texto encontrado.")

        # 2. Subir al primer contenedor padre que tenga un botón dentro
        parent_with_button = label.find_element(
            By.XPATH, './ancestor::div[.//div[@role="button"]][1]'
        )
        print("✅ Contenedor con botón localizado.")

        # 3. Buscar el botón del contacto
        button = parent_with_button.find_element(By.XPATH, './/div[@role="button"]')

        # 4. Hacer scroll hacia el botón
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(0.5)

        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(button))
            button.click()
            print("✅ Click en el botón (directo).")
        except Exception as e:
            print(f"⚠️ Click directo falló, usando JavaScript: {e}")
            driver.execute_script("arguments[0].click();", button)
            print("✅ Click en el botón (JavaScript).")

        return ("✅ Click en contacto exitoso.", True)

    except Exception as e:
        print(f"❌ Error general: {e}")
        return (f"❌ No se pudo hacer clic en el contacto: {e}", False)

def click_button_by_title(driver, title_text, timeout=10):
    """
    Hace clic en un botón buscado por su atributo title.

    :param driver: instancia de Selenium WebDriver
    :param title_text: texto exacto del atributo title (ej. "Adjuntar")
    :param timeout: tiempo máximo de espera en segundos
    :return: (msg, estado) → mensaje y True/False según éxito
    """
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f'//button[@title="{title_text}"]'))
        )

        # Resaltar antes de hacer clic
        driver.execute_script("arguments[0].style.border='2px solid red';", button)
        time.sleep(0.4)
        driver.execute_script("arguments[0].style.border='';", button)

        button.click()

        return (f'Botón con title "{title_text}" clickeado exitosamente.', True)

    except Exception as e:
        return (f'Error al hacer clic en el botón con title "{title_text}": {e}', False)

def click_button_by_inner_text(driver, text, timeout=10, normalize_spaces=True):
    """
    Busca un <button> que contenga el texto visible dado (en él o en cualquier hijo) y le hace clic.

    :param driver: instancia del navegador
    :param text: texto que debe contener el botón (total o parcial)
    :param timeout: segundos máximos de espera
    :param normalize_spaces: si True, elimina espacios antes de comparar
    :return: (msg, estado) → mensaje y éxito booleano
    """
    import re

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, '//button'))
        )

        buttons = driver.find_elements(By.XPATH, '//button')
        text_cmp = re.sub(r'\s+', '', text) if normalize_spaces else text

        for btn in buttons:
            full_text = btn.text
            full_cmp = re.sub(r'\s+', '', full_text) if normalize_spaces else full_text

            if text_cmp in full_cmp:
                # Resaltar
                driver.execute_script("arguments[0].style.border='3px solid green';", btn)
                time.sleep(0.4)
                driver.execute_script("arguments[0].style.border='';", btn)

                btn.click()
                return (f'Botón con texto "{text}" clickeado exitosamente.', True)

        return (f'No se encontró ningún botón con el texto "{text}".', False)

    except Exception as e:
        return (f'Error al buscar/clickeado botón por texto "{text}": {e}', False)

def enviar_imagen(driver, ruta_imagen, timeout=10):
    """
    Adjunta y envía una imagen en el chat activo de WhatsApp Web.

    :param driver: instancia de Selenium WebDriver
    :param ruta_imagen: ruta absoluta del archivo de imagen
    :param timeout: tiempo máximo de espera
    :return: (msg, estado)
    """
    try:
        # 1. Clic en el ícono de clip 📎
        msg, estado = click_button_by_title(driver, "Adjuntar")
        if not estado:
            return (f"Error al presionar el botón adjuntar: {msg}", False)
        time.sleep(0.5)

        # 2. Ubicar el input de tipo file directamente (sin usar click visible)
        input_file = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
        )

        # 3. Enviar ruta del archivo
        input_file.send_keys(ruta_imagen)
        time.sleep(1.5)

        # 4. Clic en el botón de enviar (flecha azul)
        #send_btn = WebDriverWait(driver, timeout).until(
        #    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        #)
        #send_btn.click()

        return ("✅ Imagen enviada correctamente.", True)

    except Exception as e:
        return (f"❌ Error al enviar imagen: {e}", False)


def click_boton_atras(driver, timeout=10):
    """
    Da clic en el botón con aria-label 'Atrás' en WhatsApp Web.

    Parámetros:
        - driver: instancia de Selenium WebDriver
        - timeout: tiempo máximo de espera (default 10 segundos)

    Retorna:
        - (mensaje, True/False)
    """
    try:
        boton_atras = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Atrás"]'))
        )
        boton_atras.click()
        return ("✅ Botón 'Atrás' clickeado con éxito.", True)
    except Exception as e:
        return (f"❌ Error al hacer clic en el botón 'Atrás': {e}", False)


def existe_mensaje_no_resultados(driver, timeout=5):
    """
    Verifica si aparece el mensaje 'No se encontraron resultados para' en WhatsApp Web.

    Parámetros:
        - driver: instancia de Selenium WebDriver
        - timeout: tiempo máximo de espera para encontrar el span (default 5 segundos)

    Retorna:
        - (mensaje, True/False)
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(text(), "No se encontraron resultados para")]')
            )
        )
        return ("🔍 Mensaje 'No se encontraron resultados para' detectado.", True)
    except Exception:
        return ("✅ No se detectó mensaje de 'sin resultados'.", False)