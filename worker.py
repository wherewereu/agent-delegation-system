#!/usr/bin/env python3
"""
Agent Worker - Poll Hydra and execute delegated tasks
Usage: python3 worker.py [agent_name]
Example: python3 worker.py scout
"""
import sys
import time
import json
import requests
from datetime import datetime

HYDRA_URL = "http://192.168.0.247:8500"
POLL_INTERVAL = 5  # seconds

# Agent task handlers
def handle_scout(content):
    """Research agent - search the web"""
    import requests
    
    # Clean the content
    content = content.strip().rstrip('?').lower()
    
    # Remove common research keywords to get the actual topic
    skip_phrases = ['research', 'search', 'find', 'look up', 'what is', 'who is', 'history of', 'about', 'information on']
    query = content
    for phrase in skip_phrases:
        query = query.replace(phrase, '')
    
    # Clean up and take first meaningful words
    query = ' '.join(query.split())[:50]
    query = query.replace(" ", "_")
    
    if not query:
        query = content.replace(" ", "_")[:50]
    
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        resp = requests.get(url, timeout=5, headers={"User-Agent": "FlumeDelegation/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            return f"🔍 Research for '{content}':\n\n📖 {data.get('extract', 'No results')}\n\nSource: {data.get('content_urls', {}).get('desktop', {}).get('page', 'Wikipedia')}"
        elif resp.status_code == 404:
            return f"🔍 Research for '{content}':\n\n❓ Couldn't find info on '{query.replace('_', ' ')}'"
    except Exception as e:
        pass
    
    return f"🔍 Research for '{content}':\n\n(Search unavailable)"

def handle_link(content):
    """Communications agent - handle messages"""
    # Use gog for Gmail or imsg for iMessage
    return f"📧 Would send message: {content}\n\n(Note: Link needs explicit recipient to send)"

def handle_cart(content):
    """Procurement agent - handle orders"""
    return f"🛒 Would order: {content}\n\n(Note: Cart needs product details to order)"

def handle_clock(content):
    """Calendar agent - handle scheduling"""
    return f"🕐 Would schedule: {content}\n\n(Note: Clock needs time details to create event)"

def handle_vital(content):
    """Health agent - handle health tracking"""
    return f"❤️ Would track: {content}\n\n(Note: Vital needs specific metrics)"

def handle_forge(content):
    """Code agent - handle coding tasks"""
    return f"⚒️ Would code: {content}\n\n(Note: Output routes to Judge for review)"

def handle_judge(content):
    """Review agent - handle code review"""
    return f"⚖️ Would review: {content}"

HANDLERS = {
    "scout": handle_scout,
    "link": handle_link,
    "cart": handle_cart,
    "clock": handle_clock,
    "vital": handle_vital,
    "forge": handle_forge,
    "judge": handle_judge,
}

def get_messages(agent_name):
    """Get pending messages for an agent from Hydra"""
    try:
        response = requests.get(f"{HYDRA_URL}/messages/{agent_name}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("messages", [])
    except Exception as e:
        print(f"Error fetching messages: {e}")
    return []

def process_message(message, agent_name):
    """Process a single message"""
    task_id = message.get("id")
    content = message.get("content", "")
    sender = message.get("sender", "unknown")
    
    print(f"[{datetime.now().isoformat()}] Processing task {task_id} from {sender}: {content[:50]}...")
    
    handler = HANDLERS.get(agent_name)
    if handler:
        try:
            result = handler(content)
            print(f"Result: {result[:100]}...")
            
            # Acknowledge completion (would update state here)
            return True
        except Exception as e:
            print(f"Error processing: {e}")
            return False
    else:
        print(f"No handler for agent: {agent_name}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: worker.py <agent_name>")
        print(f"Valid agents: {', '.join(HANDLERS.keys())}")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    if agent_name not in HANDLERS:
        print(f"Unknown agent: {agent_name}")
        print(f"Valid agents: {', '.join(HANDLERS.keys())}")
        sys.exit(1)
    
    print(f"Starting worker for {agent_name}. Polling every {POLL_INTERVAL}s...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            messages = get_messages(agent_name)
            
            for msg in messages:
                process_message(msg, agent_name)
            
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping worker...")
        sys.exit(0)

if __name__ == "__main__":
    main()