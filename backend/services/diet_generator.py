import anthropic, json, re
from core.config import settings
from models.profile import PCOSProfile


async def generate_diet_plan(profile: PCOSProfile) -> dict:
    """Generate a personalized daily diet plan using Claude."""
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    symptoms_str  = ", ".join(profile.symptoms or []) or "not specified"
    allergies_str = ", ".join(profile.allergies or []) or "none"
    goals_str     = ", ".join(profile.goals or []) or "general wellness"

    prompt = f"""Create a detailed personalized daily PCOS diet plan for a woman with these characteristics:
- Age: {profile.age or 'not specified'}
- Weight: {profile.weight_kg or 'not specified'} kg, BMI: {profile.bmi or 'not specified'}
- Dietary preference: {profile.dietary_preference}
- PCOS symptoms: {symptoms_str}
- Food allergies/intolerances: {allergies_str}
- Wellness goals: {goals_str}
- Activity level: {profile.activity_level}

Generate a JSON object (and nothing else) with this exact structure:
{{
  "total_cal": <integer>,
  "total_protein_g": <float>,
  "total_carbs_g": <float>,
  "total_fat_g": <float>,
  "notes": "<brief personalization note>",
  "meals": [
    {{
      "meal_type": "breakfast",
      "name": "<name>",
      "emoji": "<single emoji>",
      "description": "<1-2 sentences>",
      "calories": <int>,
      "protein_g": <float>,
      "carbs_g": <float>,
      "fat_g": <float>,
      "fiber_g": <float>,
      "gi_level": "low|medium|high",
      "tags": ["<tag1>", "<tag2>"],
      "sort_order": 0
    }},
    {{ meal_type: "lunch", sort_order: 1, ... }},
    {{ meal_type: "dinner", sort_order: 2, ... }},
    {{ meal_type: "snack", sort_order: 3, ... }}
  ]
}}

Rules:
- All meals must be PCOS-friendly (low glycemic, anti-inflammatory)
- Avoid foods matching allergies: {allergies_str}
- Respect dietary preference: {profile.dietary_preference}
- Include hormone-balancing ingredients where possible
- Return ONLY valid JSON, no markdown, no explanation"""

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)
