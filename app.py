# app.py (Same code as before)
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os # We'll use os.environ to get secure variables

# --- Configuration ---
# Use environment variables for security (Render supports this!)
SHIVANSH_WHATSAPP_NUMBER = os.environ.get("SHIVANSH_WHATSAPP_NUMBER")
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

app = Flask(__name__)

# --- Helper Functions (Defined in the previous response) ---
def send_notification_to_shivansh(user_number, message_content):
    """
    In a real application, this would use the Twilio client
    to send a message to your number. You need to initialize the Twilio Client here.
    """
    # Placeholder for actual notification logic using TWILIO_SID and TWILIO_TOKEN
    print(f"--- NOTIFICATION ATTEMPT ---")
    print(f"User {user_number} wants to talk. Notification to: {SHIVANSH_WHATSAPP_NUMBER}")

def get_help_message():
    # ... (same content as before)
    return (
        "🤖 **Shivansh Bot Help Menu**\n"
        "Type one of the following commands:\n\n"
        "*/help*: Show this command list again.\n"
        "*/user*: Request a direct chat with Shivansh. "
        "Shivansh will receive a notification."
    )

def handle_initial_message():
    # ... (same content as before)
    response_text = (
        "You are talking with **Shivansh's Bot**, How may I help you?\n\n"
        "Type *1* for: Nothing Important\n"
        "Type *2* for: Talk with Shivansh"
    )
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)


# --- Main Webhook Route ---
@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '')
    
    resp = MessagingResponse()

    # --- 1. COMMAND HANDLING ---
    if incoming_msg.startswith('/'):
        if incoming_msg == '/help':
            resp.message(get_help_message())
        
        elif incoming_msg == '/user':
            username = from_number.split(':')[-1]
            send_notification_to_shivansh(username, "Requested chat via /user command")
            
            resp.message(
                f"Thank you, {username.split('+')[-1]}! "
                "Shivansh has been notified and will contact you shortly."
            )
        else:
            resp.message("❌ Unknown command. Type */help* to see available commands.")

    # --- 2. BUTTON/OPTION HANDLING ---
    elif incoming_msg == '1': # Nothing Important
        reply_text = (
            "Selection locked.\n"
            "Is there any questions that I can solve?\n"
            "Need any help, type **/help**."
        )
        resp.message(reply_text)
        
    elif incoming_msg == '2': # Talk with Shivansh
        username = from_number.split(':')[-1]
        send_notification_to_shivansh(username, "Requested chat via 'Talk with Shivansh' option")
        resp.message("I'm connecting you now. Please wait for Shivansh to respond.")

    # --- 3. DEFAULT RESPONSE ---
    else:
        # Spam check logic would go here
        return handle_initial_message()
    
    return str(resp)

# Required for Render to find the application entry point
if __name__ == "__main__":
    app.run(debug=True)
