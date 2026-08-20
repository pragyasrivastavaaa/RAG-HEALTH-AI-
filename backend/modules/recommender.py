"""Phase 3 — Condition-based recommender (diet + lifestyle)."""
import json, os

DIET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "diet_rules.json")

def recommend(conditions: list) -> dict:
    try:
        with open(DIET_PATH) as f:
            rules = json.load(f)
    except FileNotFoundError:
        return {"conditions_addressed": [], "diet": [], "lifestyle": []}

    diet, lifestyle, addressed = [], [], []
    seen_diet, seen_life = set(), set()

    for key in conditions:
        rule = rules.get(key)
        if not rule:
            continue
        addressed.append({"key": key, "display_name": rule["display_name"]})
        for tip in rule.get("diet", []):
            if tip not in seen_diet:
                diet.append({"condition": key, "tip": tip})
                seen_diet.add(tip)
        for tip in rule.get("lifestyle", []):
            if tip not in seen_life:
                lifestyle.append({"condition": key, "tip": tip})
                seen_life.add(tip)

    return {"conditions_addressed": addressed, "diet": diet, "lifestyle": lifestyle}