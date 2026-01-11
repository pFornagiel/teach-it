# Teach.it - AI Tutoring Platform 🎓

**Teach.it** is an interactive AI-powered educational platform designed to transform static study materials into dynamic tutoring sessions.

Instead of passively reading notes, users upload their documents, and the system acts as a **Socratic Tutor**. It extracts key topics, engages the user in a dialogue to test understanding, and provides comprehensive evaluations.

### Key Features
*   **📄 Smart Document Analysis**: Upload PDF, DOCX, or TXT files. The system analyzes the content to extract "learnable" topics.
*   **🧠 Socratic Dialogue**: The AI asks probing questions to check depth of understanding, rather than just delivering information.
*   **📊 Performance Evaluation**: Get real-time feedback and a structured grading at the end of a session.

## 🎥 Demo

![App Demo](assets/demo.webp)

## 🛠 Technologies

### Frontend
*   **Framework**: [React](https://react.dev/) (v19) with [Vite](https://vitejs.dev/)
*   **Language**: TypeScript
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
*   **UI Components**: [Shadcn/UI](https://ui.shadcn.com/)
*   **Animations**: [Framer Motion](https://www.framer.com/motion/)
*   **Icons**: Lucide React

### Backend
*   **Server**: [Flask](https://flask.palletsprojects.com/) (Python)
*   **AI Orchestration**: [LangChain](https://www.langchain.com/)
*   **LLM Providers**: Open AI & Google Gemini
*   **Vector Store**: FAISS (for RAG - Retrieval Augmented Generation)

## 🚀 Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Start-Up-Side-2025/upside-hackaton.git
    cd upside-hackaton
    ```

2.  **Backend Setup**
    Navigate to the backend directory and set up the virtual environment.

    ```bash
    cd backend
    # Create virtual environment
    python -m venv venv
    
    # Activate virtual environment
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```

    **Configuration**: Create a `.env` file in the `backend` directory:
    ```env
    OPENAI_API_KEY=your_openai_key
    GOOGLE_API_KEY=your_gemini_key
    ```

3.  **Frontend Setup**
    Navigate to the frontend directory and install dependencies.

    ```bash
    cd ../frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend Server**
    ```bash
    # In backend directory
    python app.py
    ```
    The server will start at `http://127.0.0.1:5000`.

2.  **Start the Frontend Client**
    ```bash
    # In frontend directory
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## 👥 Contributors

*   [**pFornagiel**](https://github.com/pFornagiel/)
*   [**macwsn**](https://github.com/macwsn)
*   [**Hbrtjm**](https://github.com/Hbrtjm)
*   [**radbene**](https://github.com/radbene)

---
*Created for Upside Hackathon 2025*
