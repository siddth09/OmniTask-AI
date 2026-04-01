from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel

app = FastAPI(title="OmniTask AI System")

# Initialize Vertex AI
vertexai.init(project="omnitask-ai-project", location="us-central1")
supervisor_model = GenerativeModel("gemini-2.5-pro")

class UserRequest(BaseModel):
    prompt: str

# 1. THIS ROUTE SERVES THE VISUAL DASHBOARD
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OmniTask AI Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 500px; }
            h2 { color: #1a73e8; margin-top: 0; }
            textarea { width: 100%; height: 80px; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; font-family: inherit; }
            button { background-color: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; }
            button:hover { background-color: #1557b0; }
            .result-box { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #34a853; border-radius: 4px; display: none; white-space: pre-wrap; line-height: 1.5; }
            .loading { display: none; margin-top: 15px; color: #666; font-style: italic;}
        </style>
    </head>
    <body>
    <div class="container">
        <h2>🤖 OmniTask AI Supervisor</h2>
        <p>Enter your complex request below, and the multi-agent system will coordinate the execution.</p>
        <textarea id="promptInput" placeholder="e.g., Move my 3 PM meeting to tomorrow and save a note..."></textarea>
        <button onclick="sendTask()">Execute Workflow</button>
        <div id="loadingText" class="loading">Agents are processing your request...</div>
        <div id="resultBox" class="result-box"></div>
    </div><script>
        async function sendTask() {
            const promptText = document.getElementById("promptInput").value;
            const resultBox = document.getElementById("resultBox");
            const loadingText = document.getElementById("loadingText");
            
            if (!promptText) return alert("Please enter a task!");

            loadingText.style.display = "block";
            loadingText.innerText = "Supervisor Agent is planning...";
            resultBox.style.display = "none";

            try {
                const response = await fetch("/execute-task", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: promptText })
                });

                const data = await response.json();
                
                // Build the execution logs HTML
                let executionHtml = "<br><br><strong>⚡ Sub-Agent Execution Logs (via MCP):</strong><br>";
                data.execution.forEach(log => {
                    executionHtml += `<div style="background: #e8f0fe; padding: 10px; margin-top: 10px; border-radius: 5px; border-left: 4px solid #1a73e8;">
                        <strong>${log.agent}</strong><br>
                        ${log.action}<br>
                        <span style="color: green; font-size: 0.9em;">${log.status}</span>
                    </div>`;
                });

                resultBox.innerHTML = `<strong>Status:</strong> ${data.status}<br><br><strong>🧠 Supervisor Plan:</strong><br>${data.supervisor_plan} ${executionHtml}`;
                
                loadingText.style.display = "none";
                resultBox.style.display = "block";
            } catch (error) {
                loadingText.style.display = "none";
                resultBox.style.display = "block";
                resultBox.innerHTML = `❌ Error: ${error.message}`;
            }
        }
    </script>
    </body>
    </html>
    """
    return html_content

# 2. THIS ROUTE HANDLES THE AI BRAINPOWER
@app.post("/execute-task")
def execute_multi_agent_task(request: UserRequest):
    # 1. THE SUPERVISOR PHASE
    supervisor_prompt = f"""
    You are the OmniTask Supervisor Agent. 
    Analyze this user request: "{request.prompt}"
    Determine if you need to route this to the Calendar Agent, Task Agent, or Knowledge Agent.
    Outline your execution plan concisely in bullet points.
    """
    
    response = supervisor_model.generate_content(supervisor_prompt)
    
    # 2. THE EXECUTION PHASE (Simulating MCP Tool Calls)
    # In a production environment, this is where LangGraph would trigger the MCP servers.
    execution_logs = []
    
    prompt_lower = request.prompt.lower()
    if "meeting" in prompt_lower or "calendar" in prompt_lower:
        execution_logs.append({
            "agent": "📅 Calendar Sub-Agent",
            "action": "Connecting to Calendar via MCP... Success. Event '3 PM Meeting' modified to tomorrow.",
            "status": "✅ Complete"
        })
        
    if "note" in prompt_lower or "task" in prompt_lower or "prep" in prompt_lower:
        execution_logs.append({
            "agent": "✅ Task Sub-Agent",
            "action": "Connecting to Task Manager via MCP... Success. New task created: 'Prep the slide deck'.",
            "status": "✅ Complete"
        })
        
    if "database" in prompt_lower or "search" in prompt_lower:
        execution_logs.append({
            "agent": "🧠 Knowledge Sub-Agent",
            "action": "Querying AlloyDB pgvector via MCP... Retrieved past notes.",
            "status": "✅ Complete"
        })

    return {
        "original_request": request.prompt,
        "supervisor_plan": response.text,
        "execution": execution_logs,
        "status": "Workflow Executed Successfully"
    }
