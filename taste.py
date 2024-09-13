from playwright.sync_api import sync_playwright
import time
import os
import json
import base64
import psycopg2  

# Cargar la configuración del archivo JSON
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

login_url = config['login']['login_url']
username = config['login']['username']
password = config['login']['password']
db_config = config['postgres']
primary_key = config['data_columns']['primary_key']
table_name = config['data_columns']['table_name']
url_column = config['data_columns']['url_column']
image_base64_column = config['data_columns']['image_base64_column']

# Conectar a la base de datos
def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=db_config['host'],
            port=db_config['puerto'],
            user=db_config['usuario'],
            password=db_config['contrasena'],
            dbname=db_config['db']
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Guardar la imagen en la base de datos
def save_image_to_db(connection, ticket_id, image_base64):
    try:
        with connection.cursor() as cursor:
            print(f"Guardando la imagen en la base de datos para el ticket ID: {ticket_id}")
            print(f"Contenido en Base64 a guardar: {image_base64[:100]}...")  # Imprime los primeros 100 caracteres para verificar

            cursor.execute(
                f'UPDATE "{table_name}" SET "{image_base64_column}" = %s WHERE "{primary_key}" = %s',
                (image_base64, ticket_id)
            )
            connection.commit()
            print(f"Imagen guardada en la base de datos para el ticket ID: {ticket_id}")
    except Exception as e:
        print(f"Error al guardar la imagen en la base de datos: {e}")
        connection.rollback()

# Obtener las URLs desde la base de datos
def get_urls_from_db(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT "{primary_key}", "{url_column}" FROM "{table_name}" WHERE "{primary_key}" IS NOT NULL')
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener URLs de la base de datos: {e}")
        return []

# Almacenar imágenes en una lista
imagenes_por_ticket = []

# Proceso de scraping y conversión de imágenes
def process_url(connection, ticket_id, url):  # Pasar la conexión como argumento
    try:
        print(f"Procesando la URL: {url}")
        
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

            # Verificar si el botón "No permanecer conectado" existe y es visible
            try:
                if page.query_selector('input[id="idBtn_Back"]'):
                    page.click('input[id="idBtn_Back"]')
                    print("Botón 'No permanecer conectado' fue encontrado y clicado.")
                else:
                    print("El botón 'No permanecer conectado' no está presente.")
            except Exception as e:
                print(f"Error al intentar encontrar o clicar el botón 'No permanecer conectado': {e}")

            # Navegar a la URL de extracción de datos
            page.goto(url)

            # Esperar hasta que la red esté inactiva
            page.wait_for_load_state('networkidle')

            # Verificar si los elementos están en un iframe
            iframes = page.frames
            found = False

            for frame in iframes:
                record_no_element = frame.query_selector('input[id="oj-collapsible-2-contentrecord_no\\|input"]')
                
                if record_no_element:
                    print("Elementos encontrados en un iframe.")
                    found = True
                    break

            if found:
                # Inicializar la lista para almacenar imágenes
                imagenes_por_ticket.clear()  # Limpiar la lista antes de almacenar nuevas imágenes

                # Hacer scroll en la página para cargar más elementos e imágenes
                frame.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)  # Esperar para que se carguen las imágenes al hacer scroll

                # Extraer imágenes
                image_elements = frame.query_selector_all('img')
                for img in image_elements:
                    try:
                        # Convertir imagen a Base64
                        img_data = img.screenshot()
                        image_base64 = base64.b64encode(img_data).decode('utf-8')
                        imagenes_por_ticket.append((ticket_id, image_base64))  # Guardar imagen en la lista
                        print(f"Imagen capturada y guardada en lista para el ticket ID: {ticket_id}")

                    except Exception as e:
                        print(f"Error al convertir o guardar la imagen en Base64: {e}")

                # Guardar todas las imágenes en la base de datos
                for ticket_id, image_base64 in imagenes_por_ticket:
                    save_image_to_db(connection, ticket_id, image_base64)

                print(f"Todas las imágenes se han procesado para el ticket ID: {ticket_id}.")
            
            else:
                print("Uno o más elementos no fueron encontrados en el DOM.")

            # Cerrar el navegador
            browser.close()

    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")

# Ejecutar el proceso de scraping periódicamente
def main():
    connection = connect_to_db()
    if not connection:
        return

    while True:
        urls = get_urls_from_db(connection)
        if urls:
            for ticket_id, url in urls:
                process_url(connection, ticket_id, url)  # Pasar la conexión a la función
        else:
            print("No se encontraron URLs para procesar.")

        # Esperar 5 minutos antes de la siguiente verificación
        time.sleep(30000)

# Llamada a la función principal
main()

