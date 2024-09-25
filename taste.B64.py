from playwright.sync_api import sync_playwright
import time
import os
import json
import base64
import psycopg2

# Leer el archivo de configuración
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

login_url = config['login']['login_url']
username = config['login']['username']
password = config['login']['password']

# Configuración de la base de datos
db_config = config['postgres']
db_connection = psycopg2.connect(
    host=db_config['host'],
    database=db_config['db'],
    user=db_config['usuario'],
    password=db_config['contrasena'],
    port=db_config['puerto']
)

# Función para guardar imágenes en formato Base64 en la base de datos
def save_images_to_db(record_no, folder_name):
    """
    Esta función convierte las imágenes de una carpeta en formato Base64
    y las inserta en la columna correspondiente en la base de datos.
    """
    try:
        # Convertir las imágenes a Base64 y concatenarlas
        images_base64 = []
        for image_file in os.listdir(folder_name):
            image_path = os.path.join(folder_name, image_file)
            with open(image_path, "rb") as img_file:
                images_base64.append(base64.b64encode(img_file.read()).decode('utf-8'))

        # Unir todas las imágenes en un solo string, separadas por ;
        images_base64_str = ";".join(images_base64)

        # Insertar los datos en la base de datos
        cursor = db_connection.cursor()
        insert_query = f"""
        INSERT INTO "{config['imagenesB64']['table_name']}" ("{config['imagenesB64']['Record']}", "{config['imagenesB64']['imagen']}")
        VALUES (%s, %s)
        ON CONFLICT ("{config['imagenesB64']['Record']}") DO UPDATE
        SET "{config['imagenesB64']['imagen']}" = EXCLUDED."{config['imagenesB64']['imagen']}";
        """
        cursor.execute(insert_query, (record_no, images_base64_str))
        db_connection.commit()
        cursor.close()
        print(f"Imágenes guardadas en la base de datos para el Record No.: {record_no}")
    except Exception as e:
        print(f"Error al guardar las imágenes en la base de datos: {e}")

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

            # Intentar hacer clic en el botón 'Siguiente'
            try:
                print("Esperando el botón 'Siguiente'...")
                page.wait_for_selector('input[id="idSubmit_ProofUp_Redirect"]', timeout=10000)
                
                if page.is_visible('input[id="idSubmit_ProofUp_Redirect"]'):
                    print("Botón 'Siguiente' visible, intentando hacer clic...")
                    for _ in range(3):
                        page.click('input[id="idSubmit_ProofUp_Redirect"]', force=True)
                        time.sleep(1)
                    print("Clic en el botón 'Siguiente' realizado.")
                else:
                    print("El botón 'Siguiente' no está visible.")
            except Exception as e:
                print(f"Error al intentar encontrar o clicar el botón 'Siguiente': {e}")

            # Esperar el enlace 'Omitir configuración' y hacer clic
            try:
                print("Esperando el enlace 'Omitir configuración'...")
                page.wait_for_selector('a.L0g5CbGcDigQv3yxT1b_', timeout=5000)
                page.click('a.L0g5CbGcDigQv3yxT1b_')
                print("Clic en el enlace 'Omitir configuración' realizado.")
            except Exception as e:
                print(f"Error al intentar encontrar o clicar el enlace 'Omitir configuración': {e}")

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
                            time.sleep(2)
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
                time.sleep(2)

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

                # Llamar a la función para guardar las imágenes en la base de datos
                save_images_to_db(record_no, folder_name)

                print(f"Todas las imágenes se guardaron con éxito en la carpeta {folder_name}.")
            
            else:
                print("Uno o más elementos no fueron encontrados en el DOM.")

            # Cerrar el navegador
            browser.close()

    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")

# Llamada a la función principal
extract_data()
