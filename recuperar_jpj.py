import psycopg2
import os
import base64

# Cargar la configuración desde el archivo config.json
import json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Configuración de PostgreSQL
db_config = config['postgres']

# Establecer conexión con la base de datos
connection = psycopg2.connect(
    user=db_config['usuario'],
    password=db_config['contrasena'],
    host=db_config['host'],
    port=db_config['puerto'],
    database=db_config['db']
)

cursor = connection.cursor()

# Consulta para obtener los registros de la tabla ImagenesB64
select_query = f"""
SELECT "{config['imagenesB64']['Record']}", "{config['imagenesB64']['imagen']}"
FROM "{config['imagenesB64']['table_name']}";
"""

cursor.execute(select_query)
records = cursor.fetchall()

# Crear una carpeta para guardar las imágenes
output_folder = "imagenes_extraidas"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Recorrer los registros y guardar las imágenes
for record in records:
    record_no = record[0]
    base64_images = record[1].split(";")  # Si las imágenes están separadas por ";"

    # Crear una subcarpeta para cada Record
    record_folder = os.path.join(output_folder, f"Record_{record_no}")
    if not os.path.exists(record_folder):
        os.makedirs(record_folder)

    # Convertir y guardar cada imagen
    for index, base64_image in enumerate(base64_images):
        image_data = base64.b64decode(base64_image)  # Convertir de Base64 a bytes
        image_path = os.path.join(record_folder, f"imagen_{index + 1}.jpg")

        with open(image_path, 'wb') as image_file:
            image_file.write(image_data)

        print(f"Imagen guardada: {image_path}")

# Cerrar la conexión a la base de datos
cursor.close()
connection.close()

print("Proceso completado.")
