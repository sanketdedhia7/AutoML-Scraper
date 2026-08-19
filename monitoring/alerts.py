import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

class Alerter:
    def __init__(self):
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    
    def send_alert(self, message: str, severity: str = "warning", retries: int = 3, backoff_factor: int = 2):
        """Send alert to Discord with exponential backoff retry for transient network errors."""
        if not self.discord_webhook or self.discord_webhook == "your_webhook_url":
            print(f"Alert ({severity}): {message}")
            return
        
        color_map = {
            "info": 3447003,      # Blue
            "warning": 16766720,  # Yellow
            "error": 15548997,    # Red
            "critical": 10038562  # Dark red
        }
        
        payload = {
            "embeds": [{
                "title": f"🚨 Scraper Alert ({severity.upper()})",
                "description": message,
                "color": color_map.get(severity, 3447003)
            }]
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(self.discord_webhook, json=payload, timeout=10)
                if response.status_code == 204:
                    print(f"Alert sent: {message}")
                    return
                else:
                    print(f"Webhook HTTP {response.status_code}: {response.text} (attempt {attempt + 1}/{retries})")
            except Exception as e:
                print(f"Webhook request error (attempt {attempt + 1}/{retries}): {e}")
            
            if attempt < retries - 1:
                time.sleep(backoff_factor ** attempt)
        
        print(f"Fallback Alert ({severity}): {message}")
