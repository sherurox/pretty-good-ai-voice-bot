# Voice Bot - Medical Office AI Testing

An automated voice bot system that calls a medical office AI agent to test conversation quality, identify bugs, and evaluate patient interaction capabilities.

---

## Overview

This project tests Pretty Good AI's medical office phone system by simulating realistic patient scenarios through automated voice calls. The bot makes real phone calls to **805-439-8008**, records conversations, transcribes audio, and identifies quality issues in the AI agent's responses.

---

## Features

* **Real Phone Calls** – Makes actual calls via Twilio
* **10 Test Scenarios** – Appointment scheduling, refills, cancellations, and edge cases
* **Automatic Transcription** – Uses Groq Whisper for speech-to-text conversion
* **Bug Detection** – Identifies response errors, logic failures, and conversation flow issues
* **Complete Transcripts** – Captures both patient (bot) and agent (AI) dialogue

---

## Project Structure
```
voice-bot-challenge/
├── src/
│   ├── bot.py              # Patient bot conversation logic
│   ├── call_handler.py     # Twilio call management & transcription
│   └── scenarios.py        # 10 test scenario definitions
├── transcripts/            # Call recordings and transcripts (JSON)
├── main.py                 # Main entry point
├── analyze_bugs.py         # Bug analysis and reporting
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── .env.example            # Environment variable template
├── README.md               # This file
├── architecture.md         # System design documentation
└── BUG_REPORT.md           # Identified bugs and issues
```

---

## Setup

### Prerequisites

* Python 3.9+
* Twilio account (with upgraded credits to call unverified numbers)
* Groq API account (free tier works)

---

### Installation

1. Clone the repository
```
git clone <your-repo-url>
cd voice-bot-challenge
```

2. Create virtual environment

Mac/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

Windows:
```
venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Configure environment variables
```
cp .env.example .env
```

Edit `.env`:
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
GROQ_API_KEY=your_groq_api_key
TARGET_PHONE_NUMBER=8054398008
```

---

## Getting API Keys

### Twilio

[https://www.twilio.com/](https://www.twilio.com/)

1. Sign up for free account
2. Get Account SID and Auth Token from Console
3. Get a phone number (trial includes one free)
4. Add credits to call unverified numbers

### Groq

[https://console.groq.com/](https://console.groq.com/)

1. Sign up for free account
2. Create API key from dashboard
3. Free tier includes Whisper transcription

---

## Usage

### Run Single Scenario
```
python main.py 1
```

Runs scenario #1 (Simple Appointment Scheduling)

---

### Run All 10 Scenarios
```
python main.py all
```

This will:

* Make 10 phone calls
* Record and transcribe each conversation
* Save transcripts to `transcripts/`
* Take approximately 30–35 minutes

---

### Analyze Results
```
python analyze_bugs.py
```

Generates `BUG_REPORT.md` with identified issues.

---

## Test Scenarios

1. Simple Appointment Scheduling
2. Medication Refill
3. Appointment Rescheduling
4. Office Hours Inquiry
5. Insurance Question
6. Urgent Appointment
7. Cancellation
8. Confused Patient
9. Billing Question
10. Wrong Number

---

## Architecture

This system uses a **pre-scripted approach with timed pauses**:

* Patient bot speaks predefined messages
* 18-second initial pause
* 10–14 second pauses between messages
* Twilio records entire conversation
* Groq Whisper transcribes audio
* Pattern matching identifies bugs

See `architecture.md` for detailed design decisions.

---

## Key Design Decisions

### Why pre-scripted instead of interactive?

* Reliable and reproducible testing
* Simpler implementation
* Faster development
* Successfully identifies critical bugs

### Tradeoffs

* Not perfectly synchronized with agent responses
* May miss conversational nuances
* Still effective at identifying logic errors

---

## Output

Each call generates:

* JSON transcript:
  `transcripts/call_YYYYMMDD_HHMMSS.json`

* Audio recording:
  `transcripts/call_YYYYMMDD_HHMMSS_recording.mp3`

Transcript includes:

* Patient script messages
* Full transcription
* Parsed dialogue
* Timestamps and metadata

---

## Results Summary

Success Rate: **4/10 scenarios (40%)**

### Working Scenarios

* New appointment scheduling
* Office hours inquiry
* Insurance verification
* Wrong number handling

### Failed Scenarios

* Medication refills (phone number loop)
* Appointment rescheduling
* Urgent care handling
* Cancellations
* Billing questions
* Confused patient support

---

## Critical Bugs Found

1. Phone Number Loop Bug
2. Rescheduling Failure
3. Urgent Care Not Prioritized
4. Low Task Completion Rate
5. Inflexible Workflow
6. Name Transcription Errors

See `BUG_REPORT.md` for detailed evidence.

---

## Cost Estimate

For 10 calls:

* Twilio: ~$1–2
* Groq Whisper: Free
* Total: ~$1–2

---

## Development Stack

* Python 3.12
* Twilio (voice + recording)
* Groq Whisper (transcription)
* Pre-scripted TwiML

---

## Troubleshooting

**Twilio trial error**
Add credits to your account.

**Groq quota exceeded**
Check usage in console.

**No transcripts generated**
Ensure recordings process fully and check folder permissions.

**Calls too short**
Adjust pause timings in `_create_twiml_script()` inside `src/call_handler.py`.

---

## License

Created as part of a technical challenge for Pretty Good AI.

---

## Author

Built with assistance from Claude (Anthropic) for iterative development, debugging, and implementation support.