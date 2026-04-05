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
            .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 550px; }
            h2 { color: #1a73e8; margin-top: 0; }
            textarea { width: 100%; height: 80px; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; font-family: inherit; resize: vertical; }
            .primary-btn { background-color: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; }
            .primary-btn:hover { background-color: #1557b0; }
            
            /* NEW STYLES FOR SAMPLE BUTTONS */
            .sample-container { margin-bottom: 15px; }
            .sample-label { font-size: 0.85em; color: #5F6368; margin-bottom: 8px; font-weight: bold; }
            .sample-btn { background-color: #f1f3f4; color: #3c4043; border: 1px solid #dadce0; padding: 6px 12px; border-radius: 16px; cursor: pointer; font-size: 0.85em; margin-right: 6px; margin-bottom: 6px; display: inline-block; transition: all 0.2s;}
            .sample-btn:hover { background-color: #e8f0fe; color: #1967d2; border-color: #d2e3fc; }
            
            .result-box { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #34a853; border-radius: 4px; display: none; white-space: pre-wrap; line-height: 1.5; font-size: 0.95em; }
            .loading { display: none; margin-top: 15px; color: #666; font-style: italic; text-align: center; }
        </style>
    </head>
    <body>
    <div class="container">
        <h2>🤖 OmniTask AI Supervisor</h2>
        <p style="color: #555; font-size: 0.95em;">Enter a complex request, and the multi-agent system will coordinate the execution across your tools.</p>
        
        <div class="sample-container">
            <div class="sample-label">Try a sample workflow:</div>
            <button class="sample-btn" onclick="setPrompt('Move my 3 PM meeting to tomorrow and save a note that I need to prep the slide deck.')">📅 Calendar + Task</button>
            <button class="sample-btn" onclick="setPrompt('Search my notes for the Q3 marketing plan and create a task to review it by Friday.')">🧠 Knowledge + Task</button>
            <button class="sample-btn" onclick="setPrompt('Cancel my 10 AM sync and push my lunch break to 1 PM.')">📅 Complex Calendar</button>
        </div>

        <textarea id="promptInput" placeholder="Type your multi-step request here..."></textarea>
        <button class="primary-btn" onclick="sendTask()">Execute Workflow</button>
        
        <div id="loadingText" class="loading">Supervisor Agent is planning...</div>
        <div id="resultBox" class="result-box"></div>
    </div>
    
    <script>
        // FUNCTION TO AUTO-FILL THE TEXT BOX
        function setPrompt(text) {
            document.getElementById("promptInput").value = text;
        }

        async function sendTask() {
            const promptText = document.getElementById("promptInput").value;
            const resultBox = document.getElementById("resultBox");
            const loadingText = document.getElementById("loadingText");
            
            if (!promptText) return alert("Please enter a task!");

            loadingText.style.display = "block";
            resultBox.style.display = "none";

            try {
                const response = await fetch("/execute-task", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: promptText })
                });

                const data = await response.json();
                
                let executionHtml = "<br><br><strong>⚡ Sub-Agent Execution Logs (via MCP):</strong><br>";
                data.execution.forEach(log => {
                    executionHtml += `<div style="background: #e8f0fe; padding: 10px; margin-top: 10px; border-radius: 5px; border-left: 4px solid #1a73e8;">
                        <strong>${log.agent}</strong><br>
                        ${log.action}<br>
                        <span style="color: green; font-size: 0.9em; font-weight: bold;">${log.status}</span>
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

# 2. THIS ROUTE HANDLES THE AI BRAINPOWER & MCP LOGIC
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
    execution_logs = []
    
    prompt_lower = request.prompt.lower()
    if "meeting" in prompt_lower or "calendar" in prompt_lower or "sync" in prompt_lower or "lunch" in prompt_lower:
        execution_logs.append({
            "agent": "📅 Calendar Sub-Agent",
            "action": "Connecting to Calendar via MCP... Success. Schedule updated.",
            "status": "✅ Complete"
        })
        
    if "note" in prompt_lower or "task" in prompt_lower or "prep" in prompt_lower or "plan" in prompt_lower:
        execution_logs.append({
            "agent": "✅ Task Sub-Agent",
            "action": "Connecting to Task Manager via MCP... Success. Tasks updated.",
            "status": "✅ Complete"
        })
        
    if "database" in prompt_lower or "search" in prompt_lower or "knowledge" in prompt_lower:
        execution_logs.append({
            "agent": "🧠 Knowledge Sub-Agent",
            "action": "Querying AlloyDB pgvector via MCP... Retrieved requested context.",
            "status": "✅ Complete"
        })

    return {
        "original_request": request.prompt,
        "supervisor_plan": response.text,
        "execution": execution_logs,
        "status": "Workflow Executed Successfully"
    }
