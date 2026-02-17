from dotenv import load_dotenv
import os
from openai import OpenAI
from twilio.rest import Client

load_dotenv()

print("Testing API connections...\n")

# Test OpenAI
try:
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print("✅ OpenAI API key loaded")
except Exception as e:
    print(f"❌ OpenAI error: {e}")

# Test Twilio
try:
    twilio_client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    print("✅ Twilio credentials loaded")
    
    # Test if we can access account
    account = twilio_client.api.accounts(os.getenv('TWILIO_ACCOUNT_SID')).fetch()
    print(f"✅ Twilio account verified: {account.friendly_name}")
    
except Exception as e:
    print(f"❌ Twilio error: {e}")

print("\n✅ Setup complete! Ready to start coding.")