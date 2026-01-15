import os
import streamlit as st
from src.genai_core import process_paper_content


from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import shutil
import io
import PyPDF2

# Initialize empty graph data for visualization
initial_graph_data = {"nodes": [], "relationships": []}

st.set_page_config(page_title="AI Research Graph Project", layout="wide")

st.title("AI Research Graph Project")

st.markdown(
    """
    Welcome to the AI Research Graph Project! This tool aims to assist in the discovery of scientific hypotheses
    by ingesting research papers, building a knowledge graph, identifying gaps and contradictions,
    and generating testable hypotheses.
    """
)

# Text input for research paper content
st.header("1. Ingest Research Paper Content")

uploaded_file = st.file_uploader("Upload a research paper (PDF only)", type=["pdf"])
paper_content = st.text_area(
    "Alternatively, paste your research paper content here:",
    height=300,
    help="Copy and paste the raw text content of a research paper.",
)

processed_text = ""
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(bytes_data))
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            processed_text += page.extract_text() or ""
        st.success(f"Successfully extracted text from {num_pages} pages of the PDF.")
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        processed_text = ""
elif paper_content:
    processed_text = paper_content

if st.button("Process Paper"):
    if processed_text:
        st.subheader("Processing Initiated...")
        st.info("Extracting entities and relations using GenAI...")
        
        extracted_data = process_paper_content(processed_text)
        
        st.subheader("2. Extracted Information")
        if extracted_data.get("entities") or extracted_data.get("relations"):
            st.json(extracted_data)
        else:
            st.warning("No entities or relations were extracted. Check your API key and input text.")
        
        st.subheader("3. Knowledge Graph Visualization")
        if extracted_data["entities"]: # Use extracted_data for visualization
            # Create a PyVis network
            net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
            
            # Add nodes
            for node in extracted_data["entities"]: # Use extracted_data
                node_id = node["name"] # Use name as ID for visualization for extracted entities
                node_label = node["name"]
                node_title = node["type"]
                node_color = "#FFC300" # Default color

                if "Person" == node["type"]: # Use type for coloring
                    node_color = "#DAF7A6"
                elif "Concept" == node["type"]:
                    node_color = "#FF5733"
                elif "Organization" == node["type"]:
                    node_color = "#C70039"
                elif "Method" == node["type"]:
                    node_color = "#900C3F"
                elif "Field" == node["type"]:
                    node_color = "#581845"

                net.add_node(node_id, label=node_label, title=node_title, color=node_color, size=20)
            
            # Add edges
            all_nodes = set(net.get_nodes())
            for edge in extracted_data["relations"]: # Use extracted_data
                source_id = edge["source"] # Use source name
                target_id = edge["target"] # Use target name
                relation_type = edge["type"]

                if source_id not in all_nodes:
                    net.add_node(source_id, label=source_id)
                    all_nodes.add(source_id)
                
                if target_id not in all_nodes:
                    net.add_node(target_id, label=target_id)
                    all_nodes.add(target_id)
                    
                net.add_edge(source_id, target_id, title=relation_type, label=relation_type, width=2)

            # Generate and display the graph
            try:
                # Create a temporary directory
                with tempfile.TemporaryDirectory() as tmpdir:
                    html_file = os.path.join(tmpdir, "kg_graph.html")
                    net.save_graph(html_file)

                    # Read the HTML file and display it
                    with open(html_file, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    components.html(html_content, height=760)
            except Exception as e:
                st.error(f"Error generating graph visualization: {e}")
        else:
            st.info("No graph data available to visualize.")
        
        st.subheader("4. Generated Hypotheses (Placeholder)")
        st.write("Testable hypotheses will be generated here.")
        
    else:
        st.warning("Please paste some research paper content to process.")

st.sidebar.header("About")
st.sidebar.info(
    "This is a prototype for the AI Research Graph Project. "
    "More features will be added iteratively."
)


