# src/genai_core.py
import time
import os
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv() # Call load_dotenv() here to ensure variables are loaded

# For Langchain integration
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field # Corrected import

# For Neo4j integration
from src.sqlite_graph_utils import SQLiteGraphConnector

# Set OPENAI_API_KEY for compatibility with underlying openai client
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")

# Initialize the LLM (OpenRouter with Llama 3.1 8B Instruct)
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), # Explicitly pass the API key
    base_url="https://openrouter.ai/api/v1", # Use base_url for non-OpenAI endpoints
    model_name="meta-llama/llama-3.1-8b-instruct",
    temperature=0
)

# Define output schema for Langchain
class Entity(BaseModel):
    name: str = Field(description="Name of the entity")
    type: str = Field(description="Type of the entity (e.g., Person, Organization, Concept, Method, Field)")

class Relation(BaseModel):
    source: str = Field(description="Name of the source entity")
    target: str = Field(description="Name of the target entity")
    type: str = Field(description="Type of the relationship (e.g., DISCUSSES, USES, CONTAINS, RELATED_TO)")

class Extraction(BaseModel):
    entities: List[Entity] = Field(description="List of extracted entities")
    relations: List[Relation] = Field(description="List of extracted relations")

parser = JsonOutputParser(pydantic_object=Extraction)

# Define the prompt for entity and relation extraction
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert at extracting entities and relations from scientific texts.
         Extract all relevant entities and their types, and relationships between them and their types.
         Entity types should be chosen from: Person, Organization, Concept, Method, Field.
         Relation types should be chosen from: DISCUSSES, USES, CONTAINS, RELATED_TO, DEVELOPS, INVESTIGATES, FINDS.
         
         Format your output as a JSON object with 'entities' and 'relations' keys, following this schema:
         {format_instructions}
         """),
        ("human", "Extract entities and relations from the following text:\n\n{text}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Initialize Neo4j Connector
graph_connector = SQLiteGraphConnector(db_path=os.getenv("GRAPH_DATABASE_PATH", "graph.db"))

def process_paper_content(content: str) -> Dict[str, List[Any]]:
    """
    Function to process research paper content using a GenAI model (Langchain)
    to extract entities and relations, and then store them in SQLite.
    """
    extracted_data = {"entities": [], "relations": []}
    try:
        # Create a chain with the LLM and the parser
        chain = prompt | llm | parser
        
        # Invoke the chain with the paper content
        extracted_data_pydantic = chain.invoke({"text": content})
        
        # Convert Pydantic objects to dictionaries for easier handling in Streamlit and Neo4j
        extracted_data["entities"] = [e.dict() for e in extracted_data_pydantic['entities']]
        extracted_data["relations"] = [r.dict() for r in extracted_data_pydantic['relations']]

        # Store in SQLite
        if graph_connector.conn: # Only proceed if SQLite connection is active
            for entity in extracted_data["entities"]:
                graph_connector.get_or_create_node(name=entity["name"], node_type=entity["type"])
            
            for relation in extracted_data["relations"]:
                source_entity = next((e for e in extracted_data["entities"] if e["name"] == relation["source"]), None)
                target_entity = next((e for e in extracted_data["entities"] if e["name"] == relation["target"]), None)

                if source_entity and target_entity:
                    graph_connector.create_relationship(
                        source_name=source_entity["name"],
                        source_type=source_entity["type"],
                        target_name=target_entity["name"],
                        target_type=target_entity["type"],
                        relationship_type=relation["type"]
                    )
                else:
                    print(f"Warning: Could not find source or target entity types for relation: {relation}")
        else:
            print("SQLite is not connected. Skipping graph storage.")

        return extracted_data

    except Exception as e:
        print(f"Error during GenAI or Neo4j processing: {e}")
        # Return dummy data or an error message if LLM or Neo4j call fails
        return {
            "entities": [{"name": "Error", "type": "Problem"}],
            "relations": [{"source": "GenAI Process", "target": "Error", "type": "CAUSED_BY"}]
        }

