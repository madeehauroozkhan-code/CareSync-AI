"""
sms_service.py
-----------------
Wrapper around Twilio for sending WhatsApp/SMS messages -- used by the
Family Notification flow and the Follow-up Agent's check-in message.

`send_message()` simulates delivery (logs instead of sending) whenever
Twilio credentials aren't configured, so the demo runs end-to-end without
requiring a paid account.
"""

from backend.core.config import settings


def send_message(to_phone: str, body: str, channel: str = "whatsapp") -> dict:
    """
    Sends a message via Twilio. channel: "whatsapp" or "sms".
    Returns a dict describing what happened -- always safe to call, never
    raises, so a missing/invalid Twilio config never breaks the demo flow.
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        print(f"[SIMULATED {channel.upper()} to {to_phone}]: {body}")
        return {"status": "simulated", "channel": channel, "to": to_phone, "body": body}

    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        from_number = settings.twilio_whatsapp_from
        to_number = f"whatsapp:{to_phone}" if channel == "whatsapp" else to_phone

        message = client.messages.create(body=body, from_=from_number, to=to_number)
        return {"status": "sent", "sid": message.sid, "channel": channel, "to": to_phone}
    except Exception as e:
        print(f"[Twilio send failed, falling back to simulated log]: {e}")
        return {"status": "failed_simulated", "error": str(e), "channel": channel, "to": to_phone, "body": body}
