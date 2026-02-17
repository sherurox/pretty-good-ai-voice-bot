"""
Handles real phone calls to 805-439-8008 via Twilio
Uses pre-scripted patient messages to test their AI system
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from openai import OpenAI

load_dotenv()

class CallHandler:
    def __init__(self):
        # Initialize Twilio
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.to_number = os.getenv('TARGET_PHONE_NUMBER')
        
        # Initialize OpenAI for transcription
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.conversation_log = []
        
    def make_call(self, bot, scenario):
        """
        Make a real phone call to 805-439-8008
        Uses pre-scripted messages based on scenario
        """
        print(f"\n{'='*60}")
        print(f"📞 CALLING REAL NUMBER: {self.to_number}")
        print(f"Scenario: {scenario['name']}")
        print(f"Persona: {scenario['persona']}")
        print(f"{'='*60}\n")
        
        call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_log = []
        
        # Build conversation script for this scenario
        script = self._build_conversation_script(scenario, bot)
        
        try:
            # Create TwiML for the call
            twiml = self._create_twiml_script(script)
            
            print(f"☎️  Initiating call to {self.to_number}...")
            print(f"📝 Script has {len(script)} patient messages\n")
            
            # Make the call
            call = self.twilio_client.calls.create(
                to=self.to_number,
                from_=self.from_number,
                twiml=twiml,
                record=True,
                recording_status_callback_event=['completed'],
                timeout=60
            )
            
            print(f"✅ Call initiated: {call.sid}")
            print(f"Status: {call.status}\n")
            
            # Log the script we're using
            for i, message in enumerate(script, 1):
                self.conversation_log.append({
                    "speaker": "patient",
                    "message": message,
                    "turn": i,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Wait for call to complete
            print("⏳ Waiting for call to complete...")
            final_status = self._wait_for_call_completion(call.sid)
            
            print(f"\n✅ Call completed with status: {final_status}")
            
            # Wait a bit for recording to be ready
            print("\n⏳ Waiting for recording to be ready...")
            time.sleep(5)
            
            # Get and transcribe recordings
            print("\n🎙️  Retrieving call recordings...")
            self._process_call_recordings(call.sid, call_id)
            
            # Save transcript
            self._save_transcript(call_id, scenario, call.sid)
            
            return call.sid
            
        except Exception as e:
            print(f"\n❌ Error making call: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_conversation_script(self, scenario, bot):
        """
        Minimal generic script - fewer messages that work for most agent responses
        """
        script = []
        
        scenario_id = scenario['id']
        
        if scenario_id == 1:  # Simple Appointment Scheduling
            script.append("Hi, I'm Sarah Chen. I'd like to schedule an appointment.")
            script.append("March 15, 1990.")  # DOB
            script.append("Yes, that's correct.")  # Confirmation
            script.append("A new patient consultation for a general checkup.")
            script.append("The earliest available time works for me.")
            script.append("Yes, please book that time.")
            script.append("Yes, that's correct.")  # Second confirmation if needed
            script.append("No, that's all. Thank you!")
        
        elif scenario_id == 2:  # Medication Refill
            script.append("Hi, I'm John Martinez. I need a medication refill.")
            script.append("June 10, 1975.")
            script.append("Correct.")
            script.append("Lisinopril for blood pressure.")
            script.append("Yes, please process that.")
            script.append("Thank you!")
        
        elif scenario_id == 3:  # Rescheduling
            script.append("Hi, I'm Emily Thompson. I need to reschedule.")
            script.append("April 22, 1988.")
            script.append("Yes.")
            script.append("My appointment next Tuesday to Wednesday afternoon.")
            script.append("Yes, that works.")
            script.append("Thank you!")
        
        elif scenario_id == 4:  # Office Hours
            script.append("What are your weekend hours?")
            script.append("And the downtown location address?")
            script.append("Thank you!")
        
        elif scenario_id == 5:  # Insurance
            script.append("Do you accept Blue Cross Blue Shield?")
            script.append("Yes, PPO.")
            script.append("Thank you!")
        
        elif scenario_id == 6:  # Urgent
            script.append("I'm not feeling well. Do you have anything today?")
            script.append("Two weeks is too long. Any urgent options?")
            script.append("Okay, thank you.")
        
        elif scenario_id == 7:  # Cancellation
            script.append("Hi, I'm Jennifer Lee. I need to cancel.")
            script.append("September 5, 1982.")
            script.append("My appointment next week.")
            script.append("Yes, cancel it. Thank you!")
        
        elif scenario_id == 8:  # Confused Patient
            script.append("My doctor said to call. Not sure why.")
            script.append("Maybe an appointment or refill?")
            script.append("What's your address?")
            script.append("Okay, thanks.")
        
        elif scenario_id == 9:  # Billing
            script.append("I have a billing question.")
            script.append("My visit last month. The amount seems high.")
            script.append("Okay, I'll call them. Thank you!")
        
        elif scenario_id == 10:  # Wrong Number
            script.append("Is this the veterinary clinic?")
            script.append("Oh, wrong number. Sorry!")
        
        return script
    
    def _create_twiml_script(self, script):
        """
        Conservative timing - longer pauses to let agent finish speaking
        """
        twiml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<Response>']
        
        # Long initial wait for full greeting (18 seconds to be safe)
        twiml_parts.append('<Pause length="18"/>')
        
        for i, message in enumerate(script):
            # Speak slightly slower for clarity
            twiml_parts.append(f'<Say voice="Polly.Joanna" rate="90%">{message}</Say>')
            
            # Longer pauses throughout - be conservative
            if i == 0:
                # After intro, wait for DOB question
                twiml_parts.append('<Pause length="10"/>')
            elif i == 1:
                # After DOB, wait for confirmation
                twiml_parts.append('<Pause length="12"/>')
            elif i == 2:
                # After confirmation, wait for next question
                twiml_parts.append('<Pause length="12"/>')
            elif i < len(script) - 1:
                # General pauses - give agent time to speak
                twiml_parts.append('<Pause length="14"/>')
            else:
                # Last message - long wait for final response
                twiml_parts.append('<Pause length="18"/>')
        
        # End call politely
        twiml_parts.append('<Pause length="4"/>')
        twiml_parts.append('<Say voice="Polly.Joanna" rate="90%">Goodbye.</Say>')
        twiml_parts.append('<Pause length="3"/>')
        twiml_parts.append('<Hangup/>')
        twiml_parts.append('</Response>')
        
        return '\n'.join(twiml_parts)
    
    def _wait_for_call_completion(self, call_sid, timeout=180):
        """Wait for call to complete (increased timeout for longer calls)"""
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            call = self.twilio_client.calls(call_sid).fetch()
            
            if call.status != last_status:
                print(f"   Status: {call.status}")
                last_status = call.status
            
            if call.status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
                return call.status
            
            time.sleep(2)
        
        return 'timeout'
    
    def _process_call_recordings(self, call_sid, call_id):
        """Retrieve and transcribe call recordings"""
        try:
            # Get recordings for this call
            recordings = self.twilio_client.recordings.list(call_sid=call_sid)
            
            if not recordings:
                print("❌ No recordings found yet")
                return
            
            print(f"✅ Found {len(recordings)} recording(s)")
            
            for idx, recording in enumerate(recordings):
                print(f"\n📥 Processing recording {idx + 1}/{len(recordings)}")
                print(f"   Recording SID: {recording.sid}")
                print(f"   Duration: {recording.duration} seconds")
                
                # Download and transcribe
                self._download_and_transcribe(recording, call_id)
                
        except Exception as e:
            print(f"❌ Error processing recordings: {e}")
    
    def _download_and_transcribe(self, recording, call_id):
        """Download recording and transcribe using Groq Whisper (free!)"""
        try:
            # Import Groq
            from groq import Groq
            groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            
            # Build recording URL
            recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
            
            print(f"   Downloading audio...")
            
            # Download the audio file
            auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
            response = requests.get(recording_url, auth=auth)
            
            if response.status_code == 200:
                # Save audio file temporarily
                audio_file = f"transcripts/{call_id}_recording.mp3"
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"   ✅ Audio saved: {audio_file}")
                print(f"   🎯 Transcribing with Groq Whisper...")
                
                # Transcribe using Groq Whisper (FREE!)
                with open(audio_file, 'rb') as audio:
                    transcript = groq_client.audio.transcriptions.create(
                        model="whisper-large-v3-turbo",
                        file=audio,
                        response_format="verbose_json"
                    )
                
                print(f"   ✅ Transcription complete!")
                
                # Parse the transcription
                self._parse_transcription(transcript, call_id)
                
            else:
                print(f"   ❌ Failed to download: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error in transcription: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_transcription(self, transcript, call_id):
        """
        Parse Whisper transcription and identify agent vs patient
        """
        try:
            full_text = transcript.text
            
            print(f"\n📝 Full Transcription:")
            print(f"   {full_text}")
            
            # Add full transcription to log
            self.conversation_log.append({
                "speaker": "full_recording",
                "message": full_text,
                "timestamp": datetime.now().isoformat(),
                "note": "Complete call transcription - includes both patient and agent"
            })
            
            # Simple speaker detection
            segments = full_text.split('. ')
            
            for segment in segments:
                if segment.strip():
                    is_patient = any(msg.lower() in segment.lower() 
                                   for msg in [log['message'] for log in self.conversation_log 
                                             if log['speaker'] == 'patient'])
                    
                    speaker = "patient" if is_patient else "agent"
                    
                    self.conversation_log.append({
                        "speaker": speaker,
                        "message": segment.strip(),
                        "timestamp": datetime.now().isoformat(),
                        "note": "Parsed from audio (speaker detection is approximate)"
                    })
            
        except Exception as e:
            print(f"   ❌ Error parsing transcription: {e}")
    
    def _save_transcript(self, call_id, scenario, call_sid):
        """Save call transcript to file"""
        filename = f"transcripts/{call_id}.json"
        
        transcript_data = {
            "call_id": call_id,
            "call_sid": call_sid,
            "scenario_id": scenario['id'],
            "scenario_name": scenario['name'],
            "persona": scenario['persona'],
            "goal": scenario['goal'],
            "timestamp": datetime.now().isoformat(),
            "target_number": self.to_number,
            "conversation": self.conversation_log,
            "note": "Real call to 805-439-8008. Transcription parsed from audio recording."
        }
        
        os.makedirs('transcripts', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(transcript_data, f, indent=2)
        
        print(f"\n💾 Transcript saved: {filename}")
        print(f"📊 Logged items: {len(self.conversation_log)}")