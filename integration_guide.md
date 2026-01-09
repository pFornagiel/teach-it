# Integration Guide: Frontend, Backend & AI Models

This guide details how to transform the current `upside-hackaton` prototype (which currently uses mock data) into a fully functional AI-powered learning platform.

## 1. System Architecture

The system follows a standard 3-tier architecture:
- **Frontend (Vite/React)**: Handles user interaction, file uploads, and chat interface.
- **Backend (Flask)**: Orchestrates logic, manages session state, and interfaces with AI models.
- **AI Layer (OpenAI / Gemini)**: Provides intelligence for topic generation, teaching chat, and evaluation.

### Current Data Flow vs. Target Flow

| Feature | Current Implementation (Mock) | Target Implementation (Real) |
| :--- | :--- | :--- |
| **Topic Generation** | Returns hardcoded list | Backend reads uploaded file -> Sends content to LLM -> LLM extracts topics |
| **Teaching Chat** | Returns cyclic pre-set questions | Backend sends conversation history + Topic + File Context to LLM -> LLM generates contextual question/response |
| **Evaluation** | Returns hardcoded grade | Backend sends full session history to LLM -> LLM analyzes performance and returns structured feedback |

## 2. Environment Setup

To enable "actual models", you must configure the environment variables.

1.  **Create/Edit `.env` in `d:\hackaton\upside-hackaton\backend\.env`**
2.  **Add API Keys**:
    ```ini
    # Choose your provider
    OPENAI_API_KEY=sk-proj-...
    # OR
    GOOGLE_API_KEY=AIzaSy...
    ```

## 3. Implementation Steps

There are 3 main backend functions in `app.py` that need to be "hydrated" with real AI logic.

### A. Topic Generation (`/api/topics`)

**Goal**: Extract learnable topics from the uploaded user files.

1.  **Read File Content**: Use a library like `PyPDF2` (for PDFs) or built-in file reading (for text) to extract text from the file stored in `UPLOAD_FOLDER`.
2.  **Prompt the Model**:
    > "Analyze the following text and extract 5 key learnable topics suitable for a student. Return ONLY a JSON array of strings."
3.  **Parse & Return**: Clean the response and return it as `{'topics': ["Topic 1", "Topic 2"]}`.

### B. Teaching Session (`/api/chat`)

**Goal**: Acts as a Socratic tutor, asking questions to check understanding.

1.  **Retrieve Context**: Get the `session` object from memory, including `topic` and `history`.
2.  **Construct Prompt**:
    *   **System Prompt**: "You are a Socratic tutor. Your goal is to verify the student's understanding of {topic}. Ask insightful questions one by one. Do not lecture; ask. Assess their previous answer before moving on."
    *   **Context**: Include a summary or snippet of the uploaded file content if relevant.
    *   **History**: Append the full `session['history']` (User/Assistant turns).
3.  **Call API**: Use `openai.chat.completions.create` (stream=False for simplicity) or `genai.GenerativeModel.generate_content`.
4.  **Update State**: Append the AI's response to `session['history']`.
5.  **Scoring (Optional)**: Ask the LLM to also return a hidden "score" for the user's last answer to track progress for the `questions_asked` limit.

### C. Evaluation (`/api/evaluate`)

**Goal**: Provide a final grade and detailed feedback.

1.  **Compile Transcript**: Format `session['history']` into a readable string.
2.  **Prompt the Model**:
    > "Review the following tutoring session transcript. Evaluate the student's understanding of {topic}. Provide a Grade (A-F), a general comment, and detailed feedback points. Return as JSON: { grade, comments, details: [{point, status}] }."
3.  **Return**: Pass this JSON directly to the frontend.

## 4. Code Snippets for "Actual Models"

Here is how the code *should* look when implemented. Current mocks in `app.py` should be replaced with this logic.

### OpenAI Example (`topics`)

```python
import openai
import json

client = openai.OpenAI() # Uses OPENAI_API_KEY from env

def get_real_topics(file_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful curriculum planner."},
            {"role": "user", "content": f"Extract 5 distinct study topics from this text: {file_content[:4000]}..."} # Truncate if too long
        ],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)
```

### Gemini Example (`chat`)

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def get_tutor_response(history, topic):
    # Convert history format if needed
    chat = model.start_chat(history=[])
    
    prompt = f"Topic: {topic}. Evaluate previous answer (if any) and ask the next question."
    response = chat.send_message(prompt)
    return response.text
```

## 5. Workflow for the Agent

If you (the Agent) are asked to "implement the models", follow this exact checklist:

1.  [ ] **Install Dependencies**: Ensure `openai` or `google-generativeai` is installed.
2.  [ ] **Setup Client**: Initialize the client at the top of `app.py`.
3.  [ ] **Helper Functions**: Create `extract_text_from_file(filepath)` helper in `app.py`.
4.  [ ] **Replace `/api/topics`**: Remove the sleep and hardcoded list. Insert the LLM call to generate topics from the file text.
5.  [ ] **Replace `/api/chat`**:
    *   Change logic to send `session['history']` to the LLM.
    *   Ensure the System Prompt enforces "Socratic Method" (asking instead of telling).
6.  [ ] **Replace `/api/evaluate`**: Send the conversation log to the LLM for grading.

## 6. Frontend Considerations

The Frontend is largely ready (`frontend/src/lib/api.ts` likely expects these JSON structures).
*   **No big changes needed** on Frontend if the Backend maintains the JSON contract:
    *   `/api/topics` -> `{ topics: string[] }`
    *   `/api/chat` -> `{ question: string, finished: bool }`
    *   `/api/evaluate` -> `{ grade: string, comments: string, details: [] }`

Just ensure the backend returns these exact keys!
