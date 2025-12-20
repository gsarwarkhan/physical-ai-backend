# **Physical-AI-Humanoid-Textbook**

## Bridging the Digital Brain to the Physical Body

This repository hosts the 'Physical AI & Humanoid Robotics' textbook, an interactive and comprehensive resource designed to guide learners through the complexities of integrating artificial intelligence with physical robotic systems. This project serves as a dynamic learning platform, combining in-depth theoretical knowledge with practical applications, all powered by modern web and AI technologies.

## 🚀 Tech Stack

Our platform leverages a robust and contemporary tech stack to deliver an engaging and intelligent learning experience:

-   **Frontend**: [**Docusaurus**](https://docusaurus.io/)
    *   A static site generator that helps us build and maintain our documentation website with ease, providing a clean, navigable, and responsive user interface for the textbook content.
-   **Backend**: [**FastAPI**](https://fastapi.tiangolo.com/)
    *   A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It powers our intelligent chatbot.
-   **Large Language Model**: [**Gemini 1.5 Flash**](https://ai.google.dev/models/gemini)
    *   Google's cutting-edge generative AI model, utilized for its efficiency and capability in understanding complex queries and generating coherent, contextually relevant answers within our chatbot.
-   **Vector Database**: [**Qdrant**](https://qdrant.tech/)
    *   A vector similarity search engine that stores, searches, and manages vector embeddings. It's crucial for the Retrieval-Augmented Generation (RAG) capabilities of our chatbot, allowing it to efficiently find relevant textbook passages.

## ✨ Features

-   **RAG-powered Chatbot**: An intelligent conversational agent that can answer questions about the textbook content by retrieving relevant information from the knowledge base and synthesizing answers using Gemini 1.5 Flash.
-   **Hardware Personalization**: Detailed guides and considerations for various hardware setups, from high-end workstations (NVIDIA RTX 4090) to embedded systems (Jetson Orin Nano) and cloud environments (AWS/Google Cloud).
-   **Urdu Language Support**: The textbook supports multiple locales, including English and Urdu, making it accessible to a broader audience.

## ⚡ Quick Start

Follow these steps to get your local development environment up and running.

### 1. Prerequisites

-   Node.js (>=18.0)
-   Python (>=3.8)
-   `pip` (Python package installer)
-   `npm` or `yarn` (Node.js package manager)
-   A Google Cloud Project with the Gemini API enabled (for `GOOGLE_API_KEY`)
-   A Qdrant Cloud instance or local installation (for `QDRANT_URL` and `QDRANT_API_KEY`)

### 2. Environment Variables

Create a `.env` file in the root of your project or set these as system-wide environment variables:

```bash
# Example for PowerShell (Windows)
$env:QDRANT_URL='YOUR_QDRANT_URL'
$env:QDRANT_API_KEY='YOUR_QDRANT_API_KEY'
$env:GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'

# Example for Bash/Zsh (Linux/macOS)
export QDRANT_URL='YOUR_QDRANT_URL'
export QDRANT_API_KEY='YOUR_QDRANT_API_KEY'
export GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'
```
**Replace the placeholder values with your actual API keys and Qdrant URL.**

### 3. Frontend (Docusaurus)

1.  **Install Dependencies**:
    ```bash
    npm install
    ```
2.  **Start Development Server**:
    ```bash
    npm start
    ```
    The Docusaurus site will open in your browser, usually at `http://localhost:3001`.

### 4. Backend (FastAPI RAG Chatbot)

1.  **Install Python Dependencies**:
    ```bash
    pip install fastapi uvicorn qdrant-client google-generativeai pydantic
    ```
2.  **Navigate to the `src` directory**:
    ```bash
    cd src
    ```
3.  **Run the Backend Server**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    The FastAPI server will start, listening on `http://127.0.0.1:8000`.

### 5. Ingest Textbook Content into Qdrant (Optional, First-time Setup)

To enable the RAG chatbot to answer questions about your textbook content, you need to ingest the markdown files into Qdrant.

1.  **Navigate to the `src/backend` directory**:
    ```bash
    cd src/backend
    ```
2.  **Run the ingestion script**:
    ```bash
    python ingest.py
    ```
    This script will read your `docs` content, generate embeddings, and upload them to your configured Qdrant instance.

## 💖 Credits

This project was developed as part of the **Panaversity Hackathon**, an initiative dedicated to fostering innovation and practical application in AI and robotics education.

---

Happy learning and building!