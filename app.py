import os
import streamlit as st
from src.genai_core import (
    process_paper_content, 
    generate_key_topics, 
    generate_hypotheses, 
    generate_future_work
)
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
        st.header("2. Analysis Results")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Knowledge Graph", "Key Topics & Methods", "Hypotheses & Ideas", "Future Work"])

        with tab1:
            st.subheader("Knowledge Graph")
            with st.spinner("Extracting entities and relations to build the knowledge graph..."):
                extracted_data = process_paper_content(processed_text)
            
            if extracted_data["entities"]:
                # Create a PyVis network
                net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
                
                # Add nodes
                for node in extracted_data["entities"]:
                    node_id = node["name"]
                    node_label = node["name"]
                    node_title = node["type"]
                    node_color = "#FFC300" # Default color

                    if "Person" == node["type"]:
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
                for edge in extracted_data["relations"]:
                    net.add_edge(edge["source"], edge["target"], title=edge["type"], label=edge["type"], width=2)

                # Generate and display the graph
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        html_file = os.path.join(tmpdir, "kg_graph.html")
                        net.save_graph(html_file)
                        with open(html_file, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        components.html(html_content, height=760)
                except Exception as e:
                    st.error(f"Error generating graph visualization: {e}")
            else:
                st.warning("Could not extract any entities or relations to build the graph.")
        
        with tab2:
            st.subheader("Key Topics and Methodologies")
            with st.spinner("Generating summary of key topics and methodologies..."):
                key_topics_md = generate_key_topics(processed_text)
            st.markdown(key_topics_md)
            
        with tab3:
            st.subheader("Generated Hypotheses and Research Ideas")
            with st.spinner("Generating novel hypotheses and research ideas..."):
                hypotheses_md = generate_hypotheses(processed_text)
            st.markdown(hypotheses_md)

        with tab4:
            st.subheader("Suggested Future Work")
            with st.spinner("Generating suggestions for future work..."):
                future_work_md = generate_future_work(processed_text)
            st.markdown(future_work_md)

    else:
        st.warning("Please upload a PDF or paste some research paper content to process.")

st.sidebar.header("About")
st.sidebar.info(
    "This is a prototype for the AI Research Graph Project. "
    "More features will be added iteratively."
)


