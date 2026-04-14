from os import getenv

db_host = getenv("DB_HOST", "localhost")
db_port = getenv("DB_PORT", "5432")
db_user = getenv("DB_USER", "ai")
db_pass = getenv("DB_PASS", "ai")
db_name = getenv("DB_DATABASE", "ai")

db_url = f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
