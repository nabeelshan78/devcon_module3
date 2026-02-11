# 🧠 Adaptive Reasoning Agent Pro

**A latency-aware AI agent that adjusts *how* it thinks based on *where* it operates.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-UI-red) ![Mistral AI](https://img.shields.io/badge/AI-Mistral-orange) ![Status](https://img.shields.io/badge/Status-Winning-success)

## 📖 Overview

The **Adaptive Reasoning Agent** is a "framework-less" AI system designed to solve the problem of AI performance under varying network conditions. Unlike static chatbots, this agent utilizes a **Network Sentinel** to monitor real-time latency and dynamically switches its cognitive strategy:

* **⚡ Fast Response:** (Low Latency / Manual Override) -> Heuristic, TL;DR answers.
* **⚖️ Standard:** (Moderate Latency) -> Balanced, structured explanations.
* **🧠 Deep Reasoning:** (High Latency / Manual Override) -> Analytical, multi-step logic.

It features a **Native RAG Pipeline** built from scratch (no LangChain/VectorDB dependencies) and a powerful **Document Generation Engine** capable of creating PDFs, Word Docs, and Excel sheets on command.

---

## ✨ Key Features

### 1. 📡 Network-Adaptive Intelligence
The core engine (`NetworkSentinel`) pings high-availability servers to calculate RTT (Round Trip Time).
* **< 300ms:** Enables *Deep Reasoning* (Heavy compute allowed).
* **< 1000ms:** Enforces *Standard Mode*.
* **> 1000ms:** Triggers *Fast Response* (Panic mode, minimizes tokens).
* *Note: Users can manually override this strategy via the Sidebar.*

### 2. 📂 Native RAG Pipeline
A custom-built Retrieval Augmented Generation system without external libraries like LangChain or ChromaDB.
* **Ingestion:** Parses PDF documents using `pypdf`.
* **Chunking:** Sliding window text chunking.
* **Vectorization:** Uses `mistral-embed` for high-quality embeddings.
* **Retrieval:** `scikit-learn` Cosine Similarity for precise context matching.

### 3. 🛠️ Multi-Modal Tooling
The agent intelligently routes queries to specific tools based on intent classification:
* **📄 Document Generator:**
    * **PDF:** Generates structured reports with sanitization for special characters.
    * **Word (.docx):** Creates editable documents with real headings and formatting.
    * **Excel (.xlsx):** Parses data requests into structured spreadsheets.
* **🌐 Adaptive Web Search:** Uses DuckDuckGo to perform "Shallow" (3 results) or "Deep" (8 results + news) searches based on the current reasoning mode.

### 4. 🎨 Clean Streamlit UI
* Dark Mode optimized.
* Real-time token streaming.
* Dynamic "Download" buttons that appear only when files are generated.
* Visual "Internal Thinking" expanders to show the agent's logic.

---

## 🏗️ Architecture

```mermaid
graph TD
    User[User Query] --> UI[Streamlit UI]
    UI --> Sentinel{Network Sentinel}
    Sentinel -- Latency Check --> Mode[Select Reasoning Mode]
    UI -- Manual Override --> Mode
    
    Mode --> Router[Intent Router]
    
    Router -- "WEB" --> WebTool[DuckDuckGo Search]
    Router -- "RAG" --> NativeRAG[Vector Search]
    Router -- "DOC" --> DocTool[File Generator]
    Router -- "NONE" --> LLM[Mistral LLM]
    
    WebTool --> LLM
    NativeRAG --> LLM
    
    LLM --> Response[Streamed Response]
    DocTool --> File[Downloadable File]
```

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8+
* A Mistral AI API Key

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/adaptive-reasoning-agent.git](https://github.com/yourusername/adaptive-reasoning-agent.git)
cd adaptive-reasoning-agent
```

2. Create a Virtual Environment
Bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Configure Environment
Create a .env file in the root directory (or update config.py directly, though .env is safer):

Code snippet
MISTRAL_API_KEY=your_mistral_api_key_here
5. Run the Application
Bash
streamlit run app.py
📂 Project Structure
Plaintext
adaptive-reasoning-agent/
├── app.py                     # Main Streamlit UI entry point
├── config.py                  # Configuration & Thresholds
├── requirements.txt           # Dependencies
├── data/                      # Temporary storage for generated files
└── src/
    ├── core/
    │   └── reasoning_engine.py # The brain: Router, Prompt Engineering, Agent Logic
    ├── tools/
    │   ├── document_tool.py    # Generates PDF/DOCX/XLSX
    │   ├── native_rag.py       # Custom RAG implementation
    │   └── web_tool.py         # Adaptive Web Search
    └── utils/
        └── network.py          # Latency detection logic
💡 Usage Examples
Generating Documents
User: "Create an Excel sheet comparing the revenue of Apple, Google, and Microsoft."

Agent: Detects DOC intent -> Parses data -> Creates .xlsx -> Provides [Download] button.

Adaptive Search
User: "What is the latest news on Quantum Computing?"

Agent (Deep Mode): Performs a deep web search (8+ sources), synthesizes a detailed report.

Agent (Fast Mode): Grabs top 3 headlines, provides a 2-sentence summary.

RAG Analysis
Action: Upload a PDF via the Sidebar.
User: "Summarize the key findings of this paper."
Agent: Vectorizes the PDF -> Retrieves top-k chunks -> Generates grounded summary.

🛡️ License
This project is open-source and available under the MIT License.

Built for the DevCon Module 3 Challenge.
