import pywhatkit as kit
import datetime
import time
import pytz
from datetime import date
from typing import Dict, List

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

def calculate_time_until_target() -> Dict[str, int]:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    target_date = datetime.datetime(2025, 2, 15, tzinfo=IST)
    diff = target_date - now
    
    return {
        'days': diff.days,
        'hours': diff.seconds // 3600,
        'minutes': (diff.seconds % 3600) // 60,
        
    }

def format_message() -> str:
    time_left = calculate_time_until_target()
    
    message = (
        "🎯 *COUNTDOWN TO Boards - FEBRUARY 15, 2025*\n\n"
        "Time Remaining:\n"
        "===================\n"
        f"📅 *Days:* {time_left['days']}\n"
        f"⏰ *Hours:* {time_left['hours']}\n"
        f"⌚ *Minutes:* {time_left['minutes']}\n"
        
        "===================\n"
        " ☠ "
    )
    
    return message

def send_to_number(phone_number: str) -> bool:
    """Send message to individual number"""
    try:
        message = format_message()
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

def send_to_group(group_id: str) -> bool:
    """Send message to group"""
    try:
        message = format_message()
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

def send_all_messages() -> Dict[str, List[str]]:
    """Send messages to all configured targets"""
    results = {
        "successful": [],
        "failed": []
    }
    
    # Send to groups
    for group_id in TARGETS["groups"]:
        if send_to_group(group_id):
            results["successful"].append(f"Group: {group_id}")
        else:
            results["failed"].append(f"Group: {group_id}")
        time.sleep(5)  # Delay between messages
    
    # Send to numbers
    for number in TARGETS["numbers"]:
        if send_to_number(number):
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
    
    print("\n" + "="*50)
    print("📱 WhatsApp Multi-Target Reminder Service")
    print("="*50)
    print("\n📍 Time Zone: Indian Standard Time (IST)")
    print("⏰ Scheduled Time: 11:00 AM IST")
    print("\n🎯 Configured Targets:")
    print(f"   • Groups: {len(TARGETS['groups'])}")
    print(f"   • Numbers: {len(TARGETS['numbers'])}")
    
    print("\n✨ Sending initial messages...")
    results = send_all_messages()
    print_status(results)
    
    while True:
        now = datetime.datetime.now(IST)
        
        if now.hour == 11 and now.minute == 0:
            print("\n🕋 It's 11:00 AM! Sending scheduled messages...")
            results = send_all_messages()
            print_status(results)
            time.sleep(60)
        
        time.sleep(30)

if __name__ == "__main__":
    print("\n🚀 WhatsApp Multi-Target Reminder Setup")
    print("=" * 50)
    
    # Interactive setup
    setup_targets()
    
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
