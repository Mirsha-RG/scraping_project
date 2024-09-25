import pandas as pd
from sqlalchemy import create_engine
import json
from sqlalchemy.types import Text

# Cargar configuración del archivo JSON
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

usuario = config['postgres']['usuario']
contraseña = config['postgres']['contrasena']
host = config['postgres']['host']
puerto = config['postgres']['puerto']
db = config['postgres']['db']

# Leer el archivo Excel usando pandas
ruta_archivo = 'C:\\Users\\Mirsha\\Documents\\Proyectos\\scraping_cpa\\base_urls.xlsx'

# Lee el archivo Excel en un DataFrame
df = pd.read_excel(ruta_archivo, sheet_name='Sheet1', engine='openpyxl')

# Manejar valores nulos y convertir todo a cadena
df['Business Process Record URL'] = df['Business Process Record URL'].fillna('').astype(str)

# Verificar la longitud de las URLs para asegurarse de que no estén truncadas
print(df['Business Process Record URL'].apply(len).describe())

# Verificar las primeras filas del DataFrame para asegurar que las URLs son correctas
print(df.head())

# Conexión a PostgreSQL
conexion_str = f'postgresql+psycopg2://{usuario}:{contraseña}@{host}:{puerto}/{db}'
motor = create_engine(conexion_str)

# Guardar el DataFrame en PostgreSQL con un tipo de datos específico para la URL
df.to_sql('tickets', motor, if_exists='replace', index=False, dtype={'Business Process Record URL': Text()})
