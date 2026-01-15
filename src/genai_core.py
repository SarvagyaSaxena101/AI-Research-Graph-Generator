# src/genai_core.py
import time
import os
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv() # Call load_dotenv() here to ensure variables are loaded

# For Langchain integration
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Set OPENAI_API_KEY for compatibility with underlying openai client
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")

# Initialize the LLM (OpenRouter with Llama 3.1 8B Instruct)
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), # Explicitly pass the API key
    base_url="https://openrouter.ai/api/v1", # Use base_url for non-OpenAI endpoints
    model_name="nvidia/nemotron-3-nano-30b-a3b:free",
    temperature=0.6
)

# Initialize Embeddings model via OpenRouter
embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="openai/text-embedding-3-small", # A valid and common embedding model on OpenRouter
)

# --- GRAPH EXTRACTION ---

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

# Use PydanticOutputParser for better type safety and error handling
graph_parser = PydanticOutputParser(pydantic_object=Extraction)

# Define the prompt for entity and relation extraction
graph_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert at extracting entities and relations from scientific texts.
         Extract all relevant entities and their types, and relationships between them and their types.
         Be comprehensive. For every relation you extract, ensure that both the source and target entities are also present in the extracted entities list.
         Your output MUST be a JSON object.
         Entity types should be chosen from: Person, Organization, Concept, Method, Field.
         Relation types should be chosen from: DISCUSSES, USES, CONTAINS, RELATED_TO, DEVELOPS, INVESTIGATES, FINDS, INTRODUCES, PROPOSES, COMPARES_TO, PART_OF, APPLIES_TO, AUTHORED_BY, AFFILIATED_WITH.
         
         Format your output as a JSON object with 'entities' and 'relations' keys, following this schema:
         {format_instructions}
         """),
        ("human", "Extract entities and relations from the following text:\n\n{text}"),
    ]
).partial(format_instructions=graph_parser.get_format_instructions())


def process_paper_content(content: str) -> Dict[str, List[Any]]:
    """
    Function to process research paper content using a GenAI model (Langchain)
    to extract entities and relations. It chunks the document, processes each chunk
    with retry logic, and aggregates the results into a single, robustly de-duplicated graph.
    """
    try:
        # 1. Chunking
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        chunks = text_splitter.split_text(content)
        chunks = chunks[:5] # Limit to first 5 chunks

        # 2. Create Vector Store (as requested by user)
        print("Creating vector store from document chunks...")
        vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
        print("Vector store created.")

        # 3. Process chunks and extract graph data
        all_entities = []
        all_relations = []
        
        # Create a chain with retry logic for robustness against parsing errors
        chain = graph_prompt | llm | graph_parser
        chain_with_retry = chain.with_retry(
            stop_after_attempt=3
        )

        print(f"Processing {len(chunks)} chunks for graph extraction...")
        for i, chunk in enumerate(chunks):
            print(f"  - Processing chunk {i+1}/{len(chunks)}")
            try:
                # Invoke the chain with retry
                extracted_chunk_data = chain_with_retry.invoke({"text": chunk})
                
                # The PydanticOutputParser returns a Pydantic 'Extraction' object directly
                if extracted_chunk_data and extracted_chunk_data.entities:
                    all_entities.extend(extracted_chunk_data.entities)
                if extracted_chunk_data and extracted_chunk_data.relations:
                    all_relations.extend(extracted_chunk_data.relations)
            except Exception as e:
                print(f"    - Warning: Could not process chunk {i+1} for graph extraction. Error: {e}")
                # Continue to the next chunk
                continue
        
        print("All chunks processed. De-duplicating results...")
        
        # 4. De-duplicate and merge results robustly
        unique_entities_dict = {e.name: e for e in reversed(all_entities)}
        for r in all_relations:
            if r.source not in unique_entities_dict:
                unique_entities_dict[r.source] = Entity(name=r.source, type='Concept')
            if r.target not in unique_entities_dict:
                unique_entities_dict[r.target] = Entity(name=r.target, type='Concept')
        
        unique_relations = {}
        for r in all_relations:
            relation_key = (r.source, r.target, r.type)
            if r.source in unique_entities_dict and r.target in unique_entities_dict:
                unique_relations[relation_key] = r

        final_entities = [e.dict() for e in unique_entities_dict.values()]
        final_relations = [r.dict() for r in unique_relations.values()]
        
        print("De-duplication complete.")
        return {"entities": final_entities, "relations": final_relations}

    except Exception as e:
        print(f"An unexpected error occurred in process_paper_content: {e}")
        return {
            "entities": [{"name": "Error", "type": "Processing Failed"}],
            "relations": [{"source": "Document Processing", "target": "Error", "type": "ENCOUNTERED"}]
        }

# --- TEXTUAL ANALYSIS GENERATION ---

str_parser = StrOutputParser()

# --- Key Topics and Methodologies ---
key_topics_prompt = ChatPromptTemplate.from_template(
    """You are an expert at analyzing scientific papers. 
    Analyze the following text and identify the most important topics and the key methodologies associated with them.
    Present your findings as a list of topics, each with a brief explanation of its methodology. 
    Use Markdown for formatting, including headers and bullet points.

    Text to analyze:
    {text}
    """
)

def generate_key_topics(content: str) -> str:
    """Generates a summary of key topics and methodologies from the text."""
    try:
        chain = key_topics_prompt | llm | str_parser
        return chain.invoke({"text": content})
    except Exception as e:
        return f"Error generating key topics: {e}"

# --- Hypotheses and Ideas ---
hypotheses_prompt = ChatPromptTemplate.from_template(
    """You are a creative and insightful research assistant. 
    Based on the following research paper, generate a list of novel, testable hypotheses and broader research ideas.
    These could be based on identified gaps, contradictions, or logical next steps from the paper's findings. 
    Frame them as clear, concise points. Use Markdown for formatting, including headers and bullet points.

    Text to analyze:
    {text}
    """
)

def generate_hypotheses(content: str) -> str:
    """Generates novel hypotheses and research ideas from the text."""
    try:
        chain = hypotheses_prompt | llm | str_parser
        return chain.invoke({"text": content})
    except Exception as e:
        return f"Error generating hypotheses: {e}"

# --- Future Work ---
future_work_prompt = ChatPromptTemplate.from_template(
    """You are a critical reviewer of scientific work. 
    Analyze the provided research paper and suggest concrete directions for future work. 
    What are the limitations of the current study? What are the next logical experiments or theoretical developments? 
    Present your answer as a list of suggestions. Use Markdown for formatting, including headers and bullet points.

    Text to analyze:
    {text}
    """
)

def generate_future_work(content: str) -> str:
    """Generates suggestions for future work based on the text."""
    try:
        chain = future_work_prompt | llm | str_parser
        return chain.invoke({"text": content})
    except Exception as e:
        return f"Error generating future work suggestions: {e}"

