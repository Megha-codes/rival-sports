"""WhatsApp webhook server for Rival Sports / Performance Plus Physio.

Works with Meta's WhatsApp Cloud API directly, or through 360dialog (needed for
"coexistence", where the same number also stays active in the WhatsApp Business App).
"""

import logging
import os
import sys
from collections import deque

import requests
from dotenv import load_dotenv
from flask import Flask, abort, request

load_dotenv()

import business_info as info  # noqa: E402
from bot import handle_message, pause_bot  # noqa: E402

PROVIDER = os.getenv("WHATSAPP_PROVIDER", "meta").strip().lower()  # "meta" or "360dialog"
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
# How long the bot stays quiet with a customer after you reply to them yourself from the Business App.
PAUSE_HOURS = float(os.getenv("BOT_PAUSE_HOURS", "4"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("whatsapp-bot")

D360_BASE = os.getenv("D360_BASE_URL", "https://waba-v2.360dialog.io").rstrip("/")
if PROVIDER == "360dialog":
    _key = os.getenv("D360_API_KEY", "").strip()
    SEND_URL = f"{D360_BASE}/messages"
    HEADERS = {"D360-API-KEY": _key}
else:
    _key = os.getenv("WHATSAPP_TOKEN", "").strip()
    PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    SEND_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    HEADERS = {"Authorization": f"Bearer {_key}"}
    _key = _key if PHONE_NUMBER_ID else ""
# The server still starts without keys (so it can be deployed before WhatsApp is set up); it just can't reply yet.
CONFIGURED = bool(_key)
if not CONFIGURED:
    log.warning("WhatsApp keys are not set yet (provider: %s). The server is running, but it can't send replies.", PROVIDER)
app = Flask(__name__)

# WhatsApp retries webhooks, so remember recent message ids to avoid answering twice.
_seen_ids: deque[str] = deque(maxlen=2000)


def send_text(to: str, body: str) -> None:
    if not CONFIGURED:
        log.warning("Not sending to %s: WhatsApp keys are not set.", to)
        return
    resp = requests.post(
        SEND_URL,
        headers=HEADERS,
        json={"messaging_product": "whatsapp", "recipient_type": "individual", "to": to,
              "type": "text", "text": {"body": body, "preview_url": True}},
        timeout=15,
    )
    if resp.status_code >= 400:
        log.error("Send to %s failed: %s %s", to, resp.status_code, resp.text)


def _is_new(msg_id: str | None) -> bool:
    if not msg_id or msg_id in _seen_ids:
        return False
    _seen_ids.append(msg_id)
    return True


def _handle_incoming(msg: dict) -> None:
    sender = msg.get("from")
    if not sender:
        log.warning("Incoming message without a phone number, skipped: %s", msg.get("id"))
        return
    kind = msg.get("type", "")
    if kind == "text":
        text = msg["text"].get("body", "")
    elif kind == "interactive":
        inter = msg["interactive"]
        text = (inter.get("button_reply") or inter.get("list_reply") or {}).get("title", "")
    elif kind in {"reaction", "unsupported", "system"}:
        return  # don't answer emoji reactions and system notices
    else:
        text = msg.get(kind, {}).get("caption", "") if isinstance(msg.get(kind), dict) else ""

    log.info("From %s (%s): %r", sender, kind, text)
    for reply in handle_message(sender, text, kind):
        send_text(sender, reply)


def _handle_echo(echo: dict) -> None:
    """You replied to a customer from the WhatsApp Business App, so the bot steps back."""
    customer = echo.get("to")
    if customer:
        pause_bot(customer, PAUSE_HOURS)
        log.info("You replied to %s from the app. Bot paused for them for %s h.", customer, PAUSE_HOURS)


@app.get("/webhook")
def verify():
    # Meta's one-time webhook check. (360dialog doesn't use this.)
    if (VERIFY_TOKEN and request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge", ""), 200
    abort(403)


@app.post("/webhook")
def receive():
    payload = request.get_json(silent=True) or {}
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            # Messages you sent by hand from the Business App (coexistence only).
            for echo in value.get("message_echoes", []):
                if _is_new(echo.get("id")):
                    _handle_echo(echo)

            for msg in value.get("messages", []):
                if _is_new(msg.get("id")):
                    _handle_incoming(msg)
    return "ok", 200


@app.get("/")
def health():
    status = "connected to WhatsApp" if CONFIGURED else "waiting for WhatsApp keys"
    return f"Rival Sports WhatsApp bot is running ({PROVIDER}, {status}).", 200


@app.get("/privacy")
def privacy():
    """Privacy policy page. Meta asks for this URL when you set up the WhatsApp app."""
    contact = info.PHONE + (f" or {info.EMAIL}" if info.EMAIL else "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Policy | {info.BUSINESS_NAME}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:40px auto;padding:0 16px;line-height:1.6;color:#222}}</style>
</head><body>
<h1>Privacy Policy</h1>
<p><strong>{info.BUSINESS_NAME} / {info.CLINIC_NAME}</strong>, Kolkata, India</p>
<h2>What we collect</h2>
<p>When you message us on WhatsApp, we receive your WhatsApp phone number, your profile name and the messages you send.
If you register for an appointment, our registration form (Google Forms) collects your name, contact number, address, age, gender, health concern and preferred appointment time, and you may send us a payment screenshot on WhatsApp.</p>
<h2>How we use it</h2>
<p>We use this information only to answer your questions, arrange and confirm appointments, and contact you about your treatment.
We do not sell your information or use it for advertising.</p>
<h2>Who we share it with</h2>
<p>Messages are delivered through WhatsApp (Meta Platforms) and our WhatsApp service provider, and registration forms are stored with Google. They process this information on our behalf.
We do not share your information with anyone else unless the law requires it.</p>
<h2>How long we keep it</h2>
<p>We keep appointment requests for as long as needed to provide care and keep our records, then delete them.</p>
<h2>Your choices</h2>
<p>You can ask us to see, correct or delete your information at any time. Contact us at {contact}.</p>
</body></html>""", 200


def set_360dialog_webhook(url: str) -> None:
    """Tell 360dialog where to send messages: python main.py set-webhook https://bot.example.com/webhook"""
    resp = requests.post(f"{D360_BASE}/v1/configs/webhook", headers=HEADERS, json={"url": url}, timeout=15)
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "set-webhook":
        if PROVIDER != "360dialog":
            sys.exit("set-webhook is only for 360dialog. For Meta, set the webhook in the Meta developer dashboard.")
        set_360dialog_webhook(sys.argv[2])
    else:
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
