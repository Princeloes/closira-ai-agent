import os
import json
from typing import Dict, Any

class SOPManager:
    def __init__(self, sop_path: str = "sop.json"):
        self.sop_path = sop_path
        self.sop_data = self.load_sop()

    def load_sop(self) -> Dict[str, Any]:
        """Loads and parses the SOP JSON file."""
        if not os.path.exists(self.sop_path):
            # Try parent directory relative path if needed
            alt_path = os.path.join(os.path.dirname(__file__), "..", self.sop_path)
            if os.path.exists(alt_path):
                self.sop_path = alt_path
            else:
                raise FileNotFoundError(f"SOP file not found at {self.sop_path}")
        
        with open(self.sop_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_formatted_sop(self) -> str:
        """Returns a clean plain text representation of the SOP for prompting."""
        data = self.sop_data
        hours = data.get("hours", {})
        services_list = data.get("services", [])
        
        services_str = ""
        for s in services_list:
            services_str += f"- {s['name']}: {s['price']} ({s.get('description', '')})\n"
            
        booking_str = ", ".join(data.get("booking_channels", []))
        cancellation = data.get("cancellation_policy", "")
        escalation_reasons = "\n".join([f"- {reason}" for reason in data.get("escalation_policy", {}).get("reasons", [])])
        
        sop_text = f"""--- STANDARD OPERATING PROCEDURES (SOP) ---
Business: {data.get('business_name')}
Hours: {hours.get('days')}, {hours.get('time')}

Services & Pricing:
{services_str}
Booking Info: Bookings can be made via: {booking_str}.
Cancellation Policy: {cancellation}

Escalate to human immediately if the customer's request/message meets any of these criteria:
{escalation_reasons}
------------------------------------------"""
        return sop_text
