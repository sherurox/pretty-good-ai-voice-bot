"""
Main bot logic - handles conversation intelligence using Claude
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class VoiceBot:
    def __init__(self, scenario):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.scenario = scenario
        self.conversation_history = []
        self.turn_count = 0
        self.max_turns = 15
        
    def get_system_prompt(self):
        """Create system prompt based on scenario"""
        return f"""You are roleplaying as a patient calling a medical office.

Scenario: {self.scenario['name']}
Your persona: {self.scenario['persona']}
Your goal: {self.scenario['goal']}
Context: {self.scenario['context']}

IMPORTANT INSTRUCTIONS:
- Stay in character as this patient
- Be natural and conversational
- Keep responses brief (1-2 sentences max)
- Respond directly to what the agent says
- If they ask for information, provide it naturally
- If your goal is accomplished, politely end the call
- Don't mention you're an AI or testing anything
- Sound like a real person would on the phone

Remember: You called THEM, so respond to their questions and prompts."""

    def generate_response(self, agent_message):
        """Generate bot's response to the agent's message"""
        self.turn_count += 1
        
        if self.turn_count >= self.max_turns:
            return "Thank you so much for your help. Have a great day! Goodbye."
        
        # Build conversation for Claude
        messages = []
        for entry in self.conversation_history:
            messages.append({
                "role": entry["role"],
                "content": entry["content"]
            })
        
        # Add current agent message
        messages.append({
            "role": "user",
            "content": f"Agent said: {agent_message}"
        })
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                temperature=0.7,
                system=self.get_system_prompt(),
                messages=messages
            )
            
            bot_response = response.content[0].text.strip()
            
            # Update history
            self.conversation_history.append({
                "role": "user",
                "content": f"Agent said: {agent_message}"
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })
            
            return bot_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, could you repeat that?"
    
    def get_initial_message(self):
        """Get the first message to start the conversation"""
        return self.scenario['initial_message']
    
    def should_end_conversation(self, bot_response):
        """Determine if conversation should end"""
        end_phrases = [
            "goodbye",
            "have a great day",
            "thank you, bye",
            "that's all i needed"
        ]
        return any(phrase in bot_response.lower() for phrase in end_phrases)