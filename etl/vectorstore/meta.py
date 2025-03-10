from openai import OpenAI
from sqlalchemy.types import DateTime
from sqlalchemy import Column, MetaData, Table, Integer, Text, create_engine, ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector  
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime



load_dotenv()


class Meta:
    def __init__(self):
        self.meta = MetaData()
        self.file_table = Table("files", self.meta,
            Column("file_id", Integer(), primary_key=True),
            Column("file_name", Text()), 
            Column("created_at", DateTime, server_default=func.now())
        )
        self.chunk_table = Table("chunks", self.meta, 
            Column("chunk_id", Integer(), primary_key=True),
            Column("file_id", Integer(), ForeignKey("files.file_id")),
            Column("page_number", Integer()),
            Column("timestamp", DateTime, server_default=func.now()),
            Column("chunk_text", Text()),
            Column("embedding", Vector(1536))
        )

def main() -> None:
    username = os.getenv("POSTGRE_USERNAME")
    password = os.getenv("POSTGRE_PASSWORD")
    meta = Meta()
    engine = create_engine(
            f'postgresql+psycopg2://{username}:{password}@localhost/agno_knowledge',
            echo = True
        )
    conn = engine.connect()
    result = conn.execute(
        meta.file_table.insert().returning(meta.file_table.c.file_id),
        {"file_name": "some name 3",
         "created_at": datetime.now()
        }
    )
    file_id = result.fetchone()[0]
    print(file_id)
    conn.commit()
    conn.execute(
        meta.chunk_table.insert().returning(meta.chunk_table.c.chunk_id),
        {"file_id": file_id,
         "chunk_text": "test",
         "timestamp": datetime.now(),
         "embedding": [0.0] * 1536
        }
    )
    conn.commit()
    return 
        
async def async_main() -> None: # for testing
    username = os.getenv("POSTGRE_USERNAME")
    password = os.getenv("POSTGRE_PASSWORD")
    meta = Meta()
    engine = create_async_engine(f'postgresql+asyncpg://{username}:{password}@localhost/agno_knowledge', echo=True)
    async with engine.begin() as conn:
        result = await conn.execute(
        meta.file_table.insert().returning(meta.file_table.c.file_id),
        {"file_name": "some name",
         "created_at": datetime.now()
        }
        )
        file_id = result.fetchone()[0]
        print(file_id)
        await conn.execute(
        meta.chunk_table.insert().returning(meta.chunk_table.c.chunk_id),
        {"file_id": file_id,
         "chunk_text": "test",
         "timestamp": datetime.now(),
         "embedding": [0.0] * 1536
        }
    )
    

    

    await engine.dispose()
        
    
        
if __name__ == "__main__":
    #main()
    asyncio.run(async_main())   
    
