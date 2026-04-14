# AutoScout 🚀

AutoScout is a powerful personal interest research assistant built on **Agno** and **AgentOS**. It leverages a multi-agent orchestration team to dynamically track your interests, scan the web for high-signal content, and synthesize daily digests.

## ✨ Features

- **Dynamic Interest Profiling**: Automatically tracks and refines your research categories.
- **Multi-Agent Teams**: specialized agents for web scouting, deep analysis, criticism, and curation.
- **Daily Digest Pipeline**: A structured workflow that transforms raw web data into actionable insights.
- **RAG-Powered Memory**: Uses PgVector and `BAAI/bge-m3` embeddings for long-term knowledge retention.

## 🛠️ Technology Stack

- **Framework**: [Agno](https://github.com/agno-ai/agno) & AgentOS
- **Models**: Google Gemini 3.0 (Flash & Pro)
- **Search**: Exa AI (via MCP)
- **Database**: PostgreSQL + PgVector
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## 🚀 Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- [uv](https://astral.sh/uv/) installed

### 2. Setup Infrastructure
Start the PostgreSQL database with the pgvector extension:
```bash
docker compose up -d
```

### 3. Environment Configuration
Copy the template and add your API keys:
```bash
cp .env.example .env # If template was created as .env, just edit it
```
Ensure `GOOGLE_API_KEY` and `EXA_API_KEY` are populated.

### 4. Install Dependencies
Synchronize the virtual environment:
```bash
uv sync
```

### 5. Run the Application
Start the AgentOS server:
```bash
uv run python -m app.main
```
The UI will be accessible at `http://localhost:8000`.

## 📁 Project Structure

```text
.
├── agents/             # Agent definitions and settings
├── teams/              # Multi-agent coordination (Coordinate, Route, Broadcast)
├── workflows/          # Task-specific pipelines (Daily Digest)
├── db/                 # Database session and RAG configuration
├── app/                # Main entry point and AgentOS config
├── interests/          # Managed user preference files
└── context/            # Static prompts and evaluation criteria
```

## 📝 License
MIT
