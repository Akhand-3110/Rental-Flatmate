import json
import logging
from google import genai
from google.genai import types
from app.config import settings
from app.models import Listing, TenantProfile

logger = logging.getLogger("uvicorn.error")

def calculate_rule_based_fallback(listing: Listing, profile: TenantProfile) -> dict:
    """
    Fallback safety rule engine executed if the primary LLM pipeline crashes[cite: 1].
    """
    score = 100
    reasons = []

    if listing.location.lower().strip() != profile.preferred_location.lower().strip():
        score -= 30
        reasons.append("The room location falls outside your exact profile preference location.")
    else:
        reasons.append("The room target location matches perfectly with your criteria.")

    if listing.rent > profile.budget_max:
        over_budget_percentage = (listing.rent - profile.budget_max) / profile.budget_max
        penalty = min(50, int(over_budget_percentage * 100))
        score -= penalty
        reasons.append(f"Rent price is above your maximum budget constraint by {int(over_budget_percentage * 100)}%.")
    elif listing.rent < profile.budget_min:
        score -= 10
        reasons.append("Rent is lower than your configured minimum target profile floor.")
    else:
        reasons.append("The billing model corresponds beautifully to your specified budget metrics.")

    return {
        "score": max(0, min(100, score)),
        "explanation": f"[Rule-Based Fallback] { ' '.join(reasons) }"
    }

def compute_compatibility(listing: Listing, profile: TenantProfile) -> dict:
    """
    Computes room/tenant pairing matrix score using modern Gemini flash model schemas[cite: 1].
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("Gemini token missing. Automatically processing baseline fallback rules.")
        return calculate_rule_based_fallback(listing, profile)
    prompt = (
        f"Given this room listing: Location: {listing.location}, Rent: {listing.rent}, Type: {listing.room_type}, Furnished: {listing.is_furnished} "
        f"and this tenant profile: Preferred Location: {profile.preferred_location}, Budget Range: {profile.budget_min}-{profile.budget_max}, "
        f"compute a compatibility score from 0 to 100 based on budget and location match. "
        f"Return JSON: {{ score: number, explanation: string }}"
    )

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        return {"score": int(data.get("score", 50)), "explanation": data.get("explanation", ""), "is_fallback": False}
    except Exception as e:
        logger.error(f"Gemini processing error occurred: {str(e)}. Safe failing back to local logic[cite: 1].")
        res = calculate_rule_based_fallback(listing, profile)
        res["is_fallback"] = True
        return res