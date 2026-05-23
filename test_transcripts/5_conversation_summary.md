# Test Transcript: 5. Conversation Summary

Demonstrates generating a structured JSON summary at the end of a session detailing intents, details, gaps, and recommendations.

**Customer**: Can I schedule an appointment?
**AI Agent**: First, could you please tell me your full name?

**Customer**: Jane Doe
**AI Agent**: Great! Which treatment are you looking to book? We offer Botox (from £200), Fillers (from £250), or a free Consultation.

**Customer**: Botox
**AI Agent**: Have you had this type of aesthetics treatment before? (Yes/No)

**Customer**: No, I haven't done it before
**AI Agent**: What is your preferred day and time for the appointment? (We are open Mon–Sat, 9 am–7 pm)

**Customer**: Saturday morning at 10am
**AI Agent**: Thank you for providing those details, Jane Doe! I have recorded your booking request for Botox on Saturday morning at 10am. A clinic member will contact you shortly to confirm the appointment. Have a wonderful day!

## Session End - Structured Summary (Stage 4)
```json
{
  "intent": "Inquiry and booking request for aesthetics treatment",
  "details_collected": {
    "name": "Jane Doe",
    "treatment_interest": "Botox",
    "prior_treatment": "No",
    "preferred_schedule": "Saturday morning at 10am"
  },
  "sop_gaps": [
    "Customer asked about dental/teeth whitening treatments which are not offered"
  ],
  "recommended_action": "Schedule Jane Doe for a free Botox consultation on Saturday morning and send confirmation details."
}
```