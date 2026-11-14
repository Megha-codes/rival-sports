"""All business details and reply texts live here, so they can be edited without touching the bot logic."""

from urllib.parse import quote_plus

BUSINESS_NAME = "Rival Sports"
CLINIC_NAME = "Performance Plus Physio"
DOCTOR = "Dr. Dibyajit Mitra"
PHONE = "+91 9804218167"
PHONE_LINK = "tel:+919804218167"
EMAIL = ""  # not provided yet. Fill in and it will show up in the contact reply.

LOCATIONS = [
    {
        "name": "Rajarhat Centre",
        "address": "1st Floor, Purti Star, Rajarhat Main Road, Kolkata, West Bengal 700135",
    },
    {
        "name": "Vivekananda Sarani Centre",
        "address": "87, Vivekananda Sarani, Prince Anwar Shah Connector, Next to RX VITAL, Kolkata 700078",
    },
]

TIMINGS = "6:30 AM to 11:00 PM"
APPROX_CHARGES = "₹1,000"
SERVICE_AREA = "Kolkata and its surrounding areas"

SERVICES = [
    "Sports & Gym Injury Rehabilitation",
    "Post-Operative Rehabilitation (e.g. TKR, THR)",
    "Bone & Joint Care",
    "Chronic Pain Management (e.g. Arthritis, Frozen Shoulder)",
    "ACL Rehabilitation",
]


def maps_link(address: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(address)


# ---------------------------------------------------------------- reply texts

WELCOME = (
    f"🙏 *Greetings from {CLINIC_NAME}*, led by *{DOCTOR}* at *{BUSINESS_NAME}*.\n\n"
    "We are committed to helping you move better, feel stronger, and live pain-free.\n\n"
    f"🚨 In case of an emergency, call us at *{PHONE}*."
)

MENU_TEXT = (
    "How can we help you? Reply with a number:\n\n"
    "1️⃣ Our services\n"
    "2️⃣ Clinic locations\n"
    "3️⃣ Timings\n"
    "4️⃣ Charges\n"
    "5️⃣ Service area\n"
    "6️⃣ Book an appointment\n"
    "7️⃣ Contact us / Emergency\n\n"
    "Type *menu* any time to see this again."
)

SERVICES_TEXT = (
    "💪 *Our Services*\n\n"
    + "\n".join(f"• {s}" for s in SERVICES)
    + "\n\nReach out to us for personalized care and recovery support. Reply *6* to book an appointment."
)

LOCATIONS_TEXT = "📍 *Our Centres*\n\n" + "\n\n".join(
    f"*{i}. {loc['name']}*\n{loc['address']}\n🗺️ {maps_link(loc['address'])}"
    for i, loc in enumerate(LOCATIONS, start=1)
)

TIMINGS_TEXT = f"🕕 *Timings*\n\nWe are open every day from *{TIMINGS}*."

CHARGES_TEXT = (
    f"💰 *Charges*\n\nApproximate charges: *{APPROX_CHARGES}*.\n"
    "The exact fee depends on your condition and treatment plan. "
    f"Call us at {PHONE} for details."
)

SERVICE_AREA_TEXT = f"🚗 *Service Area*\n\nWe serve *{SERVICE_AREA}*."

CONTACT_TEXT = (
    "📞 *Contact Us*\n\n"
    f"Phone / WhatsApp: *{PHONE}*\n"
    + (f"Email: {EMAIL}\n" if EMAIL else "")
    + f"Timings: {TIMINGS}\n\n"
    f"🚨 *Emergency support:* call *{PHONE}* right away."
)

EMERGENCY_TEXT = (
    "🚨 *For an emergency, please call us right now at "
    f"{PHONE}.*\n\n"
    "If you have a serious injury, heavy bleeding, chest pain, or cannot move a limb, "
    "please also go to the nearest hospital emergency department."
)

FALLBACK_TEXT = "Sorry, I didn't quite get that. 🙂\n\n" + MENU_TEXT

# Registration & booking happens through this Google Form (it also shows the UPI QR code for the fee).
REGISTRATION_FORM_URL = "https://forms.gle/1ZQy8KrBSV5LBSKR9"

BOOKING_TEXT = (
    "📝 *Book an appointment*\n\n"
    "Please register using our form (takes about 2 minutes):\n"
    f"👉 {REGISTRATION_FORM_URL}\n\n"
    "*How it works:*\n"
    "1️⃣ Fill in your details, health concern and preferred date & time.\n"
    "2️⃣ Pay the registration fee using the UPI QR code at the end of the form.\n"
    "3️⃣ Send the *payment screenshot* here in this chat.\n\n"
    "⚠️ Your appointment is confirmed only after we receive the payment screenshot.\n\n"
    f"Need help? Call us at {PHONE}."
)

PAYMENT_RECEIVED_TEXT = (
    "✅ *Thank you! We've received your file.*\n\n"
    "If this is your payment screenshot, our team will check it and confirm your appointment shortly.\n\n"
    f"Haven't filled the registration form yet? 👉 {REGISTRATION_FORM_URL}"
)
