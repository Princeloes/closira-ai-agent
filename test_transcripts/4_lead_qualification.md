# Test Transcript: 4. Lead Qualification

Demonstrates structured lead qualification questions to gather and store customer data.

**Customer**: Can I book a Botox session?
**AI Agent**: First, could you please tell me your full name?

**Customer**: Jane Doe
**AI Agent**: Great! Which treatment are you looking to book? We offer Botox (from £200), Fillers (from £250), or a free Consultation.

**Customer**: Botox
**AI Agent**: Have you had this type of aesthetics treatment before? (Yes/No)

**Customer**: No, this is my first time
**AI Agent**: What is your preferred day and time for the appointment? (We are open Mon–Sat, 9 am–7 pm)

**Customer**: Saturday morning at 10am
**AI Agent**: Thank you for providing those details, Jane Doe! I have recorded your booking request for Botox on Saturday morning at 10am. A clinic member will contact you shortly to confirm the appointment. Have a wonderful day!

## Internal State Metadata
- **Stage**: completed
- **Escalated**: False
- **Lead Details Collected**:
{
  "name": "Jane Doe",
  "treatment_interest": "Botox",
  "prior_treatment": "No",
  "preferred_schedule": "Saturday morning at 10am"
}