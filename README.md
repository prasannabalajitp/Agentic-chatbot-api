# Enterprise ChatBot

A production-ready AI-powered chatbot built using **FastAPI**, **LangGraph**, **LangChain**, **MongoDB**, and **NVIDIA NIM LLMs**.

The application supports:

- JWT Authentication
- Conversation Management
- Conversation Streaming (SSE)
- Chat History
- Tool Calling
- Web Search
- Weather Tool
- Calculator Tool
- Conversation Title Generation
- Docker Deployment

---

# Tech Stack

- Python 3.11
- FastAPI
- LangGraph
- LangChain
- MongoDB
- NVIDIA AI Endpoints
- Docker
- JWT Authentication

---

# Project Structure

```
app/
│
├── common/
├── core/
├── database/
├── dependencies.py
├── llm/
├── models/
├── repository/
├── routers/
├── service/
├── tools/
├── app.py
│
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

# Features

- User Registration
- User Login
- JWT Authentication
- Create Conversation
- Rename Conversation
- Delete Conversation
- Delete Conversation Messages
- Paginated Conversation List
- Streaming Chat Responses (SSE)
- Chat History
- Tool Calling
- Weather Information
- Web Search
- Calculator
- Automatic Conversation Title Generation

---

# Environment Variables

Copy the example file.

```bash
cp .env.example .env
```

Update the values inside `.env`.

---

# Installation

Create virtual environment

```bash
python -m venv chatbotenv
```

Activate

Windows

```bash
chatbotenv\Scripts\activate
```

Linux

```bash
source chatbotenv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn app:app --reload
```

Swagger

```
http://localhost:8000/docs
```

---

# Docker

Build Image

```bash
docker build -t enterprise-chatbot .
```

Run

```bash
docker run -d \
    --name enterprise-chatbot \
    --env-file .env \
    -p 8000:8000 \
    enterprise-chatbot
```

View Logs

```bash
docker logs -f enterprise-chatbot
```

Stop

```bash
docker stop enterprise-chatbot
```

Remove

```bash
docker rm enterprise-chatbot
```

---

# Authentication

Register User

```
POST /users
```

Login

```
POST /auth/login
```

The login endpoint returns a JWT access token.

Use the token in subsequent requests.

```
Authorization: Bearer <access_token>
```

---

# API Endpoints

## Authentication

```
POST /auth/login
```

---

## Users

```
POST /users
GET /users
GET /users/{user_id}
DELETE /users/{user_id}
```

---

## Conversations

```
POST   /conversations
GET    /conversations
PATCH  /conversations/{thread_id}
DELETE /conversations/{thread_id}
DELETE /conversations/{thread_id}/messages
```

---

## Messages

```
POST /conversations/{thread_id}/messages
POST /conversations/{thread_id}/messages/stream
GET  /conversations/{thread_id}/messages
```

---

# Future Enhancements

- Refresh Tokens
- Role-Based Access Control (RBAC)
- File Upload Support
- RAG Integration
- Vector Database
- Conversation Export
- Multi-Agent Support

---

# License

MIT License
