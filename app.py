import os
import logging
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.rest import Client
from dotenv import load_dotenv
from database import init_db, save_message, save_call, get_last_sender_by_last_four
from models import MessageRecord, CallRecord

load_dotenv()

init_db()

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']
RELAY_TO_NUMBER = os.environ['RELAY_TO_NUMBER']

LOG_FILE = os.getenv('LOG_FILE', 'relay.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/", methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return "Relay App is running!", 200

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming messages."""
    from_number = request.form.get('From')
    to_number = request.form.get('To')
    body = request.form.get('Body', '')
    if not from_number or not to_number:
        return Response("Invalid request. Requires both from number and to number", status=400)


    logging.info(f"Incoming SMS from {from_number} to {to_number}: {body}")

    try:
        msg_record = MessageRecord(from_number=from_number, to_number=to_number, body=body)
        save_message(msg_record)
    except Exception as e:
        logging.error(f"Failed to save message to database: {e}")

    resp = MessagingResponse()

    if from_number == RELAY_TO_NUMBER:
        try:
            parts = body.split(' ', 1)
            if len(parts) < 2:
                logging.warning(f"Invalid reply format from {from_number}: {body}")
                return str(resp)

            last_four = parts[0]
            message_to_send = parts[1]

            target_number = get_last_sender_by_last_four(last_four, TWILIO_NUMBER)
            
            if target_number:
                if not client:
                    logging.error("Twilio Client not initialized. Check credentials.")
                    return str(resp)

                client.messages.create(
                    to=target_number,
                    from_=TWILIO_NUMBER,
                    body=message_to_send
                )
                logging.info(f"Forwarded reply to {target_number}: {message_to_send}")
            else:
                logging.warning(f"Could not find original sender in database for last 4 digits: {last_four}")
                
        except Exception as e:
            logging.error(f"Error processing reply from {from_number}: {e}")
    else:
        forward_body = f"[{from_number}] - {body}"
        resp.message(forward_body, to=RELAY_TO_NUMBER)
        logging.info(f"Forwarded SMS from {from_number} to {RELAY_TO_NUMBER}")

    return str(resp)

@app.route("/voice", methods=['POST'])
def voice_reply():
    """Respond to incoming calls."""
    from_number = request.form.get('From')
    to_number = request.form.get('To')
    logging.info(f"Incoming Call from {from_number} to {to_number}")
    if not from_number or not to_number:
        return Response("Invalid request. Requires both from number and to number", status=400)

    try:
        call_record = CallRecord(from_number=from_number, to_number=to_number)
        save_call(call_record)
    except Exception as e:
        logging.error(f"Failed to save call to database: {e}")

    resp = VoiceResponse()
    
    if from_number == RELAY_TO_NUMBER:
        resp.say("Relay system active.")
    else:
        dial = Dial(caller_id=TWILIO_NUMBER)
        dial.number(RELAY_TO_NUMBER)
        resp.append(dial)
        logging.info(f"Forwarding call from {from_number} to {RELAY_TO_NUMBER}")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
