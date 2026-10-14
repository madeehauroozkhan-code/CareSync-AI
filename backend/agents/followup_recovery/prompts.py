"""
Follow-up & Recovery Agent — Prompt Templates
================================================
Check-in message templates for WhatsApp/SMS follow-ups.
"""

FOLLOWUP_MESSAGE_HINDI = """
🩺 AI Sahayak — Follow-up

Namaste {patient_name} ji,

Aapko kal {hospital_name} bheja gaya tha. Hum jaanna chahte hain:

1️⃣ Kya aap hospital pahunch gaye?
2️⃣ Kya aapka ilaaj hua?
3️⃣ Aap ab kaisa mehsoos kar rahe hain?

Kripya reply karein:
👍 "THEEK" — agar sab sahi hai
⚠️ "ABHI BHI TAKLEEF" — agar abhi bhi problem hai
🏥 "DOBARA DIKHANA HAI" — agar dobara doctor se milna hai
"""

FOLLOWUP_MESSAGE_ENGLISH = """
🩺 AI Sahayak — Follow-up

Hello {patient_name},

You were referred to {hospital_name} yesterday. We'd like to check:

1️⃣ Did you reach the hospital?
2️⃣ Did you receive treatment?
3️⃣ How are you feeling now?

Please reply:
👍 "BETTER" — if you're feeling better
⚠️ "SAME" — if no change
🏥 "NEED VISIT" — if you need to see a doctor again
"""

FOLLOWUP_RESPONSE_PROMPTS = {
    "better": "Bahut accha! Aaram karein aur agar koi nai takleef ho toh batayein. 🙏",
    "same": "Dhyan rakhein. Agar 24 ghante mein aur na sahi ho toh hospital zaroor jayein.",
    "worse": "⚠️ Kripya turant najdeeki hospital jayein. Hum aapke liye dobara hospital dhundh sakte hain.",
    "no_response": "Follow-up message sent. Awaiting patient response.",
}
