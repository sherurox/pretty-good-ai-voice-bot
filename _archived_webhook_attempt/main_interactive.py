"""
Interactive voice bot - Real conversations with webhooks
Run this AFTER starting webhook_server.py
"""

import sys
import os
import time
from pyngrok import ngrok
from src.scenarios import get_scenario, get_all_scenarios
from src.bot import VoiceBot
from src.call_handler_interactive import InteractiveCallHandler

# Store ngrok URL globally
NGROK_URL = None

def setup_ngrok():
    """Start ngrok tunnel"""
    global NGROK_URL
    
    print("\n🌐 Starting ngrok tunnel...")
    
    # Kill any existing ngrok processes
    ngrok.kill()
    
    # Start tunnel on port 5000 (Flask default)
    tunnel = ngrok.connect(5000, bind_tls=True)
    NGROK_URL = tunnel.public_url
    
    print(f"✅ Ngrok tunnel active: {NGROK_URL}")
    print(f"   Webhook endpoints:")
    print(f"   - {NGROK_URL}/start_call")
    print(f"   - {NGROK_URL}/handle_speech")
    print(f"   - {NGROK_URL}/call_status")
    
    return NGROK_URL

def run_single_call(scenario_id, ngrok_url):
    """Run single interactive call"""
    scenario = get_scenario(scenario_id)
    
    bot = VoiceBot(scenario)
    bot.scenario = scenario  # Store for webhook access
    
    call_handler = InteractiveCallHandler(ngrok_url)
    
    call_sid = call_handler.make_call(bot, scenario)
    
    if call_sid:
        print(f"\n✅ Call completed: {call_sid}")
    else:
        print(f"\n❌ Call failed")
    
    return call_sid

def run_all_scenarios(ngrok_url):
    """Run all 10 scenarios"""
    scenarios = get_all_scenarios()
    
    print(f"\n🚀 Running {len(scenarios)} interactive calls...")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}/{len(scenarios)}")
        print(f"{'='*60}")
        
        run_single_call(scenario['id'], ngrok_url)
        
        if i < len(scenarios):
            print("\n⏳ Waiting 15 seconds before next call...")
            time.sleep(15)
    
    print(f"\n✅ All calls completed!")

def main():
    print("="*60)
    print("INTERACTIVE VOICE BOT - Real Conversations")
    print("="*60)
    
    # Setup ngrok tunnel
    ngrok_url = setup_ngrok()
    
    print("\n⚠️  IMPORTANT: Make sure webhook_server.py is running!")
    print("   In another terminal: python webhook_server.py")
    input("\n   Press ENTER when server is ready...")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_all_scenarios(ngrok_url)
        else:
            try:
                scenario_id = int(sys.argv[1])
                run_single_call(scenario_id, ngrok_url)
            except ValueError:
                print("Usage: python main_interactive.py [scenario_id|all]")
    else:
        print("\nRunning scenario 1 (default)")
        run_single_call(1, ngrok_url)
    
    print("\n✅ Done! Press Ctrl+C to stop ngrok tunnel.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        ngrok.kill()

if __name__ == "__main__":
    main()