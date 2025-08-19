# fetch_nutrition.py
# Requires: requests, pyyaml
# Install: pip install requests pyyaml

import os
import requests
import yaml
from pathlib import Path

# Config
ING_DIR = Path("Ingredients")
API_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
APP_ID = os.getenv("NUTRITIONIX_APP_ID")
APP_KEY = os.getenv("NUTRITIONIX_APP_KEY")
SERVING_TEXT = "1/4 cup"   # adjust if you prefer grams or different serving

if not APP_ID or not APP_KEY:
    raise SystemExit("Set NUTRITIONIX_APP_ID and NUTRITIONIX_APP_KEY environment variables.")

headers = {
    "x-app-id": APP_ID,
    "x-app-key": APP_KEY,
    "Content-Type": "application/json"
}

def uc_first_filename(name: str) -> str:
    # Simple UC-first per word; tweak if you want different rules.
    return " ".join(w.capitalize() for w in name.replace('-', ' ').split())

def safe_round(value, ndigits=0):
    """Round numeric values safely. If value is None or non-numeric, return 0.

    - ndigits=0 returns an int
    - ndigits>0 returns a float with that many decimals
    """
    if value is None:
        return 0 if ndigits == 0 else 0.0
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0 if ndigits == 0 else 0.0
    if ndigits == 0:
        return int(round(f))
    return round(f, ndigits)

for md in ING_DIR.glob("*.md"):
    text = md.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        print(f"Skipping (has frontmatter): {md.name}")
        continue

    ingredient = md.stem
    query = f"{SERVING_TEXT} {ingredient}"
    payload = {"query": query}

    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        if not data.get("foods"):
            print(f"No foods returned for {ingredient}; skipping.")
            continue
        food = data["foods"][0]
    except Exception as e:
        print(f"API error for {ingredient}: {e}")
        continue

    # Map Nutritionix fields -> your frontmatter keys
    nm = {
        "source": "Nutritionix API",
        "serving_size": SERVING_TEXT,
    "calories_kcal": safe_round(food.get("nf_calories", 0)),
    "carbohydrates_g": safe_round(food.get("nf_total_carbohydrate", 0), 1),
    "sugar_g": safe_round(food.get("nf_sugars", 0), 1),
    "fiber_g": safe_round(food.get("nf_dietary_fiber", 0), 1),
    "protein_g": safe_round(food.get("nf_protein", 0), 1),
    "fat_g": safe_round(food.get("nf_total_fat", 0), 1),
    "saturated_fat_g": safe_round(food.get("nf_saturated_fat", 0), 1),
    "cholesterol_mg": safe_round(food.get("nf_cholesterol", 0)),
    "sodium_mg": safe_round(food.get("nf_sodium", 0))
    }

    front = "---\n" + yaml.safe_dump(nm, sort_keys=False).strip() + "\n---\n\n"
    md.write_text(front + text, encoding="utf-8")
    new_name = uc_first_filename(ingredient) + md.suffix
    new_path = md.with_name(new_name)
    if new_path != md:
        md.rename(new_path)
        print(f"Updated & renamed: {md.name} -> {new_path.name}")
    else:
        print(f"Updated: {md.name}")