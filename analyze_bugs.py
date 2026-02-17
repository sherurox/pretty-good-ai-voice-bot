"""
Analyze call transcripts and identify bugs in the medical office AI
"""

import json
import os
from datetime import datetime

def load_transcripts():
    """Load all transcript files"""
    transcripts = []
    transcript_dir = 'transcripts'
    
    if not os.path.exists(transcript_dir):
        print("No transcripts directory found!")
        return []
    
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.json'):
            with open(f'{transcript_dir}/{filename}', 'r') as f:
                transcripts.append(json.load(f))
    
    return sorted(transcripts, key=lambda x: x['scenario_id'])

def analyze_for_bugs(transcripts):
    """Analyze transcripts for bugs and quality issues"""
    bugs = []
    
    for transcript in transcripts:
        scenario_id = transcript['scenario_id']
        scenario_name = transcript['scenario_name']
        conversation = transcript['conversation']
        
        # Bug 1: Duplicate time slots offered
        for msg in conversation:
            if msg['speaker'] == 'agent' and '2 PM' in msg['message']:
                if msg['message'].count('2 PM') > 1:
                    bugs.append({
                        'scenario': scenario_name,
                        'type': 'Logic Error',
                        'severity': 'High',
                        'description': 'Agent offered the same time slot twice (2 PM and 2 PM)',
                        'evidence': msg['message'],
                        'impact': 'Confuses patients and makes scheduling impossible'
                    })
        
        # Bug 2: Wrong medication hallucination
        for i, msg in enumerate(conversation):
            if msg['speaker'] == 'agent' and 'metformin' in msg['message'].lower():
                if i > 0 and 'lisinopril' in conversation[i-1]['message'].lower():
                    bugs.append({
                        'scenario': scenario_name,
                        'type': 'Hallucination',
                        'severity': 'Critical',
                        'description': 'Agent hallucinated wrong medication - patient asked for lisinopril (blood pressure) but agent mentioned metformin (diabetes)',
                        'evidence': f"Patient: {conversation[i-1]['message']}\nAgent: {msg['message']}",
                        'impact': 'Could lead to dangerous medication errors'
                    })
        
        # Bug 3: Poor urgency handling
        if scenario_id == 6:  # Urgent appointment scenario
            for msg in conversation:
                if msg['speaker'] == 'agent' and 'two weeks' in msg['message'].lower():
                    bugs.append({
                        'scenario': scenario_name,
                        'type': 'Inappropriate Response',
                        'severity': 'High',
                        'description': 'Agent offered appointment 2 weeks out for urgent care request',
                        'evidence': msg['message'],
                        'impact': 'Patient with urgent medical need is not properly triaged'
                    })
        
        # Bug 4: Asks for unnecessary information
        if scenario_id == 3:  # Rescheduling scenario
            for msg in conversation:
                if msg['speaker'] == 'agent' and 'date of birth' in msg['message'].lower():
                    if 'not seeing any upcoming' in msg['message'].lower():
                        bugs.append({
                            'scenario': scenario_name,
                            'type': 'Data Retrieval Failure',
                            'severity': 'Medium',
                            'description': 'Agent unable to find existing appointment for rescheduling',
                            'evidence': msg['message'],
                            'impact': 'Creates friction for legitimate rescheduling requests'
                        })
        
        # Bug 5: Inconsistent office hours
        for msg in conversation:
            if msg['speaker'] == 'agent' and 'office hours' in msg['message'].lower():
                if 'sunday' in msg['message'].lower():
                    bugs.append({
                        'scenario': scenario_name,
                        'type': 'Information Accuracy',
                        'severity': 'Medium',
                        'description': 'Agent claims office is open on Sundays (unusual for medical office)',
                        'evidence': msg['message'],
                        'impact': 'Patient may show up when office is actually closed'
                    })
        
        # Bug 6: Doesn't recognize wrong office type
        if scenario_id == 10:  # Wrong number scenario
            recognized_error = False
            for msg in conversation:
                if msg['speaker'] == 'agent':
                    if 'veterinary' in msg['message'].lower() or 'wrong' in msg['message'].lower():
                        recognized_error = True
            
            if not recognized_error:
                bugs.append({
                    'scenario': scenario_name,
                    'type': 'Context Understanding Failure',
                    'severity': 'Medium',
                    'description': 'Agent failed to recognize caller was looking for veterinary clinic, not human medical office',
                    'evidence': 'Agent proceeded with appointment scheduling despite clear mismatch',
                    'impact': 'Wastes time for both caller and office'
                })
        
        # Bug 7: Repetitive "didn't catch that"
        repeat_count = sum(1 for msg in conversation if msg['speaker'] == 'agent' and 'didn\'t quite catch' in msg['message'].lower())
        if repeat_count >= 3:
            bugs.append({
                'scenario': scenario_name,
                'type': 'Poor Conversation Flow',
                'severity': 'Medium',
                'description': f'Agent asked patient to repeat themselves {repeat_count} times in one call',
                'evidence': f'{repeat_count} instances of "I didn\'t quite catch that"',
                'impact': 'Frustrating user experience, suggests poor speech recognition'
            })
    
    return bugs

def generate_bug_report(bugs, transcripts):
    """Generate formatted bug report"""
    report = []
    
    report.append("# BUG REPORT - Medical Office AI Voice Agent")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nTotal Scenarios Tested: {len(transcripts)}")
    report.append(f"Total Bugs Found: {len(bugs)}")
    report.append("\n" + "="*80 + "\n")
    
    # Group bugs by severity
    critical_bugs = [b for b in bugs if b['severity'] == 'Critical']
    high_bugs = [b for b in bugs if b['severity'] == 'High']
    medium_bugs = [b for b in bugs if b['severity'] == 'Medium']
    
    if critical_bugs:
        report.append("\n## 🚨 CRITICAL ISSUES\n")
        for i, bug in enumerate(critical_bugs, 1):
            report.append(f"\n### Critical Bug #{i}: {bug['type']}")
            report.append(f"**Scenario:** {bug['scenario']}")
            report.append(f"**Description:** {bug['description']}")
            report.append(f"**Impact:** {bug['impact']}")
            report.append(f"\n**Evidence:**\n```\n{bug['evidence']}\n```\n")
    
    if high_bugs:
        report.append("\n## ⚠️ HIGH PRIORITY ISSUES\n")
        for i, bug in enumerate(high_bugs, 1):
            report.append(f"\n### High Bug #{i}: {bug['type']}")
            report.append(f"**Scenario:** {bug['scenario']}")
            report.append(f"**Description:** {bug['description']}")
            report.append(f"**Impact:** {bug['impact']}")
            report.append(f"\n**Evidence:**\n```\n{bug['evidence']}\n```\n")
    
    if medium_bugs:
        report.append("\n## ⚡ MEDIUM PRIORITY ISSUES\n")
        for i, bug in enumerate(medium_bugs, 1):
            report.append(f"\n### Medium Bug #{i}: {bug['type']}")
            report.append(f"**Scenario:** {bug['scenario']}")
            report.append(f"**Description:** {bug['description']}")
            report.append(f"**Impact:** {bug['impact']}")
            report.append(f"\n**Evidence:**\n```\n{bug['evidence']}\n```\n")
    
    # Summary recommendations
    report.append("\n## 📋 SUMMARY & RECOMMENDATIONS\n")
    report.append(f"- **Critical Issues:** {len(critical_bugs)} - Require immediate attention")
    report.append(f"- **High Priority:** {len(high_bugs)} - Should be fixed before production")
    report.append(f"- **Medium Priority:** {len(medium_bugs)} - Quality improvements needed\n")
    
    report.append("\n### Key Recommendations:")
    if critical_bugs:
        report.append("1. **Medication Safety:** Implement strict validation to prevent medication hallucinations")
    if high_bugs:
        report.append("2. **Logic Validation:** Add checks to prevent offering duplicate time slots")
        report.append("3. **Urgency Detection:** Improve triage system for urgent care requests")
    if medium_bugs:
        report.append("4. **Context Awareness:** Better handling of edge cases and wrong-number scenarios")
        report.append("5. **Information Accuracy:** Verify office hours and other factual information")
    
    return '\n'.join(report)

def main():
    print("="*80)
    print("BUG ANALYSIS - Medical Office AI")
    print("="*80 + "\n")
    
    # Load transcripts
    transcripts = load_transcripts()
    print(f"📁 Loaded {len(transcripts)} transcripts\n")
    
    if not transcripts:
        print("❌ No transcripts found. Run calls first with: python main.py all")
        return
    
    # Analyze for bugs
    print("🔍 Analyzing conversations for bugs...\n")
    bugs = analyze_for_bugs(transcripts)
    
    # Generate report
    report = generate_bug_report(bugs, transcripts)
    
    # Save report
    with open('BUG_REPORT.md', 'w') as f:
        f.write(report)
    
    print(f"✅ Found {len(bugs)} issues across {len(transcripts)} scenarios")
    print(f"💾 Bug report saved to: BUG_REPORT.md\n")
    
    # Print summary
    print(report)

if __name__ == "__main__":
    main()