**Brief about the idea**
====
• OmniTask AI is an API-first, intelligent backend system designed to eliminate context-switching.

• Instead of relying on a single monolithic chatbot, OmniTask utilizes a Primary "Supervisor" Agent
(powered by Gemini 2.5 Pro) that intercepts natural language requests and delegates them to
specialized Sub-Agents (Calendar, Task, and Knowledge Agents).

• These agents act autonomously to execute multi-step workflows in a single fluid action, deployed
entirely serverless on Google Cloud Run.

**OmniTask AI** directly addresses the core criteria through a modern, scalable architecture
=====
**• Multi-Agent Coordination:** A LangGraph-inspired architecture where a Gemini 2.5 Pro Supervisor
evaluates prompts and routes tasks to specialized sub-agents.

**• AlloyDB AI Integration:** We designated AlloyDB AI as the core memory engine. Because it
natively supports pgvector, it's uniquely positioned to store both structured task data and
unstructured user notes, allowing the Knowledge Agent to perform rapid semantic similarity
searches.

**• MCP Ready:** The system is designed around the Model Context Protocol (MCP) to standardize
how sub-agents communicate with external tools (Calendar, Tasks), ensuring secure and modular
tool execution.

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/63e6d267-b7ce-4f6a-875a-a36ffe3867a2" />


Technologies to be used in the solution
====
**• Google Cloud Run:** Serverless container hosting for the API and UI.

**• Vertex AI (Gemini 2.5 Pro):** The core LLM powering the reasoning, planning, and agent
coordination.

**• AlloyDB AI:** Fully managed PostgreSQL database utilizing pgvector for advanced data and
embedding storage.

**• Model Context Protocol (MCP):** Architectural standard for connecting AI models to external tools.

**• Python/FastAPI:** The backend framework for routing and API creation.
