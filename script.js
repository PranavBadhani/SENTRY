const API_URL = "http://localhost:5000";

let organicPool = [];
let swarmPool = [];
let activeCorpus = [];

function generateId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

function formatTime(ms) {
    const d = new Date(ms);
    return `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}.${d.getMilliseconds().toString().padStart(3,'0')}`;
}

function renderToStack(item, containerId) {
    const container = document.getElementById(containerId);
    
    if (container.querySelector('.empty-state')) {
        container.innerHTML = '';
    }

    const div = document.createElement('div');
    div.className = 'post-item';
    
    // Check if it's already analyzed
    if (item.threat_probability !== undefined) {
        const probStr = (item.threat_probability * 100).toFixed(1);
        if (item.flagged) {
            div.style.borderLeftColor = 'var(--accent-red)';
            div.innerHTML = `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <strong style="color: var(--accent-red); background: rgba(255, 42, 84, 0.1);">${item.handle} [FLAGGED]</strong>
                                <div style="text-align: right;">
                                    <span style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--accent-red); display: block;">THREAT: ${probStr}%</span>
                                    <span style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-muted);">${formatTime(item.timestamp)}</span>
                                </div>
                             </div>
                             ${item.text}`;
        } else {
            div.style.borderLeftColor = 'var(--accent-green)';
            div.innerHTML = `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <strong style="color: var(--accent-green); background: rgba(16, 185, 129, 0.1);">${item.handle} [AUTHENTIC]</strong>
                                <div style="text-align: right;">
                                    <span style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--accent-green); display: block;">THREAT: ${probStr}%</span>
                                    <span style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-muted);">${formatTime(item.timestamp)}</span>
                                </div>
                             </div>
                             ${item.text}`;
        }
    } else {
        // Standard unanalyzed render
        div.innerHTML = `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <strong>${item.handle}</strong>
                            <span style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-muted);">${formatTime(item.timestamp)}</span>
                         </div>
                         ${item.text}`;
    }
    
    container.prepend(div);
}

function addOrganicData() {
    const text = document.getElementById('manualPost').value;
    if (!text) return;

    const post = { id: generateId(), handle: "@user_organic", text: text, timestamp: Date.now() };
    organicPool.push(post);
    
    document.getElementById('organicCount').innerText = organicPool.length;
    renderToStack(post, 'organicFeed');
    document.getElementById('manualPost').value = '';
}

async function addSwarmData() {
    const target = document.getElementById("target").value || "#Target";
    const count = parseInt(document.getElementById("count").value) || 10;
    const btn = document.getElementById("swarmBtn");
    
    btn.innerText = "Synthesizing...";

    try {
        const res = await fetch(`${API_URL}/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target, count, type: "swarm" })
        });
        
        const data = await res.json();
        const baseTime = Date.now();
        
        data.forEach(post => {
            // Cluster the swarm virtually instantly (within ~50ms of each other)
            const clusteredTime = baseTime + Math.floor(Math.random() * 50);
            const swarmPost = { ...post, id: generateId(), timestamp: clusteredTime };
            swarmPool.push(swarmPost);
            renderToStack(swarmPost, 'swarmFeed');
        });

        document.getElementById("swarmCount").innerText = swarmPool.length;
        btn.innerText = "Initialize Swarm";
    } catch (e) {
        btn.innerText = "Agent Offline";
        console.error("Agent server not found on port 5000.");
    }
}

function shuffleAndDisplay() {
    const feed = document.getElementById('mixedFeed');
    let combined = [...organicPool, ...swarmPool];

    if (combined.length === 0) return alert("Corpus is empty. Please inject data.");

    for (let i = combined.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [combined[i], combined[j]] = [combined[j], combined[i]];
    }
    
    // Store globally so the Analysis payload uses the shuffled layout
    activeCorpus = combined;

    feed.innerHTML = '';
    activeCorpus.forEach(item => renderToStack(item, 'mixedFeed'));
}

async function executeAnalysis() {
    if (activeCorpus.length === 0) return alert("Corpus is empty. Please inject and shuffle data first.");

    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.innerText = "Scanning...";
    analyzeBtn.disabled = true;

    try {
        const res = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ corpus: activeCorpus })
        });
        
        if (!res.ok) throw new Error("Transformer backend error");
        const analyzedData = await res.json();
        
        renderAnalyzedResults(analyzedData);
        
        analyzeBtn.innerText = "Analyze Reviews";
        analyzeBtn.disabled = false;
        
    } catch (e) {
        alert("Fatal Error: Neural engine offline or crashed.");
        analyzeBtn.innerText = "Analyze Reviews";
        analyzeBtn.disabled = false;
    }
}

function renderAnalyzedResults(data) {
    const resultsContainer = document.getElementById('analysisResults');
    resultsContainer.innerHTML = ''; // Clears the placeholder and old results
    
    data.forEach(item => renderToStack(item, 'analysisResults'));
}