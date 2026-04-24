# Twilio Relay Application

This application acts as a phone relay using Twilio. It forwards incoming SMS and Voice calls to a specified number.

## Features
- **SMS Forwarding**: Incoming texts are forwarded to the `RELAY_TO_NUMBER`. The forwarded message includes the original sender's number.
- **SMS Replying**: To reply, send a message from the `RELAY_TO_NUMBER` to the Twilio number, starting with the last 4 digits of the target phone number.
  - Example: `1234 Hello there!` will send `Hello there!` to the most recent sender whose number ends in `1234`.
- **Voice Forwarding**: Incoming calls are automatically dialed to the `RELAY_TO_NUMBER`.
- **Logging & Storage**: All incoming events are logged to `relay.log` and stored in a SQLite database (`relay.db`) using SQLAlchemy and Pydantic for validation.

## Environment Variables
Create a `.env` file with the following (these will be picked up by `docker-compose.yml`):
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
- `TWILIO_NUMBER`: Your Twilio phone number (e.g., `+12223334444`).
- `RELAY_TO_NUMBER`: The phone number where you want to receive forwarded calls and texts.

## Setup
1. Install [uv](https://docs.astral.sh/uv/) if you haven't already.
2. Install dependencies: `uv sync`
3. Configure your Twilio number webhooks:
   - Messaging: `https://your-domain.com/sms`
   - Voice: `https://your-domain.com/voice`
3. Run locally: `python app.py` or use Docker: `docker-compose up -d`
