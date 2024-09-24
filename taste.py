from playwright.sync_api import sync_playwright
import time
import os
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

login_url = config['login']['login_url']
username = config['login']['username']
password = config['login']['password']

def extract_data():
    try:
        data_page_url = input("Por favor, ingresa la URL de tu ticket: ")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Navegar a la página de inicio de sesión
            page.goto(login_url)

            # Realizar el inicio de sesión
            page.fill('input[name="loginfmt"]', username)
            page.click('input[id="idSIButton9"]')

            # Esperar el campo de contraseña y llenarlo
            page.wait_for_selector('input[name="passwd"]')
            page.fill('input[name="passwd"]', password)
            page.click('input[id="idSIButton9"]')

            # Función para buscar elementos tanto en la página principal como en iframes
            def find_and_click(selector, description, by_text=False):
                try:
                    print(f"Buscando {description}...")
                    if by_text:
                        page.wait_for_selector(f"text={selector}", timeout=30000)  # Esperar hasta 30 segundos
                        element = page.query_selector(f"text={selector}")
                    else:
                        page.wait_for_selector(selector, timeout=30000)  # Esperar hasta 30 segundos
                        element = page.query_selector(selector)

                    if element:
                        print(f"{description} encontrado, intentando hacer clic...")
                        element.click(force=True)  # Forzar clic
                        print(f"Clic en {description} realizado.")
                    else:
                        # Buscar dentro de iframes si no se encuentra en la página principal
                        print(f"{description} no encontrado en la página principal, buscando en iframes...")
                        for frame in page.frames:
                            if by_text:
                                frame_element = frame.query_selector(f"text={selector}")
                            else:
                                frame_element = frame.query_selector(selector)
                                
                            if frame_element:
                                frame_element.click(force=True)
                                print(f"Clic en {description} dentro de iframe realizado.")
                                return True
                    return False
                except Exception as e:
                    print(f"Error al intentar encontrar o clicar en {description}: {e}")
                    return False

            # Intentar hacer clic en el botón 'Siguiente'
            find_and_click('input[id="idSubmit_ProofUp_Redirect"]', "botón 'Siguiente'")

            # Intentar hacer clic en el enlace 'Omitir configuración' usando el texto visible
            find_and_click("Omitir configuración", "enlace 'Omitir configuración'", by_text=True)

            # Verificar si el botón "No permanecer conectado" existe y es visible
            try:
                if page.query_selector('input[id="idBtn_Back"]'):
                    page.click('input[id="idBtn_Back"]')
                    print("Botón 'No permanecer conectado' fue encontrado y clicado.")
                else:
                    print("El botón 'No permanecer conectado' no está presente.")
            except Exception as e:
                print(f"Error al intentar encontrar o clicar el botón 'No permanecer conectado': {e}")

            # Navegar a la URL de extracción de datos ingresada por el usuario
            page.goto(data_page_url)

            # Esperar hasta que la red esté inactiva
            page.wait_for_load_state('networkidle')

            # Verificar si los elementos están en un iframe
            iframes = page.frames
            found = False

            for frame in iframes:
                record_no_element = frame.query_selector('input[id="oj-collapsible-2-contentrecord_no\\|input"]')
                
                if any([record_no_element]):
                    print("Elementos encontrados en un iframe.")
                    found = True
                    break

            if found:
                # Intentar hacer visibles los elementos si están ocultos
                for element in [record_no_element]:
                    if element:
                        try:
                            frame.evaluate("el => el.style.display = 'block';", element)
                            time.sleep(2)  # Esperar un poco para asegurar que el cambio de estilo ha ocurrido
                        except Exception as e:
                            print(f"No se pudo modificar el estilo del elemento: {e}")

                record_no = record_no_element.input_value() if record_no_element and record_no_element.is_visible() else "No Visible"
                
                print(f"Record No.: {record_no}")
             
                # Crear carpeta para guardar las imágenes
                folder_name = f'{record_no}'
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                    print(f"Carpeta creada: {folder_name}")
                else:
                    print(f"Carpeta ya existe: {folder_name}")

                # Hacer scroll en la página para cargar más elementos e imágenes
                frame.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)  # Esperar para que se carguen las imágenes al hacer scroll

                # Extraer imágenes
                image_elements = frame.query_selector_all('img')
                for index, img in enumerate(image_elements):
                    image_name = f"image_{index + 1}.jpg"
                    image_path = os.path.join(folder_name, image_name)
                    try:
                        # Intentar guardar la imagen como archivo
                        img.screenshot(path=image_path)
                        print(f"Imagen guardada en: {image_path}")
                    except Exception as e:
                        print(f"Error al guardar la imagen {image_name}: {e}")

                print(f"Todas las imágenes se guardaron con éxito en la carpeta {folder_name}.")
            
            else:
                print("Uno o más elementos no fueron encontrados en el DOM.")

            # Cerrar el navegador
            browser.close()

    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")

# Llamada a la función principal
extract_data()


