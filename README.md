# 🚀 AI Research Graph Project

**🚀 Deployed Project Link:** 

https://researchgrapher.streamlit.app/


> **Revolutionize Research Discovery with AI-Powered Knowledge Graphs**

Transform the way you explore scientific literature! The AI Research Graph Project is an innovative web application that leverages cutting-edge generative AI to analyze research papers, construct interactive knowledge graphs, and generate novel hypotheses to accelerate scientific discovery.

## 🌟 Key Features

### 📊 **Intelligent Knowledge Graph Construction**
- **Entity Extraction**: Automatically identifies and categorizes key entities (Persons, Organizations, Concepts, Methods, Fields) from research papers
- **Relation Mapping**: Discovers and visualizes relationships between entities using advanced NLP techniques
- **Interactive Visualization**: Explore knowledge graphs with an intuitive, web-based interface powered by PyVis

### 🧠 **AI-Powered Analysis**
- **Key Topics & Methodologies**: Summarizes core research themes and analytical approaches
- **Hypothesis Generation**: Creates novel, testable research hypotheses based on paper content
- **Future Work Suggestions**: Identifies research gaps and proposes next steps for scientific advancement

### 📄 **Flexible Input Options**
- **PDF Upload**: Seamlessly process research papers in PDF format
- **Text Input**: Paste raw text content for instant analysis
- **Batch Processing**: Handle multiple documents with efficient chunking and vector storage

### 🔧 **Robust Architecture**
- **LangChain Integration**: Utilizes state-of-the-art language models via OpenRouter API
- **Vector Embeddings**: Employs FAISS for efficient similarity search and document processing
- **Error Handling**: Built-in retry mechanisms ensure reliable processing even with complex documents

## 🎯 Use Cases

- **Researchers**: Accelerate literature review and hypothesis generation
- **Students**: Gain deeper insights into complex research topics
- **Academics**: Visualize connections across scientific domains
- **Innovation Teams**: Identify emerging trends and research opportunities

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenRouter API key (for AI model access)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-research-graph-project.git
   cd ai-research-graph-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv graph
   graph\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

## 📖 Usage Guide

1. **Upload or Paste Content**: Choose a PDF file or paste research paper text
2. **Process Document**: Click "Process Paper" to initiate AI analysis
3. **Explore Results**: Navigate through tabs to view:
   - Interactive Knowledge Graph
   - Key Topics and Methodologies
   - Generated Hypotheses
   - Future Work Suggestions

## 🌐 Deployment


## 🏗️ Architecture

```
├── app.py                 # Main Streamlit application
├── src/
│   └── genai_core.py      # Core AI processing functions
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [OpenRouter](https://openrouter.ai/) for AI model access
- Built with [Streamlit](https://streamlit.io/) for the web interface
- Visualization by [PyVis](https://pyvis.readthedocs.io/)
- NLP capabilities through [LangChain](https://langchain.com/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/ai-research-graph-project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-research-graph-project/discussions)

---

**Made with ❤️ for the scientific community**</content>
<parameter name="filePath">c:\Users\Sarvagya\Desktop\Codes\Projects\AI Research Graph Project\README.md