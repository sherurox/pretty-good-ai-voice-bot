"""
Main entry point for the voice bot challenge
"""

import sys
from src.scenarios import get_scenario, get_all_scenarios
from src.bot import VoiceBot
from src.call_handler import CallHandler

def run_single_call(scenario_id):
    """Run a single call with specified scenario"""
    scenario = get_scenario(scenario_id)
    
    print(f"\n🤖 Initializing bot for scenario: {scenario['name']}")
    
    # Create bot with scenario
    bot = VoiceBot(scenario)
    
    # Create call handler
    call_handler = CallHandler()
    
    # Make the call
    call_sid = call_handler.make_call(bot, scenario)
    
    if call_sid:
        print(f"\n✅ Call completed successfully!")
        print(f"Call SID: {call_sid}")
    else:
        print(f"\n❌ Call failed")

def run_all_scenarios():
    """Run calls for all scenarios"""
    scenarios = get_all_scenarios()
    
    print(f"\n🚀 Running {len(scenarios)} scenarios...")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}/{len(scenarios)}")
        print(f"{'='*60}")
        run_single_call(scenario['id'])
        
        # Wait between calls to avoid rate limits and ensure recordings are ready
        if i < len(scenarios):
            import time
            print(f"\n⏳ Waiting 15 seconds before next call...")
            time.sleep(15)
    
    print(f"\n{'='*60}")
    print(f"✅ ALL {len(scenarios)} SCENARIOS COMPLETED!")
    print(f"{'='*60}")
    print(f"\n💾 Check transcripts/ folder for all call recordings")

def main():
    """Main entry point"""
    print("="*60)
    print("VOICE BOT - Medical Office Testing")
    print("="*60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_all_scenarios()
        else:
            try:
                scenario_id = int(sys.argv[1])
                run_single_call(scenario_id)
            except ValueError:
                print("Usage: python main.py [scenario_id|all]")
    else:
        # Default: run first scenario
        print("\nRunning default scenario (ID: 1)")
        print("Usage: python main.py [scenario_id|all]")
        run_single_call(1)

if __name__ == "__main__":
    main()