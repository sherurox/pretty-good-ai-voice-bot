"""
Flask webhook server for handling Twilio voice calls
Receives agent speech, generates patient responses in real-time
"""

import os
import json
from datetime import datetime
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Groq for patient bot
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Store conversation state per call
call_conversations = {}

def get_patient_response(call_sid, agent_speech, scenario):
    """
    Generate patient response using Groq based on what agent said
    """
    # Initialize conversation history for this call if needed
    if call_sid not in call_conversations:
        call_conversations[call_sid] = {
            'scenario': scenario,
            'history': [],
            'turn': 0
        }
    
    call_data = call_conversations[call_sid]
    call_data['turn'] += 1
    
    # Add agent's speech to history
    call_data['history'].append({
        'role': 'assistant',  # Agent speaks first
        'content': f"Agent said: {agent_speech}"
    })
    
    # Build system prompt based on scenario
    system_prompt = f"""You are a patient calling a medical office.

Scenario: {scenario['name']}
Your persona: {scenario['persona']}
Your goal: {scenario['goal']}
Context: {scenario['context']}

CRITICAL INSTRUCTIONS:
- Respond naturally to what the agent just said
- Keep responses brief (1-2 sentences max)
- Provide information when asked (name, DOB, reason for visit)
- Stay in character
- If asked for date of birth, say "March 15, 1990"
- Be polite and cooperative
- When goal is accomplished or stuck, politely end: "Thank you, goodbye"

Respond ONLY as the patient would speak - no explanations or meta-commentary."""

    try:
        # Generate response using Groq
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *call_data['history']
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        patient_response = response.choices[0].message.content.strip()
        
        # Add patient's response to history
        call_data['history'].append({
            'role': 'user',
            'content': patient_response
        })
        
        print(f"\n{'='*60}")
        print(f"Turn {call_data['turn']} | Call: {call_sid[:8]}")
        print(f"AGENT: {agent_speech}")
        print(f"PATIENT: {patient_response}")
        print(f"{'='*60}\n")
        
        return patient_response
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, could you repeat that?"

@app.route('/start_call', methods=['POST'])
def start_call():
    """
    Initial webhook when call connects
    Wait for agent to speak first
    """
    call_sid = request.form.get('CallSid')
    
    print(f"\n📞 Call started: {call_sid}")
    
    response = VoiceResponse()
    
    # Use Gather to listen for agent's greeting
    gather = Gather(
        input='speech',
        action='/handle_speech',
        speech_timeout='auto',
        language='en-US',
        speech_model='experimental_conversations'
    )
    
    response.append(gather)
    
    # If no speech detected, try again
    response.redirect('/start_call')
    
    return Response(str(response), mimetype='text/xml')

@app.route('/handle_speech', methods=['POST'])
def handle_speech():
    """
    Handle agent's speech and generate patient response
    """
    call_sid = request.form.get('CallSid')
    agent_speech = request.form.get('SpeechResult', '')
    
    # Get scenario from call data or default to scenario 1
    if call_sid in call_conversations:
        scenario = call_conversations[call_sid]['scenario']
    else:
        # Import scenarios
        import sys
        sys.path.append(os.path.dirname(__file__))
        from src.scenarios import get_scenario
        scenario = get_scenario(1)  # Default
    
    # Generate patient response
    patient_response = get_patient_response(call_sid, agent_speech, scenario)
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Check if patient wants to end call
    if any(word in patient_response.lower() for word in ['goodbye', 'bye', 'thank you goodbye']):
        response.say(patient_response, voice='Polly.Joanna')
        response.hangup()
    else:
        # Speak patient's response
        response.say(patient_response, voice='Polly.Joanna')
        
        # Gather next agent response
        gather = Gather(
            input='speech',
            action='/handle_speech',
            speech_timeout='auto',
            language='en-US',
            speech_model='experimental_conversations'
        )
        response.append(gather)
        
        # If no response, end call
        response.say("I didn't hear anything. Thank you, goodbye.", voice='Polly.Joanna')
        response.hangup()
    
    return Response(str(response), mimetype='text/xml')

@app.route('/call_status', methods=['POST'])
def call_status():
    """
    Handle call status updates
    """
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    
    print(f"📊 Call {call_sid[:8]} status: {call_status}")
    
    if call_status == 'completed':
        # Save conversation
        if call_sid in call_conversations:
            save_conversation(call_sid)
    
    return '', 200

def save_conversation(call_sid):
    """
    Save conversation transcript
    """
    if call_sid not in call_conversations:
        return
    
    call_data = call_conversations[call_sid]
    call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Build conversation log
    conversation = []
    for entry in call_data['history']:
        if 'Agent said:' in entry['content']:
            conversation.append({
                'speaker': 'agent',
                'message': entry['content'].replace('Agent said: ', ''),
                'timestamp': datetime.now().isoformat()
            })
        else:
            conversation.append({
                'speaker': 'patient',
                'message': entry['content'],
                'timestamp': datetime.now().isoformat()
            })
    
    transcript_data = {
        'call_id': call_id,
        'call_sid': call_sid,
        'scenario': call_data['scenario']['name'],
        'conversation': conversation,
        'turns': call_data['turn']
    }
    
    os.makedirs('transcripts', exist_ok=True)
    filename = f'transcripts/{call_id}.json'
    
    with open(filename, 'w') as f:
        json.dump(transcript_data, f, indent=2)
    
    print(f"\n💾 Saved transcript: {filename}")
    
    # Clean up
    del call_conversations[call_sid]

if __name__ == '__main__':
    app.run(debug=True, port=5000)