"""Conversation logic. Pure Python with no WhatsApp/network code, so it can be tested from the terminal."""

import re
import sys
import threading
import time

import business_info as info

# phone number -> time until which the bot stays quiet (because a human is chatting with them)
_paused_until: dict[str, float] = {}
_lock = threading.Lock()

RESUME_WORDS = {"menu", "bot"}

GREETINGS = {"hi", "hello", "hey", "hii", "hiii", "start", "namaste", "namaskar", "good morning",
             "good afternoon", "good evening", "helo", "hlo"}

# Message types that are probably a payment screenshot (or a receipt sent as a file).
SCREENSHOT_TYPES = {"image", "document"}

# keyword -> menu option. Checked when the message isn't a plain number.
KEYWORDS = [
    ("7", ["emergency", "urgent", "accident", "severe pain", "help me"]),
    ("6", ["book", "appointment", "slot", "visit", "consult", "register", "registration", "form", "payment", "pay", "upi"]),
    ("1", ["service", "treatment", "physio", "acl", "knee", "shoulder", "arthritis", "rehab", "injury", "pain", "tkr", "thr",
           "pcl", "meniscus", "ligament", "needling", "dry needling", "sports"]),
    ("2", ["address", "location", "where", "map", "direction", "rajarhat", "vivekananda", "branch", "centre", "center"]),
    ("3", ["time", "timing", "open", "close", "hours", "when"]),
    ("4", ["charge", "fee", "price", "cost", "rate", "how much"]),
    ("5", ["area", "home visit", "surrounding", "cover"]),
    ("7", ["contact", "call", "phone", "number", "email", "mail"]),
]

MENU_REPLIES = {
    "1": info.SERVICES_TEXT,
    "2": info.LOCATIONS_TEXT,
    "3": info.TIMINGS_TEXT,
    "4": info.CHARGES_TEXT,
    "5": info.SERVICE_AREA_TEXT,
    "6": info.BOOKING_TEXT,
    "7": info.CONTACT_TEXT,
}


def pause_bot(phone: str, hours: float) -> None:
    """Stop auto-replying to this customer for a while, e.g. because staff replied from the app."""
    with _lock:
        _paused_until[phone] = time.time() + hours * 3600


def _is_paused(phone: str) -> bool:
    until = _paused_until.get(phone)
    if until is None:
        return False
    if time.time() >= until:
        _paused_until.pop(phone, None)
        return False
    return True


def _detect_option(text: str) -> str | None:
    m = re.fullmatch(r"\s*([1-7])\s*[.)]?\s*", text)
    if m:
        return m.group(1)
    for option, words in KEYWORDS:
        if any(re.search(rf"\b{re.escape(w)}", text) for w in words):
            return option
    return None


def handle_message(phone: str, text: str, kind: str = "text") -> list[str]:
    """Return the replies to send. `kind` is the WhatsApp message type (text, image, document, audio...)."""
    raw = (text or "").strip()
    low = raw.lower()

    with _lock:
        if _is_paused(phone):
            if low not in RESUME_WORDS:
                return []  # staff is handling this chat; stay silent
            _paused_until.pop(phone, None)  # customer asked for the menu, so the bot takes over again

        if kind in SCREENSHOT_TYPES:
            return [info.PAYMENT_RECEIVED_TEXT]

        if not raw or low in GREETINGS or low in {"menu", "help", "options", "0"}:
            return [info.WELCOME, info.MENU_TEXT]

        option = _detect_option(low)
        if option == "7" and any(w in low for w in ("emergency", "urgent", "accident", "severe pain", "help me")):
            return [info.EMERGENCY_TEXT]
        if option:
            return [MENU_REPLIES[option], "Type *menu* to see more options."]
        if low in {"thanks", "thank you", "ok", "okay", "thx", "ty"}:
            return ["You're welcome! 🙏 Wishing you a speedy recovery. Type *menu* if you need anything else."]
        return [info.FALLBACK_TEXT]


if __name__ == "__main__":
    # Ensure terminal output supports the bot's emoji and non-ASCII text on Windows.
    for stream_name in ("stdout", "stderr", "stdin"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            encoding = getattr(stream, "encoding", None)
            if encoding and encoding.lower() != "utf-8":
                stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    # Chat with the bot in the terminal without WhatsApp. Type "/image" to pretend you sent a screenshot.
    print("Local test mode. Type 'quit' to exit, '/image' to simulate sending a payment screenshot.\n")
    while True:
        try:
            msg = input("You: ")
        except (EOFError, KeyboardInterrupt):
            break
        if msg.strip().lower() == "quit":
            break
        if msg.strip().lower() == "/image":
            replies = handle_message("local-test", "", kind="image")
        else:
            replies = handle_message("local-test", msg)
        for r in replies:
            print(f"\nBot: {r}\n")
