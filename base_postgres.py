import pandas as pd
from sqlalchemy import create_engine
import json


with open('config.json', 'r') as config_file:
    config = json.load(config_file)


usuario = config['postgres']['usuario']
contraseña = config['postgres']['contrasena']
host = config['postgres']['host']
puerto = config['postgres']['puerto']
db = config['postgres']['db']


# Paso 1: Leer el archivo Excel usando pandas
ruta_archivo = 'C:\\Users\\Mirsha\\Documents\\Proyectos\\scraping_cpa\\base_urls.xlsx'

# Lee el archivo Excel en un DataFrame
df = pd.read_excel(ruta_archivo, sheet_name='Sheet1', engine='openpyxl') 

# Mostrar las primeras filas del DataFrame para verificar la lectura
print(df.head())


# conexión a PostgreSQL
conexion_str = f'postgresql+psycopg2://{usuario}:{contraseña}@{host}:{puerto}/{db}'
motor = create_engine(conexion_str)

# Guardar el DataFrame en PostgreSQL
df.to_sql('tikets', motor, if_exists='replace', index=False)  # Cambiar 'replace' por 'append' si quieres agregar los datos a una tabla existente

