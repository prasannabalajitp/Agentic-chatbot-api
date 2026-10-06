# Enterprise ChatBot

A production-ready AI-powered enterprise chatbot built using **FastAPI, LangGraph, LangChain, DeepAgents, MongoDB, and NVIDIA NIM LLMs**.

The application provides conversational AI with streaming responses, tool calling, uploaded-file search, RAG capabilities, artifact generation, conversation management, authentication, usage tracking, and enterprise-oriented integrations.

---

## Tech Stack

### Backend

- Python 3.11
- FastAPI
- LangGraph
- LangChain
- DeepAgents
- NVIDIA NIM / NVIDIA AI Endpoints
- MongoDB
- PyMongo
- JWT Authentication
- Server-Sent Events (SSE)

### AI / RAG

- Agentic AI
- Tool Calling
- RAG
- Vector Search
- Document Processing
- Embeddings
- LangChain document utilities

### Infrastructure

- Docker
- MongoDB
- REST APIs
- SSE Streaming

---

## Architecture

The application follows a layered architecture:

```text
                    ┌─────────────────────┐
                    │     React Client    │
                    └──────────┬──────────┘
                               │
                          REST / SSE
                               │
                    ┌──────────▼──────────┐
                    │      FastAPI        │
                    │      Routers        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    ChatService      │
                    │  Orchestration Layer│
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    AgentService     │
                    │   DeepAgent /       │
                    │    LangGraph        │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
              NVIDIA         Tools       MongoDB
                LLM         Registry     Checkpointer
```

The backend separates responsibilities across routers, services, repositories, tools, and agent execution.

---

## Project Structure

```text
app/
│
├── common/
│   ├── configurable.py
│   ├── deepagent.py
│   ├── prompt.py
│   ├── sse.py
│   └── tool_result.py
│
├── context/
│   ├── agent_context.py
│   ├── agent_event.py
│   └── agent_result.py
│
├── core/
│   ├── config.py
│   ├── constants.py
│   └── security.py
│
├── database/
│   ├── mongodb.py
│   └── checkpointer.py
|
├── guardrails/
│   ├── guardrail_factory.py
│   ├── prompt_guardrail.py
│   ├── prompts.py
│   ├── retrieval_guardrail.py
│   └── tool_guardrail.py
│
├── llm/
│   └── nvidia_llm.py
|
├── middlewares/
│   └── retry_empty_response_middleware.py
│
├── models/
│   ├── request_model.py
|   ├── request_model.py
|   └── tool_model.py
│
├── repository/
│   ├── artifact_repository.py
│   ├── checkpoint_repository.py
│   ├── conversation_repository.py
│   ├── file_repository.py
│   ├── refresh_token_repository.py
│   ├── usage_repository.py
│   └── user_repository.py
│
├── routers/
|   ├──admin
│   ├── artifact.py
│   ├── auth.py
│   ├── conversation.py
│   ├── file.py
│   ├── message.py
│   └── users.py
│
├── service/
│   ├── admin_service.py
│   ├── agent_service.py
│   ├── artifact_service.py
│   ├── chat_history_service.py
│   ├── chat_service.py
│   ├── conversation_service.py
│   ├── document_parser_service.py
│   ├── embedding_service.py
│   ├── file_service.py
│   ├── guardrail_service.py
│   ├── retrieval_service.py
│   ├── title_service.py
│   ├── usage_service.py
│   ├── user_service.py
│   ├── weather_service.py
│   └── yfinance_service.py
│
├── tools/
│   ├── ai_search.py
│   ├── artifact.py
│   ├── calculator.py
│   ├── datetime.py
│   ├── decorator.py
│   ├── list_uploaded_files.py
│   ├── tool_registry.py
│   ├── weather.py
│   ├── web_search.py
│   └── yfinance.py
│
├── dependencies.py
├── app.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Features

### Authentication

- User registration
- User login
- JWT access-token authentication
- Protected API endpoints
- User-specific resource access

### Conversation Management

- Create conversations
- List conversations
- Paginated conversation list
- Rename conversations
- Delete conversations
- Delete conversation messages
- Conversation activity tracking
- Persistent conversation state

### Streaming Chat

Chat responses are streamed to the client using **Server-Sent Events (SSE)**.

The streaming pipeline supports:

- Chat start
- Model start
- LLM chunks
- Model completion
- Tool calls
- Tool responses
- Conversation activity
- Errors
- Final response

Example:

```text
User Query
    │
    ▼
ChatService
    │
    ▼
AgentService
    │
    ▼
DeepAgent / LangGraph
    │
    ├── LLM
    │
    ├── Tool
    │
    └── LLM
    │
    ▼
SSE Stream
    │
    ▼
Client
```

### Agentic AI

The chatbot uses **DeepAgents and LangGraph** for agent execution.

The agent can:

- Understand conversation context
- Select tools dynamically
- Execute tools
- Process tool results
- Continue execution after tool calls
- Produce a final response
- Maintain state using LangGraph checkpointing

### Tool Calling

The application uses a centralized tool registry.

Current tools include:

- Web search
- Weather information
- Calculator
- Current date/time
- Uploaded-file search
- Uploaded-file listing
- Artifact generation

---

## Uploaded Files and RAG

The application supports uploaded documents and document-based question answering.

The document processing pipeline is:

```text
File Upload
    │
    ▼
File Service
    │
    ▼
Document Processing
    │
    ▼
Text Extraction
    │
    ▼
Chunking
    │
    ▼
Embeddings
    │
    ▼
Vector Storage
    │
    ▼
Retrieval
    │
    ▼
Agent
```

Supported document formats include:

- TXT
- CSV
- PDF
- DOCX

The agent can use uploaded-file search when answering questions about uploaded document content.

---

## Artifact Generation

The chatbot supports generating downloadable files from agent responses.

The artifact flow is:

```text
User Request
    │
    ▼
Agent
    │
    ▼
create_artifact_tool
    │
    ▼
ArtifactService
    │
    ▼
ArtifactRepository
    │
    ├──────────────► MongoDB Metadata
    │
    └──────────────► Artifact File Storage
```

Generated artifacts contain metadata such as:

- Artifact ID
- File name
- Content type
- File size
- File path
- User ID

Artifact metadata is:

- Returned through SSE
- Included in the final `DONE` event
- Persisted with the AI response
- Returned when conversation history is retrieved

### Artifact Download

Generated artifacts can be downloaded through:

```http
GET /artifacts/{artifact_id}/download
```

The endpoint:

- Authenticates the user
- Validates artifact ownership
- Verifies that the artifact exists
- Returns the file using `FileResponse`

Artifact storage is separate from uploaded/RAG files.

---

## Conversation History

Conversation state is persisted using **LangGraph MongoDB checkpointing**.

The application stores and retrieves:

- Human messages
- AI messages
- Tool calls
- Citations
- Generated artifact metadata

Example:

```json
{
  "type": "ai",
  "content": "Here is the generated file.",
  "tool_calls": [],
  "citations": [],
  "artifacts": [
    {
      "artifact_id": "example-id",
      "file_name": "report.csv",
      "content_type": "text/csv",
      "file_size": 1024
    }
  ]
}
```

---

## Usage Tracking

The application tracks LLM usage for each chat request.

Tracked information includes:

- Input tokens
- Output tokens
- Total tokens
- Number of tool calls
- Tools used
- Thread ID
- User ID

Usage is aggregated across multiple LLM calls that may occur during a single agent execution.

Available usage APIs:

```http
GET /users/usage
GET /users/usage/tokens
GET /users/usage/tools
```

---

## Guardrails

The application includes guardrail validation around agent execution.

Guardrails are used for:

- Prompt validation
- Response validation
- Tool execution validation
- Tool call limits
- Preventing unsafe or unintended tool execution

The agent also follows system-level instructions for:

- Tool selection
- Uploaded-file usage
- Response behavior
- Artifact generation

---

## Conversation Title Generation

Conversation titles can be generated automatically after a conversation begins.

Title generation runs as a background task so that it does not block the main response flow.

---

## MongoDB

MongoDB is used for application persistence and LangGraph checkpointing.

The application maintains collections for:

- Users
- Threads
- Conversations
- Checkpoints
- Checkpoint writes
- Uploaded files
- File vectors
- LLM usage
- Artifacts
- Refresh tokens

---

## Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Update the values inside `.env`.

The application requires configuration for:

- MongoDB
- NVIDIA AI endpoints
- JWT authentication
- Application settings

Refer to `.env.example` for the complete configuration.

---

## Installation

### Create Virtual Environment

```bash
python -m venv chatbotenv
```

### Activate

#### Windows

```bash
chatbotenv\Scripts\activate
```

#### Linux

```bash
source chatbotenv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
uvicorn app:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

## Docker

### Build Image

```bash
docker build -t enterprise-chatbot .
```

### Run Container

```bash
docker run -d \
    --name enterprise-chatbot \
    --env-file .env \
    -p 8000:8000 \
    enterprise-chatbot
```

### View Logs

```bash
docker logs -f enterprise-chatbot
```

### Stop Container

```bash
docker stop enterprise-chatbot
```

### Remove Container

```bash
docker rm enterprise-chatbot
```

---

## API Endpoints

### Authentication

```http
POST /auth/login
```

### Users

```http
POST   /users
GET    /users
GET    /users/{user_id}
DELETE /users/{user_id}
```

### Conversations

```http
POST   /conversations
GET    /conversations
PATCH  /conversations/{thread_id}
DELETE /conversations/{thread_id}
DELETE /conversations/{thread_id}/messages
```

### Messages

```http
POST /conversations/{thread_id}/messages
POST /conversations/{thread_id}/messages/stream
GET  /conversations/{thread_id}/messages
```

### Files

Uploaded-file APIs are provided through the file router.

Uploaded files and generated artifacts are maintained as separate resources.

### Artifacts

```http
GET /artifacts/{artifact_id}/download
```

### Usage

```http
GET /users/usage
GET /users/usage/tokens
GET /users/usage/tools
```

---

## Security

The application uses JWT authentication to protect user-specific resources.

Artifact downloads additionally verify that the requested artifact belongs to the authenticated user.

Conversation and file operations are scoped to the authenticated user.

---

## Current Capabilities

The current backend supports:

- JWT authentication
- Conversation management
- Conversation history
- SSE streaming
- Agentic AI
- LangGraph state management
- DeepAgents
- Tool calling
- Web search
- Weather information
- Calculator
- Current date/time
- Uploaded-file processing
- Document extraction
- Embeddings
- Vector search / RAG
- Citations
- Guardrails
- Automatic conversation titles
- LLM usage tracking
- Artifact generation
- Artifact persistence
- Artifact download
- Docker deployment
- MongoDB persistence

---

## Future Enhancements

Potential future enhancements include:

- Advanced tool failure recovery
- Tool timeout and retry policies
- OpenTelemetry integration
- Advanced agent observability
- RAG reranking and retrieval optimization
- Improved context management
- Token optimization
- Human-in-the-loop tool approvals
- Multi-agent workflows
- Advanced RBAC
- Artifact lifecycle management
- Background processing for large artifacts

---

## License

MIT License
