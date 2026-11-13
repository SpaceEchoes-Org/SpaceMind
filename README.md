# AI    
# 🚀 NASA SpaceMind

**NASA SpaceMind** is a knowledge-based chatbot and educational quiz system designed to provide information about NASA missions, space exploration, and planetary science.

The project uses a structured NASA knowledge base and BM25-based retrieval to retrieve relevant facts and generate answers supported by available evidence.

## ✨ Features

- **Knowledge-Based Chatbot:** Answers questions using the NASA knowledge base.
- **BM25 Retrieval:** Retrieves relevant information from stored knowledge records.
- **Evidence-Based Answers:** Provides supporting evidence and source information.
- **Unknown Question Handling:** Designed to avoid generating unsupported answers.
- **Quiz Generation:** Generates educational quizzes.
- **Quiz Evaluation:** Evaluates submitted answers and calculates scores.
- **FastAPI Backend:** Exposes API endpoints for backend integration.
- **NASA Image Search:** Supports searching for NASA-related images.
- **Session Management:** Supports session identifiers for conversation handling.

## 🛠️ Technologies Used

- Python
- FastAPI
- BM25 Retrieval
- Pydantic
- Uvicorn
- JSON Knowledge Base

## 📁 Project Structure

```text
NASA_SpaceMind/
│
├── api/
├── chatbot/
├── quiz/
├── retrieval/
├── ingestion/
├── images/
├── data/
├── dataraw/
├── dataprocessed/
├── tests/
│
├── requirements.txt
├── test_quiz.py
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd NASA_SpaceMind
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application

Start the FastAPI server:

```bash
uvicorn api.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

### API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 💬 Chat API

**Endpoint:**

`POST /chat`

Example request:

```json
{
  "question": "How many wheels did the Lunar Roving Vehicle have?"
}
```

Expected answer:

```text
The Lunar Roving Vehicle was an electric vehicle with four wheels.
```

## 🧠 Quiz API

The project includes quiz generation and evaluation modules.

Available API routes and request schemas should be confirmed through the FastAPI Swagger documentation.

## 🖼️ NASA Image Search

The application provides an image search endpoint.

Example:

```text
GET /images/search?query=Perseverance%20Rover&page=1&page_size=5
```

## 🧪 Testing

Run the existing quiz test script:

```bash
python test_quiz.py
```

Run automated tests with:

```bash
python -m pytest
```

Test coverage and API integration are still under review.

## ⚠️ Current Project Status

- Chat API: Initial functional tests passed for Mars Pathfinder and Lunar Roving Vehicle.
- Quiz API: Endpoint availability and integration require further verification.
- Arabic question handling: Pending testing.
- Unknown question handling: Pending testing.
- Automated test discovery: Pending verification.
- Knowledge records: Some records are pending independent verification.

## 🔗 Backend Integration

The project exposes a FastAPI backend intended for integration with a larger application.

The reviewer should verify:

- API contracts and response schemas.
- Retrieval accuracy and evidence handling.
- Session isolation.
- Quiz generation and evaluation.
- Image search functionality.
- Automated test coverage.

## 👩‍💻 Project

**NASA SpaceMind**

Knowledge-Based Chatbot & Educational Quiz API.
