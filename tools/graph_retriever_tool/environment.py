import os
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from dotenv import load_dotenv
from agno.utils.log import logger
import nest_asyncio
import os


class Environment():
    def __init__(self):
        load_dotenv()
        nest_asyncio.apply()
        self.graph_store = Neo4jPropertyGraphStore(
        username=os.getenv('NEO4J_USERNAME'),
        password=os.getenv('NEO4J_PASSWORD'),
        url=os.getenv('NEO4J_URL'),
    )
        logger.info(f"username: {os.getenv('NEO4J_USERNAME')}, password: {os.getenv('NEO4J_PASSWORD')}, url: {os.getenv('NEO4J_URL')}")
        
    def get_graph_store(self):

        return self.graph_store

