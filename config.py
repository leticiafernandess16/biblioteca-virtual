import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "biblioteca.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "database", "seed.sql")
SECRET_KEY = "troque-esta-chave-em-producao"
DIAS_EMPRESTIMO = 14
DEMO_PATH = os.path.join(BASE_DIR, "database", "demo.sql")
