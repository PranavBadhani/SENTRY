
import random
import string

# --- MODULAR BOTNET SIMULATION ENGINE ---
# Combines Openers, Issues, and Closers to dynamically generate 1,000+ unique narratives.

OPENERS = [
    "Absolutely terrible experience.",
    "Warning to everyone reading this.",
    "I've been a loyal customer for years, but no more.",
    "Honestly shocked at how bad this has become.",
    "Do NOT waste your money.",
    "This is a complete scam.",
    "I am incredibly frustrated right now.",
    "Total disaster of a release.",
    "Worst customer service I have ever dealt with.",
    "I regret buying this entirely."
]

ISSUES = [
    "The new update for {target} completely bricked my system.",
    "{target} took my money and support is completely ignoring my tickets.",
    "The build quality of {target} has completely tanked recently.",
    "Every time I try to use {target}, it crashes and deletes my data.",
    "They falsely advertised what {target} could actually do.",
    "My account got locked for no reason and {target} refuses to fix it.",
    "The battery life and performance of {target} is an absolute joke.",
    "{target} is full of hidden fees they refuse to disclose upfront.",
    "The delivery was weeks late and {target} arrived completely broken.",
    "I found out {target} is secretly logging and selling our private data."
]

CLOSERS = [
    "Unacceptable.",
    "Do not buy.",
    "Everyone needs to boycott.",
    "I want a full refund immediately.",
    "Reporting this to the authorities.",
    "Save yourself the headache and go elsewhere.",
    "Total garbage. 🗑️",
    "Never trusting this brand again.",
    "Consider yourselves warned.",
    "A complete downgrade from the previous version."
]

def generate_bot_handle():
    """Generates suspicious, auto-generated looking bot handles."""
    prefix = random.choice(["USER", "NODE", "ALERT", "ANON", "BOT", "SYS", "GHOST", "TEST"])
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"@{prefix}_{suffix}"

def mutate_text(base_text):
    """Adds random strings to the end of posts to simulate hash evasion tactics."""
    mutation = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_text} [id:{mutation}]"

def generate_swarm_payload(target="#TARGET", count=50):
    """
    Constructs the tactical payload. 
    Guarantees zero repetition by tracking generated narratives in a set.
    """
    swarm_data = []
    used_combinations = set()
    
    # Failsafe: Ensures we don't ask for more unique combinations than mathematically possible
    max_combinations = len(OPENERS) * len(ISSUES) * len(CLOSERS)
    actual_count = min(count, max_combinations)

    while len(swarm_data) < actual_count:
        # 1. Dynamically stitch a narrative together
        opener = random.choice(OPENERS)
        issue = random.choice(ISSUES).format(target=target)
        closer = random.choice(CLOSERS)
        
        base_text = f"{opener} {issue} {closer}"
        
        # 2. Check for duplicates to guarantee 100% uniqueness in this batch
        if base_text not in used_combinations:
            used_combinations.add(base_text)
            
            # 3. Apply the final botnet mutation string
            final_text = mutate_text(base_text)
            
            swarm_data.append({
                "handle": generate_bot_handle(),
                "text": final_text
            })

    return swarm_data
    
