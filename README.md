
# 🤖 AI Customer Support Agent

An AI-powered customer support system built using Google Gemini, LangChain, LangGraph, RAG, ChromaDB and Streamlit.

## 🚀 Project Overview

This project provides an intelligent customer support experience. Customers can ask questions, get AI-generated answers from a knowledge base, and create support tickets when human assistance is required.

## ✨ Features

- Customer Registration and Login
- Admin Authentication
- AI-powered Chatbot using Gemini
- Retrieval-Augmented Generation (RAG)
- PDF Document Loading
- Semantic Search using ChromaDB
- LangGraph-based Support Workflow
- Automatic Support Ticket Creation
- Ticket Search and Status Management
- Customer-specific Ticket History
- Admin Analytics Dashboard
- Chat History
- Dark Premium UI

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend |
| Streamlit | User Interface |
| Google Gemini | AI Model |
| LangChain | LLM Integration |
| LangGraph | Agent Workflow |
| ChromaDB | Vector Database |
| SQLite | Ticket and User Storage |
| Pandas | Data Analysis |

## 📂 Project Structure

```text
AI-Customer-Support-Agent/
│
├── agents/
│   ├── intent_classifier.py
│   └── support_agent.py
│
├── database/
│   ├── auth_db.py
│   └── ticket_db.py
│
├── knowledge_base/
│   ├── documents/
│   └── faqs.txt
│
├── rag/
│   ├── document_loader.py
│   ├── qa_chain.py
│   └── vector_store.py
│
├── app.py
├── config.py
├── requirements.txt
├── style.css
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/kakash9856/AI-Customer-Support-Agent.git
```

### 2. Open project folder

```bash
cd AI-Customer-Support-Agent
```

### 3. Create virtual environment

```bash
python -m venv .venv
```

### 4. Activate environment (Windows)

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Gemini API Key

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

Never upload your API key to GitHub.

### 7. Run application

```bash
python -m streamlit run app.py
```

## 🔐 Security

- Environment variables are used for API key management.
- `.env` is excluded through `.gitignore`.
- Customer ticket access is restricted by user identity.
- Admin-only ticket management operations.

## 👨‍💻 Author

**Akash Choudhary**

GitHub: https://github.com/kakash9856
