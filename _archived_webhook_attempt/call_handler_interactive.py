"""
Interactive call handler using webhooks
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from pyngrok import ngrok

load_dotenv()

class InteractiveCallHandler:
    def __init__(self, ngrok_url):
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.to_number = os.getenv('TARGET_PHONE_NUMBER')
        self.ngrok_url = ngrok_url
        
    def make_call(self, bot, scenario):
        """
        Make an interactive call with webhook handling
        """
        print(f"\n{'='*60}")
        print(f"📞 INTERACTIVE CALL: {scenario['name']}")
        print(f"Persona: {scenario['persona']}")
        print(f"{'='*60}\n")
        
        # Store scenario in bot for webhook access
        bot.scenario = scenario
        
        try:
            # Make call with webhook URLs
            call = self.twilio_client.calls.create(
                to=self.to_number,
                from_=self.from_number,
                url=f"{self.ngrok_url}/start_call",
                status_callback=f"{self.ngrok_url}/call_status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                record=True
            )
            
            print(f"✅ Call initiated: {call.sid}")
            print(f"🌐 Webhook URL: {self.ngrok_url}")
            print(f"\n⏳ Call in progress...")
            
            # Wait for call to complete
            status = self._wait_for_completion(call.sid)
            
            print(f"\n✅ Call ended with status: {status}")
            
            return call.sid
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def _wait_for_completion(self, call_sid, timeout=180):
        """Wait for call to complete"""
        start = time.time()
        
        while time.time() - start < timeout:
            call = self.twilio_client.calls(call_sid).fetch()
            
            if call.status in ['completed', 'failed', 'busy', 'no-answer']:
                return call.status
            
            time.sleep(3)
        
        return 'timeout'