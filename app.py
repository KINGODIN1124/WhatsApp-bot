from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from flask_mail import Mail, Message

# --- Configuration & Initialization ---

app = Flask(__name__)

# --- Flask-Mail Configuration ---
# These variables MUST be set in your Render Environment Variables
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# Render variables are strings, check for 'True'
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True' 
app.config['MAIL_USE_SSL'] = False 

mail = Mail(app) # Initialize Mail object

# --- Other Global Variables (Retrieved from Render Environment) ---
# Your personal Gmail to receive notifications
SHIVANSH_GMAIL = os.environ.get('SHIVANSH_GMAIL') 


# --- Helper Functions ---

def send_notification_to_shivansh(user_number, message_content):
    """
    Sends a Gmail notification to Shivansh for human handoff requests.
    """
    sender_email = os.environ.get('MAIL_USERNAME')
    
    # Check if essential variables are set
    if not sender_email or not SHIVANSH_GMAIL:
        print("ERROR: Gmail sender or recipient not configured. Skipping email notification.")
        return

    # 1. Create the Email Message
    msg = Message(
        subject=f"URGENT: WhatsApp Handoff Request from {user_number}",
        sender=sender_email,
        recipients=[SHIVANSH_GMAIL],
        body=f"The WhatsApp user {user_number} has requested to talk directly.\n\n"
             f"User's Action: {message_content}\n"
             f"Please switch to your WhatsApp to continue the conversation with this user."
    )
    
    # 2. Send the Email
    try:
        # Use app.app_context() for sending mail outside of a request context if needed,
        # but for simplicity here, we send directly within the request handler flow.
        mail.send(msg)
        print(f"Gmail notification sent to {SHIVANSH_GMAIL} for user {user_number}")
    except Exception as e:
        # Log any errors (e.g., wrong App Password, connection refused)
        print(f"ERROR: Failed to send Gmail notification: {e}")

def get_help_message():
    """Returns the formatted help menu."""
    return (
        "🤖 **Shivansh Bot Help Menu**\n"
        "Type one of the following commands:\n\n"
        "*/help*: Show this command list again.\n"
        "*/user*: Request a direct chat with Shivansh. "
        "Shivansh will receive a Gmail notification with your username."
    )

def handle_initial_message():
    """Handles the first interaction with text-based options."""
    response_text = (
        "You are talking with **Shivansh's Bot**, How may I help you?\n\n"
        "Type *1* for: Nothing Important\n"
        "Type *2* for: Talk with Shivansh"
    )
    
    # Using Twilio TwiML for the response
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)


# --- Main Webhook Route ---

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    """
    Processes every incoming WhatsApp message from Twilio.
    """
    # The 'Body' is the text content, 'From' is the sender's number (whatsapp:+...)
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '')
    
    # Extract the plain number for notifications/display
    username = from_number.split(':')[-1]
    
    resp = MessagingResponse()

    # --- 1. COMMAND HANDLING (/help, /user) ---
    if incoming_msg.startswith('/'):
        if incoming_msg == '/help':
            resp.message(get_help_message())
        
        elif incoming_msg == '/user':
            # 1a. Notify Shivansh via Gmail
            send_notification_to_shivansh(username, "Requested chat via /user command")
            
            # 1b. Reply to User
            resp.message(
                f"Shivansh has been notified via Gmail that {username} wants to talk to you. "
                "He will contact you shortly."
            )
        
        else:
            resp.message(
                "❌ Unknown command. "
                "Type */help* to see available commands."
            )

    # --- 2. BUTTON/OPTION HANDLING ---
    elif incoming_msg == '1': # Nothing Important
        reply_text = (
            "Selection locked.\n"
            "Is there any question that I can solve?\n"
            "Need any help, type **/help**."
        )
        resp.message(reply_text)
        
    elif incoming_msg == '2': # Talk with Shivansh (Human Handoff)
        
        # Notify Shivansh via Gmail
        send_notification_to_shivansh(username, "Requested chat via 'Talk with Shivansh' option")
        
        # Reply to User
        resp.message(
            "I'm connecting you now. Shivansh has been notified via Gmail. "
            "Please wait for him to respond."
        )

    # --- 3. SPAM/DEFAULT RESPONSE ---
    else:
        # NOTE: Spam/Ad blocking logic would be complex and added here. 
        # For now, every non-command/non-option message gets the welcome screen.
        
        # if is_spam(incoming_msg):
        #    return "" 
        
        return handle_initial_message()
    
    return str(resp)

# Required for Render to find the application entry point
if __name__ == "__main__":
    app.run(debug=True)
    
