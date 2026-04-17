from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.pgvector import PgVector, SearchType
from db.url import db_url

DB_ID = "autoscout-db"

def get_postgres_db(table_name: str | None = None, is_knowledge: bool = False) -> PostgresDb:
    if table_name is not None:
        if is_knowledge:
            return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=table_name)
        return PostgresDb(id=DB_ID, db_url=db_url, session_table=table_name)
    return PostgresDb(id=DB_ID, db_url=db_url)

def create_knowledge(name: str, table_name: str) -> Knowledge:
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=SentenceTransformerEmbedder(id="BAAI/bge-m3", dimensions=1024),
        ),
        contents_db=get_postgres_db(table_name=f"{table_name}_contents", is_knowledge=True),
    )
