"""
Patient scenarios for testing the medical office AI
"""

SCENARIOS = [
    {
        "id": 1,
        "name": "Simple Appointment Scheduling",
        "persona": "Sarah Chen, new patient",
        "goal": "Schedule a first-time appointment",
        "initial_message": "Hi, I'd like to schedule an appointment. This is my first time visiting.",
        "context": "Be polite, provide name when asked, prefer morning appointments"
    },
    {
        "id": 2,
        "name": "Medication Refill",
        "persona": "John Martinez, existing patient",
        "goal": "Request prescription refill",
        "initial_message": "Hello, I need to refill my blood pressure medication.",
        "context": "Patient ID if asked, mention the medication is lisinopril"
    },
    {
        "id": 3,
        "name": "Appointment Rescheduling",
        "persona": "Emily Thompson",
        "goal": "Reschedule existing appointment",
        "initial_message": "Hi, I need to reschedule my appointment for next Tuesday. Something came up.",
        "context": "Be apologetic, flexible with new times"
    },
    {
        "id": 4,
        "name": "Office Hours Inquiry",
        "persona": "Michael Rodriguez",
        "goal": "Ask about office hours and location",
        "initial_message": "Hi, what are your office hours? And do you have a location near downtown?",
        "context": "Just gathering information, not booking yet"
    },
    {
        "id": 5,
        "name": "Insurance Question",
        "persona": "Lisa Wang",
        "goal": "Verify insurance coverage",
        "initial_message": "Hello, I wanted to check if you accept Blue Cross Blue Shield insurance?",
        "context": "Needs confirmation before booking"
    },
    {
        "id": 6,
        "name": "Urgent Appointment",
        "persona": "David Kim",
        "goal": "Get same-day or next-day appointment",
        "initial_message": "Hi, I'm not feeling well and need to see a doctor as soon as possible. Do you have anything available today?",
        "context": "Urgent but not emergency, willing to come in anytime"
    },
    {
        "id": 7,
        "name": "Cancellation",
        "persona": "Jennifer Lee",
        "goal": "Cancel an upcoming appointment",
        "initial_message": "Hi, I need to cancel my appointment next week. I'm feeling better now.",
        "context": "Straightforward cancellation"
    },
    {
        "id": 8,
        "name": "Confused Patient - Multiple Questions",
        "persona": "Robert Brown (elderly, confused)",
        "goal": "Ask multiple questions in confusing order",
        "initial_message": "Yes hello, my doctor said I should call but I'm not sure... do I need to schedule something? Or was it a refill? Also what's your address?",
        "context": "Test how AI handles confused/unclear requests"
    },
    {
        "id": 9,
        "name": "Billing Question",
        "persona": "Amanda Foster",
        "goal": "Ask about a bill from previous visit",
        "initial_message": "Hi, I received a bill for my last visit and I have some questions about the charges.",
        "context": "Wants explanation of billing"
    },
    {
        "id": 10,
        "name": "Wrong Number Test",
        "persona": "Chris Anderson",
        "goal": "Test how AI handles wrong requests",
        "initial_message": "Hi, I'm looking for the veterinary clinic. Is this the animal hospital?",
        "context": "Test error handling - clearly wrong type of office"
    }
]

def get_scenario(scenario_id):
    """Get a specific scenario by ID"""
    for scenario in SCENARIOS:
        if scenario['id'] == scenario_id:
            return scenario
    return SCENARIOS[0]  # Default to first scenario

def get_all_scenarios():
    """Return all available scenarios"""
    return SCENARIOS