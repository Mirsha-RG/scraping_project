import base64
import os
import json
import psycopg2

# Leer el archivo de configuración JSON
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Extraer los datos necesarios del archivo de configuración
login_url = config['login']['login_url']
username = config['login']['username']
password = config['login']['password']
db_config = config['postgres']
primary_key = config['data_columns']['primary_key']
table_name = config['data_columns']['table_name']
url_column = config['data_columns']['url_column']
image_base64_column = config['data_columns']['image_base64_column']

# Pedir al usuario que ingrese el valor de la clave primaria que desea buscar
primary_key_value = input(f"Ingrese el numero de Record ({primary_key}) que desea buscar: ")

# Configurar la conexión a PostgreSQL
connection = psycopg2.connect(
    user=db_config['usuario'],
    password=db_config['contrasena'],
    host=db_config['host'],
    port=db_config['puerto'],
    database=db_config['db']
)

cursor = connection.cursor()

# Ejecutar la consulta para obtener el ticket id y las imágenes en base64 para el valor ingresado
cursor.execute(f'SELECT "{primary_key}", "{image_base64_column}" FROM "{table_name}" WHERE "{primary_key}" = %s', (primary_key_value,))
rows = cursor.fetchall()

# Cerrar la conexión a la base de datos
cursor.close()
connection.close()

# Crear carpeta para guardar las imágenes
folder_name = primary_key_value  # Cambia este nombre según sea necesario
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"Carpeta creada: {folder_name}")
else:
    print(f"Carpeta ya existe: {folder_name}")

# Convertir cada imagen de Base64 a JPG y guardarla en la carpeta
for row in rows:
    ticket_id = row[0]
    image_base64 = row[1]
    
    if image_base64:  # Verifica si image_base64 no es None
        # Convertir el base64 a binario
        image_data = base64.b64decode(image_base64)
        
        # Definir la ruta de salida para cada imagen
        image_path = os.path.join(folder_name, f'{ticket_id}.jpg')
        
        # Guardar la imagen en formato JPG
        with open(image_path, 'wb') as file:
            file.write(image_data)
    else:
        print(f"No se encontró imagen para el ticket ID: {ticket_id}")

print("Imágenes convertidas y guardadas correctamente.")
