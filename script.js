// ==========================================
// SENTRY PIPELINE LOGIC
// ==========================================
const API_URL = "http://localhost:5000";

let organicPool = [];
let swarmPool = [];

function renderToStack(item, containerId) {
    const container = document.getElementById(containerId);
    
    if (container.querySelector('.empty-state')) {
        container.innerHTML = '';
    }

    const div = document.createElement('div');
    div.className = 'post-item';
    div.innerHTML = `<strong>${item.handle}</strong> ${item.text}`;
    
    container.prepend(div);
}

function addOrganicData() {
    const text = document.getElementById('manualPost').value;
    if (!text) return;

    const post = { handle: "@user_organic", text: text };
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
        
        data.forEach(post => {
            swarmPool.push(post);
            renderToStack(post, 'swarmFeed');
        });

        document.getElementById("swarmCount").innerText = swarmPool.length;
        btn.innerText = "Generate Swarm";
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

    feed.innerHTML = '';
    combined.forEach(item => renderToStack(item, 'mixedFeed'));

    document.getElementById('pipeline').scrollIntoView({ behavior: 'smooth' });
}