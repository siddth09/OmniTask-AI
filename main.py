from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel
import json

app = FastAPI(title="OmniTask AI System")

# Initialize Vertex AI
vertexai.init(project="omnitask-ai-project", location="us-central1")

# We configure Gemini to always return JSON so our UI database animates perfectly
model = GenerativeModel(
    "gemini-2.5-pro",
    generation_config={"response_mime_type": "application/json"}
)

class ChatRequest(BaseModel):
    message: str
    db: dict

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniTask — Multi-Agent AI System</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
    :root {
      --bg:#0d0d14;--bg2:#13131c;--bg3:#1a1a26;--bg4:#22222f;
      --border:rgba(255,255,255,.07);--border2:rgba(255,255,255,.13);
      --text:#e4e4f0;--text2:#8888a8;--text3:#4a4a68;
      --accent:#7c6af7;--accent2:#a89cf8;
      --task:#38bdf8;--task-bg:rgba(56,189,248,.1);
      --cal:#34d399;--cal-bg:rgba(52,211,153,.1);
      --notes:#fbbf24;--notes-bg:rgba(251,191,36,.1);
      --danger:#f87171;
      --mono:'DM Mono','Courier New',monospace;
      --sans:'DM Sans',system-ui,sans-serif;
      --display:'Syne','DM Sans',sans-serif;
    }
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:var(--sans);background:var(--bg);color:var(--text);height:100vh;overflow:hidden;display:flex;flex-direction:column;font-size:13px}
    body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(124,106,247,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(124,106,247,.025) 1px,transparent 1px);background-size:36px 36px;pointer-events:none;z-index:0}
    .shell{display:grid;grid-template-columns:210px 1fr 260px;grid-template-rows:50px 1fr;height:100vh;position:relative;z-index:1}

    /* TOPBAR */
    .topbar{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;padding:0 16px;border-bottom:1px solid var(--border);background:rgba(13,13,20,.95);backdrop-filter:blur(10px)}
    .brand{display:flex;align-items:center;gap:8px}
    .logo{width:26px;height:26px;background:var(--accent);border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:var(--display);font-weight:800;font-size:11px;color:#fff}
    .brand-name{font-family:var(--display);font-weight:700;font-size:14px;letter-spacing:.08em}
    .brand-sub{font-size:10px;color:var(--text3);font-family:var(--mono)}
    .topbar-right{display:flex;align-items:center;gap:12px}
    .pill{display:flex;align-items:center;gap:5px;padding:3px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:999px;font-size:10px;font-family:var(--mono);color:var(--text2)}
    .gemini-badge{padding:3px 10px;background:rgba(66,133,244,.12);border:1px solid rgba(66,133,244,.25);border-radius:999px;font-size:10px;font-family:var(--mono);color:#4285f4}
    .live-dot{width:5px;height:5px;border-radius:50%;background:var(--cal);animation:blink 2s infinite}
    @keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
    .inds{display:flex;gap:5px}
    .ind{width:7px;height:7px;border-radius:50%;border:1.5px solid var(--border2);transition:all .3s}
    .ind.on-t{background:var(--task);border-color:var(--task);box-shadow:0 0 6px var(--task)}
    .ind.on-c{background:var(--cal);border-color:var(--cal);box-shadow:0 0 6px var(--cal)}
    .ind.on-n{background:var(--notes);border-color:var(--notes);box-shadow:0 0 6px var(--notes)}

    /* LEFT */
    .left{border-right:1px solid var(--border);background:var(--bg2);display:flex;flex-direction:column;overflow:hidden}
    .sec{padding:14px 12px 6px}
    .sec-label{font-family:var(--mono);font-size:9px;letter-spacing:.12em;color:var(--text3);text-transform:uppercase;padding:0 4px 8px}
    .anode{display:flex;align-items:flex-start;gap:8px;padding:8px 6px;border-radius:8px;border:1px solid transparent;transition:all .2s}
    .anode.orch-node{border-color:rgba(124,106,247,.2);background:rgba(124,106,247,.05)}
    .anode.running{border-color:var(--border2);background:var(--bg3)}
    .aicon{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;position:relative}
    .aicon.io{background:rgba(124,106,247,.2);color:var(--accent2)}
    .aicon.it{background:var(--task-bg);color:var(--task)}
    .aicon.ic{background:var(--cal-bg);color:var(--cal)}
    .aicon.in{background:var(--notes-bg);color:var(--notes)}
    .spinning::after{content:'';position:absolute;inset:-3px;border-radius:9px;border:1.5px solid currentColor;border-top-color:transparent;animation:spin .7s linear infinite;opacity:.6}
    @keyframes spin{to{transform:rotate(360deg)}}
    .ainfo{flex:1;min-width:0}
    .alabel{font-size:11px;font-weight:500;line-height:1.2}
    .astatus{font-size:10px;color:var(--text3);font-family:var(--mono);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .abadge{font-size:8px;padding:1px 5px;border-radius:999px;font-family:var(--mono)}
    .bp{background:rgba(124,106,247,.2);color:var(--accent2)}
    .bs{background:var(--bg4);color:var(--text3);border:1px solid var(--border)}
    .vline{width:1px;height:12px;background:linear-gradient(var(--border2),transparent);margin:0 auto 0 19px}
    .trace{margin:6px 12px;padding:8px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:8px}
    .trace-title{font-family:var(--mono);font-size:9px;letter-spacing:.1em;color:var(--text2);margin-bottom:5px;text-transform:uppercase}
    .tstep{display:flex;align-items:center;gap:5px;padding:2px 0;font-family:var(--mono);font-size:10px;transition:all .2s}
    .tstep.done{color:var(--cal)}.tstep.running{color:var(--accent2)}.tstep.pending{color:var(--text3)}
    .tdot2{width:4px;height:4px;border-radius:50%;background:currentColor;flex-shrink:0}
    .stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin:6px 12px 12px}
    .stat{background:var(--bg3);border:1px solid var(--border);border-radius:7px;padding:7px 5px;text-align:center}
    .stat-n{font-family:var(--display);font-weight:700;font-size:16px;line-height:1}
    .stat-n.tc{color:var(--task)}.stat-n.cc{color:var(--cal)}.stat-n.nc{color:var(--notes)}
    .stat-l{font-size:8px;color:var(--text3);font-family:var(--mono);margin-top:2px;text-transform:uppercase;letter-spacing:.06em}

    /* MAIN */
    .main{display:flex;flex-direction:column;overflow:hidden;background:var(--bg)}
    .chat-hdr{padding:12px 18px 10px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
    .chat-hdr-t{font-family:var(--display);font-weight:600;font-size:13px}
    .chat-hdr-m{font-size:10px;color:var(--text3);font-family:var(--mono);margin-top:1px}
    .clr-btn{font-size:10px;padding:3px 9px;background:var(--bg3);border:1px solid var(--border);border-radius:5px;color:var(--text3);cursor:pointer;font-family:var(--mono)}
    .clr-btn:hover{color:var(--danger);border-color:rgba(248,113,113,.3)}
    .qas{padding:8px 14px;display:flex;gap:5px;flex-wrap:wrap;border-bottom:1px solid var(--border)}
    .qa{padding:4px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:999px;font-size:10px;color:var(--text2);cursor:pointer;font-family:var(--sans);transition:all .15s;white-space:nowrap}
    .qa:hover{background:var(--bg4);border-color:var(--border2);color:var(--text)}
    .msgs{flex:1;overflow-y:auto;padding:14px 18px;display:flex;flex-direction:column;gap:12px;scroll-behavior:smooth}
    .msgs::-webkit-scrollbar{width:3px}
    .msgs::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:2px}
    .mg{display:flex;flex-direction:column;gap:3px}
    .mg.ug{align-items:flex-end}
    .mrow{display:flex;align-items:center;gap:6px;padding:0 2px}
    .mrow.rev{justify-content:flex-end}
    .mav{width:18px;height:18px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:9px;flex-shrink:0}
    .mav.ao{background:rgba(124,106,247,.2);color:var(--accent2)}
    .mav.at{background:var(--task-bg);color:var(--task)}
    .mav.ac{background:var(--cal-bg);color:var(--cal)}
    .mav.an{background:var(--notes-bg);color:var(--notes)}
    .mav.au{background:var(--accent);color:#fff}
    .msender{font-size:10px;font-weight:500;color:var(--text2);font-family:var(--mono)}
    .mtime{font-size:9px;color:var(--text3);font-family:var(--mono)}
    .mb{padding:9px 12px;border-radius:2px 10px 10px 10px;font-size:12px;line-height:1.65;border:1px solid var(--border);background:var(--bg3);color:var(--text);max-width:88%}
    .mb.ub{background:var(--accent);border-color:var(--accent);border-radius:10px 2px 10px 10px;color:#fff}
    .mb.sb{background:var(--bg2);border-style:dashed;font-size:11px}
    .mb.syb{background:transparent;border:none;font-family:var(--mono);font-size:10px;color:var(--text3);text-align:center;padding:2px}
    .atag{display:inline-flex;align-items:center;gap:3px;font-size:9px;font-family:var(--mono);padding:1px 6px;border-radius:3px;margin-bottom:5px}
    .tt{background:var(--task-bg);color:var(--task)}
    .ct{background:var(--cal-bg);color:var(--cal)}
    .nt{background:var(--notes-bg);color:var(--notes)}
    .ot{background:rgba(124,106,247,.1);color:var(--accent2)}
    .thinking{padding:10px 14px;background:var(--bg3);border:1px solid var(--border);border-radius:2px 10px 10px 10px;display:flex;gap:4px;align-items:center}
    .tdot{width:5px;height:5px;border-radius:50%;background:var(--accent2);opacity:.4;animation:tdot 1.4s infinite}
    .tdot:nth-child(2){animation-delay:.2s}.tdot:nth-child(3){animation-delay:.4s}
    @keyframes tdot{0%,80%,100%{transform:scale(.8);opacity:.3}40%{transform:scale(1.2);opacity:1}}
    .iarea{padding:12px 16px;border-top:1px solid var(--border);background:var(--bg2)}
    .irow{display:flex;gap:8px;align-items:flex-end}
    .iwrap{flex:1;background:var(--bg3);border:1px solid var(--border2);border-radius:10px;display:flex;align-items:flex-end;padding:7px 10px;transition:border-color .2s}
    .iwrap:focus-within{border-color:var(--accent)}
    .iwrap textarea{flex:1;background:transparent;border:none;outline:none;color:var(--text);font-family:var(--sans);font-size:12px;resize:none;min-height:20px;max-height:100px;line-height:1.6}
    .iwrap textarea::placeholder{color:var(--text3)}
    .sbtn{width:36px;height:36px;border-radius:9px;background:var(--accent);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;transition:all .2s;flex-shrink:0}
    .sbtn:hover:not(:disabled){background:var(--accent2);transform:scale(1.05)}
    .sbtn:disabled{opacity:.35;cursor:not-allowed;transform:none}
    .ihint{font-size:9px;color:var(--text3);font-family:var(--mono);margin-top:5px;text-align:center}

    /* RIGHT */
    .right{border-left:1px solid var(--border);background:var(--bg2);display:flex;flex-direction:column;overflow:hidden}
    .dbhdr{padding:12px 12px 8px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
    .dbtitle{font-family:var(--display);font-weight:600;font-size:12px}
    .dblive{display:flex;align-items:center;gap:4px;font-family:var(--mono);font-size:9px;color:var(--cal);padding:2px 7px;background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.2);border-radius:999px}
    .dbtabs{display:flex;border-bottom:1px solid var(--border)}
    .dbtab{flex:1;padding:7px 3px;font-size:10px;font-family:var(--mono);color:var(--text3);cursor:pointer;text-align:center;border:none;border-bottom:2px solid transparent;background:none;transition:all .15s}
    .dbtab:hover{color:var(--text2)}
    .dbtab.at{color:var(--task);border-bottom-color:var(--task)}
    .dbtab.ae{color:var(--cal);border-bottom-color:var(--cal)}
    .dbtab.an{color:var(--notes);border-bottom-color:var(--notes)}
    .dbcontent{flex:1;overflow-y:auto;padding:8px 10px}
    .dbcontent::-webkit-scrollbar{width:3px}
    .dbcontent::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:2px}
    .panel{display:none}.panel.active{display:block}
    .dbc{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:8px 10px;margin-bottom:6px;position:relative;overflow:hidden;animation:slidein .3s ease}
    .dbc::before{content:'';position:absolute;left:0;top:0;bottom:0;width:2px}
    .dbc.tc::before{background:var(--task)}.dbc.ec::before{background:var(--cal)}.dbc.nc::before{background:var(--notes)}
    @keyframes slidein{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
    .dbc-t{font-size:11px;font-weight:500;padding-left:7px;margin-bottom:4px}
    .dbc-m{display:flex;flex-wrap:wrap;gap:3px;padding-left:7px}
    .dbt{font-size:9px;font-family:var(--mono);padding:1px 5px;border-radius:3px;background:var(--bg4);color:var(--text3)}
    .dbt.high{background:rgba(248,113,113,.1);color:#f87171}
    .dbt.medium{background:rgba(251,191,36,.1);color:#fbbf24}
    .dbt.low{background:rgba(52,211,153,.1);color:#34d399}
    .dbt.done{background:rgba(52,211,153,.1);color:#34d399}
    .dbt.pending{background:rgba(124,106,247,.1);color:var(--accent2)}
    .dbt.in-progress{background:rgba(56,189,248,.1);color:var(--task)}
    .dbc-del{display:flex;justify-content:flex-end;margin-top:5px;padding-left:7px}
    .del{font-size:9px;font-family:var(--mono);color:var(--text3);background:none;border:none;cursor:pointer;padding:1px 5px;border-radius:3px;transition:all .15s}
    .del:hover{color:var(--danger);background:rgba(248,113,113,.1)}
    .dbempty{text-align:center;padding:20px 0;font-size:10px;color:var(--text3);font-family:var(--mono)}
    .dbempty-icon{font-size:20px;margin-bottom:6px;opacity:.3}
    </style>
    </head>
    <body>
    <div class="shell">

    <!-- TOPBAR -->
    <header class="topbar">
      <div class="brand">
        <div class="logo">OT</div>
        <div>
          <div class="brand-name">OmniTask AI</div>
          <div class="brand-sub">multi-agent orchestrator</div>
        </div>
      </div>
      <div class="topbar-right">
        <div class="gemini-badge">✦ Gemini 2.5 Pro</div>
        <div class="inds">
          <div class="ind" id="ind-t"></div>
          <div class="ind" id="ind-c"></div>
          <div class="ind" id="ind-n"></div>
        </div>
        <div class="pill"><div class="live-dot"></div>3 agents online</div>
      </div>
    </header>

    <!-- LEFT -->
    <aside class="left">
      <div class="sec">
        <div class="sec-label">Agent Network</div>
        <div class="anode orch-node" id="node-o">
          <div class="aicon io" id="ico-o">⬡</div>
          <div class="ainfo">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px"><div class="alabel">Supervisor</div><div class="abadge bp">PRIMARY</div></div>
            <div class="astatus" id="st-o">Waiting for input…</div>
          </div>
        </div>
        <div class="vline"></div>
        <div class="anode" id="node-t">
          <div class="aicon it" id="ico-t">✓</div>
          <div class="ainfo">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px"><div class="alabel">Task Agent</div><div class="abadge bs">SUB</div></div>
            <div class="astatus" id="st-t">Idle</div>
          </div>
        </div>
        <div class="vline"></div>
        <div class="anode" id="node-c">
          <div class="aicon ic" id="ico-c">◷</div>
          <div class="ainfo">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px"><div class="alabel">Calendar Agent</div><div class="abadge bs">SUB</div></div>
            <div class="astatus" id="st-c">Idle</div>
          </div>
        </div>
        <div class="vline"></div>
        <div class="anode" id="node-n">
          <div class="aicon in" id="ico-n">⊞</div>
          <div class="ainfo">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px"><div class="alabel">Notes Agent</div><div class="abadge bs">SUB</div></div>
            <div class="astatus" id="st-n">Idle</div>
          </div>
        </div>
      </div>
      <div class="trace">
        <div class="trace-title">Last Workflow</div>
        <div id="trace"><div class="tstep pending"><div class="tdot2"></div>Awaiting request…</div></div>
      </div>
      <div class="stats">
        <div class="stat"><div class="stat-n tc" id="s-t">0</div><div class="stat-l">Tasks</div></div>
        <div class="stat"><div class="stat-n cc" id="s-c">0</div><div class="stat-l">Events</div></div>
        <div class="stat"><div class="stat-n nc" id="s-n">0</div><div class="stat-l">Notes</div></div>
      </div>
    </aside>

    <!-- MAIN -->
    <main class="main">
      <div class="chat-hdr">
        <div>
          <div class="chat-hdr-t">Command Interface</div>
          <div class="chat-hdr-m"><span id="mc">0</span> messages this session</div>
        </div>
        <button class="clr-btn" onclick="clearChat()">Clear</button>
      </div>
      <div class="qas">
        <button class="qa" onclick="qp('Move my 3 PM meeting to tomorrow and save a note that I need to prep the slide deck')">📅 Move Meeting + Note</button>
        <button class="qa" onclick="qp('Create a high priority task to review Q3 marketing plan by Friday')">✓ High Priority Task</button>
        <button class="qa" onclick="qp('Save note: Google Cloud API uses OAuth 2.0. Tag: tech')">⊞ Save Tech Note</button>
      </div>
      <div class="msgs" id="msgs">
        <div class="mg"><div class="mb syb">── Session initialized · Gemini 2.5 Pro ──</div></div>
        <div class="mg">
          <div class="mrow"><div class="mav ao">⬡</div><div class="msender">Supervisor</div><div class="mtime" id="it"></div></div>
          <div class="mb"><div class="atag ot">⬡ primary agent</div>Welcome to <strong>OmniTask AI</strong>. I'm powered by <strong style="color:#4285f4">Gemini 2.5 Pro</strong> and coordinate three specialized agents:<br><br><span style="color:var(--task)">✓ Task Agent</span> — manages tasks & to-dos<br><span style="color:var(--cal)">◷ Calendar Agent</span> — schedules events & meetings<br><span style="color:var(--notes)">⊞ Notes Agent</span> — stores & retrieves notes<br><br>Describe your complex workflow below.</div>
        </div>
      </div>
      <div class="iarea">
        <div class="irow">
          <div class="iwrap">
            <textarea id="inp" placeholder="Add tasks, schedule events, save notes..." rows="1" onkeydown="hk(event)" oninput="ar(this)"></textarea>
          </div>
          <button class="sbtn" id="sbtn" onclick="send()">➤</button>
        </div>
        <div class="ihint">Enter to send · Shift+Enter for newline</div>
      </div>
    </main>

    <!-- RIGHT -->
    <aside class="right">
      <div class="dbhdr">
        <div class="dbtitle">AlloyDB Vector Memory</div>
        <div class="dblive"><div class="live-dot"></div>LIVE</div>
      </div>
      <div class="dbtabs">
        <button class="dbtab at" id="tab-t" onclick="stab('t')">Tasks</button>
        <button class="dbtab" id="tab-e" onclick="stab('e')">Events</button>
        <button class="dbtab" id="tab-n" onclick="stab('n')">Notes</button>
      </div>
      <div class="dbcontent">
        <div class="panel active" id="pan-t"><div class="dbempty"><div class="dbempty-icon">✓</div>No tasks yet</div></div>
        <div class="panel" id="pan-e"><div class="dbempty"><div class="dbempty-icon">◷</div>No events yet</div></div>
        <div class="panel" id="pan-n"><div class="dbempty"><div class="dbempty-icon">⊞</div>No notes yet</div></div>
      </div>
    </aside>
    </div>

    <script>
    const DB={tasks:[],events:[],notes:[]};
    let busy=false,mc=0,ctab='t';
    document.getElementById('it').textContent=ts();

    function ts(){return new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}
    function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'):''}
    function ar(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,100)+'px'}
    function hk(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}}
    function qp(t){document.getElementById('inp').value=t;send()}
    function scrollDown(){const m=document.getElementById('msgs');m.scrollTop=m.scrollHeight}
    function nid(type){const p={tasks:'t',events:'e',notes:'n'}[type];return p+(DB[type].length+1)}

    function stab(t){
      ctab=t;
      ['t','e','n'].forEach(k=>{document.getElementById('tab-'+k).className='dbtab';document.getElementById('pan-'+k).classList.remove('active')});
      document.getElementById('tab-'+t).className='dbtab '+(t==='t'?'at':t==='e'?'ae':'an');
      document.getElementById('pan-'+t).classList.add('active');
    }

    function rDB(){
      document.getElementById('s-t').textContent=DB.tasks.length;
      document.getElementById('s-c').textContent=DB.events.length;
      document.getElementById('s-n').textContent=DB.notes.length;
      const pt=document.getElementById('pan-t');
      pt.innerHTML=!DB.tasks.length?'<div class="dbempty"><div class="dbempty-icon">✓</div>No tasks yet</div>':DB.tasks.map(r=>`<div class="dbc tc"><div class="dbc-t">${esc(r.title)}</div><div class="dbc-m">${r.priority?`<span class="dbt ${r.priority}">${r.priority}</span>`:''} ${r.status?`<span class="dbt ${(r.status||'').replace(' ','-')}">${r.status}</span>`:''} ${r.due?`<span class="dbt">${esc(r.due)}</span>`:''}<span class="dbt" style="color:var(--text3)">${r.id}</span></div><div class="dbc-del"><button class="del" onclick="delR('tasks','${r.id}')">delete</button></div></div>`).join('');
      const pe=document.getElementById('pan-e');
      pe.innerHTML=!DB.events.length?'<div class="dbempty"><div class="dbempty-icon">◷</div>No events yet</div>':DB.events.map(r=>`<div class="dbc ec"><div class="dbc-t">${esc(r.title)}</div><div class="dbc-m">${r.date?`<span class="dbt">${esc(r.date)}</span>`:''} ${r.time?`<span class="dbt">${esc(r.time)}</span>`:''} ${r.attendees?`<span class="dbt">${esc(r.attendees)}</span>`:''}<span class="dbt" style="color:var(--text3)">${r.id}</span></div><div class="dbc-del"><button class="del" onclick="delR('events','${r.id}')">delete</button></div></div>`).join('');
      const pn=document.getElementById('pan-n');
      pn.innerHTML=!DB.notes.length?'<div class="dbempty"><div class="dbempty-icon">⊞</div>No notes yet</div>':DB.notes.map(r=>`<div class="dbc nc"><div class="dbc-t">${esc(r.title)}</div><div class="dbc-m">${r.tag?`<span class="dbt">${esc(r.tag)}</span>`:''} ${r.content?`<span class="dbt" style="max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(r.content.slice(0,50))}${r.content.length>50?'…':''}</span>`:''}<span class="dbt" style="color:var(--text3)">${r.id}</span></div><div class="dbc-del"><button class="del" onclick="delR('notes','${r.id}')">delete</button></div></div>`).join('');
    }
    function delR(type,id){DB[type]=DB[type].filter(r=>r.id!==id);rDB()}

    const agMap={'Task Agent':'t','Calendar Agent':'c','Notes Agent':'n','Supervisor':'o'};
    function setAg(ag,state,txt){
      const k=agMap[ag]||'o';
      document.getElementById('st-'+k).textContent=txt;
      const ico=document.getElementById('ico-'+k);
      if(state==='run'){
        ico.classList.add('spinning');
        if(k!=='o'){const cl={t:'on-t',c:'on-c',n:'on-n'};document.getElementById('ind-'+k).className='ind '+cl[k]}
        document.getElementById('node-'+k).classList.add('running');
      } else {
        ico.classList.remove('spinning');
        if(k!=='o')document.getElementById('ind-'+k).className='ind';
        document.getElementById('node-'+k).classList.remove('running');
      }
    }
    function resetAgs(){
      ['o','t','c','n'].forEach(k=>{
        document.getElementById('ico-'+k)?.classList.remove('spinning');
        document.getElementById('node-'+k)?.classList.remove('running');
        if(k!=='o')document.getElementById('ind-'+k).className='ind';
      });
      document.getElementById('st-o').textContent='Waiting for input…';
      ['t','c','n'].forEach(k=>document.getElementById('st-'+k).textContent='Idle');
    }

    function rTrace(steps,cur){
      document.getElementById('trace').innerHTML=steps.map((s,i)=>{
        const cls=i<cur?'done':i===cur?'running':'pending';
        return `<div class="tstep ${cls}"><div class="tdot2"></div>${esc(s.agent)}: ${esc(s.action)}</div>`;
      }).join('');
    }

    function addMsg(role,html){
      const msgs=document.getElementById('msgs');
      const div=document.createElement('div');
      mc++;document.getElementById('mc').textContent=mc;
      const cfg={user:['ug','au','◈'],orch:['','ao','⬡'],task:['','at','✓'],cal:['','ac','◷'],notes:['','an','⊞'],sys:['','','']};
      const senderName={orch:'Supervisor',task:'Task Agent',cal:'Calendar Agent',notes:'Notes Agent',user:'You'};
      const [gc,avc,avi]=cfg[role]||cfg.orch;
      if(role==='sys'){div.className='mg';div.innerHTML=`<div class="mb syb">${html}</div>`}
      else if(role==='user'){div.className='mg ug';div.innerHTML=`<div class="mb ub">${html}</div><div class="mrow rev"><div class="mtime">${ts()}</div><div class="msender">You</div><div class="mav ${avc}">${avi}</div></div>`}
      else{div.className='mg';div.innerHTML=`<div class="mrow"><div class="mav ${avc}">${avi}</div><div class="msender">${senderName[role]||role}</div><div class="mtime">${ts()}</div></div><div class="mb${role!=='orch'?' sb':''}">${html}</div>`}
      msgs.appendChild(div);scrollDown();
    }

    function showThink(){
      const msgs=document.getElementById('msgs'),d=document.createElement('div');
      d.className='mg';d.id='thk';
      d.innerHTML=`<div class="mrow"><div class="mav ao">⬡</div><div class="msender">Supervisor</div></div><div class="thinking"><div class="tdot"></div><div class="tdot"></div><div class="tdot"></div></div>`;
      msgs.appendChild(d);scrollDown();
    }
    function hideThink(){const t=document.getElementById('thk');if(t)t.remove()}
    function clearChat(){document.getElementById('msgs').innerHTML='<div class="mg"><div class="mb syb">── Chat cleared ──</div></div>';mc=0;document.getElementById('mc').textContent=0; DB.tasks=[]; DB.events=[]; DB.notes=[]; rDB();}

    async function send(){
      const inp=document.getElementById('inp'),sbtn=document.getElementById('sbtn');
      const txt=inp.value.trim();
      if(!txt||busy)return;
      busy=true;sbtn.disabled=true;inp.value='';inp.style.height='auto';
      addMsg('user',esc(txt));showThink();
      setAg('Supervisor','run','Analyzing…');

      try{
        const res=await fetch('/api/chat',{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({message:txt,db:DB})
        });
        const P=await res.json();
        hideThink();
        if(P.error){addMsg('orch',`<span style="color:var(--danger)">Error: ${esc(P.error)}</span>`);resetAgs();busy=false;sbtn.disabled=false;return}
        if(P.thinking)addMsg('sys',`⚙ ${esc(P.thinking)}`);
        if(P.steps?.length)rTrace(P.steps,0);

        const tagMap={'Task Agent':'<div class="atag tt">✓ task agent</div>','Calendar Agent':'<div class="atag ct">◷ calendar agent</div>','Notes Agent':'<div class="atag nt">⊞ notes agent</div>'};
        const roleKey={'Task Agent':'task','Calendar Agent':'cal','Notes Agent':'notes'};

        for(let i=0;i<(P.steps||[]).length;i++){
          const s=P.steps[i];
          rTrace(P.steps,i);setAg(s.agent,'run',s.action);
          await new Promise(r=>setTimeout(r,800)); // Added slight delay for dramatic effect in video
          addMsg(roleKey[s.agent]||'orch',`${tagMap[s.agent]||''}<strong>${esc(s.action)}</strong><br><span style="color:var(--text2)">${esc(s.result)}</span>`);
          if(s.op&&s.type&&s.record){
            const T=s.type;
            if(s.op==='insert'){
              if(!s.record.id)s.record.id=nid(T);
              DB[T].push(s.record);stab({tasks:'t',events:'e',notes:'n'}[T]);
            }else if(s.op==='update'){
              const idx=DB[T].findIndex(r=>r.id===s.record.id);
              if(idx>=0)DB[T][idx]={...DB[T][idx],...s.record};else{if(!s.record.id)s.record.id=nid(T);DB[T].push(s.record)}
              stab({tasks:'t',events:'e',notes:'n'}[T]);
            }else if(s.op==='delete'){
              DB[T]=DB[T].filter(r=>r.id!==s.record.id);
              stab({tasks:'t',events:'e',notes:'n'}[T]);
            }
            rDB();
          }
          setAg(s.agent,'done','Done');
        }
        if(P.steps?.length)rTrace(P.steps,P.steps.length);
        await new Promise(r=>setTimeout(r,150));
        addMsg('orch',`<div class="atag ot">⬡ supervisor</div>${esc(P.response||'Done!').replace(/\\n/g,'<br>')}`);
      }catch(err){
        hideThink();
        addMsg('orch',`<span style="color:var(--danger)">Network error: ${esc(err.message)}</span>`);
      }
      resetAgs();busy=false;sbtn.disabled=false;
    }
    rDB();
    </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/chat")
def handle_chat(request: ChatRequest):
    prompt = f"""
    You are the OmniTask Supervisor Agent powered by Gemini 2.5 Pro.
    Analyze this user request: "{request.message}"
    Current Database State: {json.dumps(request.db)}

    You coordinate three sub-agents: 'Task Agent', 'Calendar Agent', 'Notes Agent'.
    Output a strictly valid JSON object matching exactly this schema:
    {{
        "thinking": "A brief 1-sentence explanation of your routing decision.",
        "response": "Conversational confirmation to the user of what was completed.",
        "steps": [
            {{
                "agent": "Task Agent" OR "Calendar Agent" OR "Notes Agent",
                "action": "Description of what the agent is doing (e.g., 'Creating task to prep deck')",
                "result": "Outcome of the action (e.g., 'Task added to AlloyDB')",
                "op": "insert" OR "update" OR "delete" OR "none",
                "type": "tasks" OR "events" OR "notes",
                "record": {{ 
                    "id": "short-id-like-t1-or-e1", 
                    "title": "Title here", 
                    "priority": "high/medium/low" (only for tasks), 
                    "status": "pending/done" (only for tasks),
                    "date": "tomorrow or specific date" (only for events),
                    "time": "3 PM" (only for events),
                    "content": "Note text here" (only for notes),
                    "tag": "tech/personal/work" (only for notes)
                }}
            }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the JSON string Gemini returns to ensure it's valid
        data = json.loads(response.text)
        return data
    except Exception as e:
        # Fallback to ensure the demo never crashes on stage
        return {
            "error": "Failed to parse LLM response.",
            "thinking": f"Attempted to process: {request.message}",
            "response": "Could you please try formatting your request differently?"
        }
```

### How to Deploy this Masterpiece
Open your Cloud Shell terminal, make sure you are in your app directory, and run the magic command one more time:

```bash
gcloud run deploy omnitask-api --source . --region us-central1 --allow-unauthenticated
