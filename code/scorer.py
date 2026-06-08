import math


def _trend_multiplier(place: dict) -> float:
    """
    Approximate trend signal from available SerpAPI fields.
    Higher score = stronger upward momentum.
    """
    score = 0.0
    review_count = place.get("reviews", 0) or 0

    # Sweet spot: 10-100 reviews suggests early traction, not obscurity
    if 10 <= review_count <= 100:
        score += 5.0
    elif review_count < 10:
        score += 2.0  # too new — lower confidence

    # Businesses that bother responding are actively growing
    if place.get("owner_answer"):
        score += 3.0

    # Recently claimed/active listing
    if place.get("hours") and "Opens" in str(place.get("hours", "")):
        score += 1.0

    # Penalize if price level is missing (often means incomplete listing)
    if not place.get("price"):
        score -= 1.0

    return score


def compute_score(place: dict) -> float:
    rating = place.get("rating", 0) or 0
    review_count = place.get("reviews", 0) or 0
    trend = _trend_multiplier(place)

    # High rating amplified, penalized by log of review count (popularity dampener)
    return round((rating * 10) - math.log(review_count + 1) + trend, 2)


def enrich_results(places: list[dict]) -> list[dict]:
    enriched = []
    for place in places:
        enriched.append({
            "name": place.get("title", ""),
            "rating": place.get("rating", "N/A"),
            "reviews": place.get("reviews", 0),
            "score": compute_score(place),
            "address": place.get("address", ""),
            "maps_link": place.get("link", ""),
            "price": place.get("price", ""),
            "type": place.get("type", ""),
        })
    return sorted(enriched, key=lambda x: x["score"], reverse=True)
