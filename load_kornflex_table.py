import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
import snowflake.connector

load_dotenv()

user = os.getenv("SNOWFLAKE_USER")
print(user)

with open("/Users/lilianpires/Desktop/01 - PROJETOS/snowflake_key.p8", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password= None
    )

private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    private_key = private_key_bytes,
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    role=os.getenv("SNOWFLAKE_ROLE"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

movies = ['hp1.csv', 'hp2.csv', 'hp3.csv', 'hp4.csv', 'hp5.csv', 'hp6.csv', 'hp7.csv', 'hp8.csv']


try:
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION();")
    print(f"Conection ok, version: {cursor.fetchone()[0]}")

    for file in movies:
        cursor.execute(f"""COPY INTO hp_project.raw.scripts FROM
        @hp_project.raw.s3_raw_stage/movie_scripts/{file}
            FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' ENCODING = 'ISO-8859-1')""")
        print(f"{file} loaded")
finally:
    cursor.close()
    conn.close()