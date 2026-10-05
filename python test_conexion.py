import os
import sys
import time
from sqlalchemy import create_engine, text, inspect
import pymysql

def get_credentials():
    try:
        import toml
        if os.path.exists('.streamlit/secrets.toml'):
            with open('.streamlit/secrets.toml', 'r') as f:
                config = toml.load(f)
                if 'mysql' in config:
                    return config['mysql']
    except Exception:
        pass

    mysql_config = {
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT', '3306'),
        'DB_NAME': os.getenv('DB_NAME'),
    }

    if all(mysql_config.values()):
        return mysql_config

    print("\nNo se encontraron credenciales. Ingresa manualmente:\n")
    return {
        'DB_USER': input("Usuario MySQL: ").strip(),
        'DB_PASSWORD': input("Contraseña MySQL: ").strip(),
        'DB_HOST': input("Host (ej: localhost o IP): ").strip(),
        'DB_PORT': input("Puerto (default 3306): ").strip() or '3306',
        'DB_NAME': input("Nombre de la base de datos: ").strip(),
    }

def test_conexion_basica(config):
    try:
        conn = pymysql.connect(
            host=config['DB_HOST'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            database=config['DB_NAME'],
            port=int(config['DB_PORT']),
            connect_timeout=10
        )
        print("✅ Conexión básica exitosa")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error de conexión básica: {e}")
        return False

def test_sqlalchemy(config):
    try:
        url = f"mysql+pymysql://{config['DB_USER']}:{config['DB_PASSWORD']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 30, "read_timeout": 120, "write_timeout": 60},
            pool_size=5,
            max_overflow=10
        )
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ SQLAlchemy ok: {row}")
        return True, engine
    except Exception as e:
        print(f"❌ Error SQLAlchemy: {e}")
        return False, None

def main():
    config = get_credentials()
    print(f"\nHost: {config['DB_HOST']}")
    print(f"Puerto: {config['DB_PORT']}")
    print(f"Usuario: {config['DB_USER']}")
    print(f"Base: {config['DB_NAME']}")
    print()

    if not test_conexion_basica(config):
        sys.exit(1)

    ok, engine = test_sqlalchemy(config)
    if not ok or engine is None:
        sys.exit(1)

    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    print(f"Tablas: {tablas[:10]}")

if __name__ == "__main__":
    main()
