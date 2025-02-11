import pywhatkit as kit
import datetime
import time
import pytz
import json
from datetime import date
from typing import Dict, List, Optional

# Required packages:
# pip install pywhatkit
# pip install pytz

# Store targets in a dictionary
TARGETS = {
    "groups": [

    ],
    "numbers": [

    ]
}

# Define the structure for exam data
class Exam:
    def __init__(self, subject: str, date: str, time: str = "10:30"):
        self.subject = subject
        self.date = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

def load_exams(filename: str = "exams.json") -> List[Exam]:
    """Load exam schedule from JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            exams = []
            for exam in data['exams']:
                exams.append(Exam(
                    subject=exam['subject'],
                    date=exam['date'],
                    time=exam.get('time', '10:30')  # Default to 10:30 if not specified
                ))
            return sorted(exams, key=lambda x: x.date)
    except FileNotFoundError:
        print(f"\n❌ Exam schedule file '{filename}' not found!")
        return []
    except json.JSONDecodeError:
        print(f"\n❌ Invalid JSON format in '{filename}'!")
        return []

def get_next_exam(exams: List[Exam]) -> Optional[Exam]:
    """Get the next upcoming exam"""
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    
    upcoming_exams = [exam for exam in exams if exam.date.replace(tzinfo=IST) > now]
    return upcoming_exams[0] if upcoming_exams else None

def calculate_time_until_exam(exam: Exam) -> Dict[str, int]:
    """Calculate time remaining until the exam"""
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    exam_time = exam.date.replace(tzinfo=IST)
    diff = exam_time - now
    
    return {
        'days': diff.days,
        'hours': diff.seconds // 3600,
        'minutes': (diff.seconds % 3600) // 60,
    }

def format_message(exam: Optional[Exam] = None) -> str:
    """Format message with exam details and countdown"""
    if not exam:
        return "No upcoming exams scheduled! 🎉"
    
    time_left = calculate_time_until_exam(exam)
    
    message = (
        f"📚 *COUNTDOWN TO {exam.subject} EXAM*\n"
        "Time Remaining:\n"
        "===================\n"
        f"📅 *Days:* {time_left['days']}\n"
        f"⏰ *Hours:* {time_left['hours']}\n"
        f"⌚ *Minutes:* {time_left['minutes']}\n"
        "===================\n"
    )
    
    return message

def validate_targets() -> bool:
    """Validate stored targets"""
    if not TARGETS["groups"] and not TARGETS["numbers"]:
        print("\n❌ No targets configured! Please add groups or numbers.")
        return False
    
    # Validate phone numbers
    invalid_numbers = [num for num in TARGETS["numbers"] 
                      if not (num.isdigit() and len(num) == 10)]
    if invalid_numbers:
        print(f"\n❌ Invalid phone numbers found: {invalid_numbers}")
        print("Numbers should be 10 digits without spaces or country code")
        return False
    
    return True

def send_to_number(phone_number: str, message: str) -> bool:
    """Send message to individual number"""
    try:
        if not phone_number.startswith("91"):
            phone_number = "91" + phone_number
            
        kit.sendwhatmsg_instantly(
            phone_no=f"+{phone_number}",
            message=message,
            tab_close=True,
            close_time=3
        )
        print(f"✅ Message sent to +91-{phone_number}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {phone_number}: {str(e)}")
        return False

def send_to_group(group_id: str, message: str) -> bool:
    """Send message to group"""
    try:
        kit.sendwhatmsg_to_group_instantly(
            group_id=group_id,
            message=message,
            tab_close=True,
            close_time=3
        )
        print(f"✅ Message sent to group {group_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to group {group_id}: {str(e)}")
        return False

def send_all_messages(message: str) -> Dict[str, List[str]]:
    """Send messages to all configured targets"""
    results = {
        "successful": [],
        "failed": []
    }
    
    # Send to groups
    for group_id in TARGETS["groups"]:
        if send_to_group(group_id, message):
            results["successful"].append(f"Group: {group_id}")
        else:
            results["failed"].append(f"Group: {group_id}")
        time.sleep(5)  # Delay between messages
    
    # Send to numbers
    for number in TARGETS["numbers"]:
        if send_to_number(number, message):
            results["successful"].append(f"Number: {number}")
        else:
            results["failed"].append(f"Number: {number}")
        time.sleep(5)  # Delay between messages
    
    return results

def print_status(results: Dict[str, List[str]]) -> None:
    """Print message sending status"""
    print("\n📊 Message Status Report:")
    print("━━━━━━━━━━━━━━━━━━")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed deliveries:")
        for target in results['failed']:
            print(f"  • {target}")

def setup_targets() -> None:
    """Interactive setup for targets"""
    print("\n📱 Target Setup")
    print("━━━━━━━━━━━")
    
    # Setup phone numbers
    while True:
        number = input("\nEnter phone number (10 digits) or press Enter to skip: ").strip()
        if not number:
            break
        if number.isdigit() and len(number) == 10:
            TARGETS["numbers"].append(number)
        else:
            print("❌ Invalid number! Please enter 10 digits.")
    
    # Setup group IDs
    print("\n👥 Group Setup")
    print("To get group ID:")
    print("1. Open WhatsApp Web")
    print("2. Open target group")
    print("3. Copy ID from URL (after 'accept?code=')")
    
    while True:
        group_id = input("\nEnter group ID or press Enter to skip: ").strip()
        if not group_id:
            break
        TARGETS["groups"].append(group_id)

def run_reminder_service():
    IST = pytz.timezone('Asia/Kolkata')
    exams = load_exams()
    
    if not exams:
        print("\n❌ No exams loaded! Please check your exams.json file.")
        return
    
    print("\n" + "="*50)
    print("📱 WhatsApp Exam Reminder Service")
    print("="*50)
    print("\n📍 Time Zone: Indian Standard Time (IST)")
    print("⏰ Daily Update Time: 11:00 AM IST")
    print("\n📚 Loaded Exams:")
    for exam in exams:
        print(f"   • {exam.subject}: {exam.date.strftime('%B %d, %Y at %I:%M %p')}")
    
    print("\n🎯 Configured Targets:")
    print(f"   • Groups: {len(TARGETS['groups'])}")
    print(f"   • Numbers: {len(TARGETS['numbers'])}")
    
    print("\n✨ Sending initial messages...")
    next_exam = get_next_exam(exams)
    message = format_message(next_exam)
    results = send_all_messages(message)
    print_status(results)
    
    while True:
        now = datetime.datetime.now(IST)
        
        if now.hour == 11 and now.minute == 0:
            print("\n🕋 It's 11:00 AM! Sending scheduled messages...")
            next_exam = get_next_exam(exams)
            message = format_message(next_exam)
            results = send_all_messages(message)
            print_status(results)
            time.sleep(60)
        
        time.sleep(30)

if __name__ == "__main__":
    print("\n🚀 WhatsApp Exam Reminder Setup")
    print("=" * 50)
    
    # Interactive setup
    #setup_targets()
    
    # Validate configuration
    if not validate_targets():
        print("\n❌ Please fix configuration and try again.")
        exit(1)
    
    print("\n⚙️ Service Configuration:")
    print("   • WhatsApp Web must be logged in")
    print("   • Keep script running for daily reminders")
    print("   • Press Ctrl+C to stop")
    
    try:
        run_reminder_service()
    except KeyboardInterrupt:
        print("\n\n👋 Service stopped by user.")
    except Exception as e:
        print(f"\n❌ Service error: {str(e)}")
        print("Please verify your configuration and try again.")
