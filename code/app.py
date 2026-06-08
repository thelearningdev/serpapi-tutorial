import requests
import streamlit as st
import pandas as pd
from serpapi_client import get_local_restaurants
from scorer import compute_score, _trend_multiplier as _compute_trend_multiplier


def build_dataframe(raw_results: list[dict]) -> pd.DataFrame:
    rows = []
    for r in raw_results:
        rating = r.get("rating")
        reviews = r.get("reviews")

        # Skip results missing the data we need to score
        if rating is None or reviews is None:
            continue

        trend = _compute_trend_multiplier(r)
        sc = compute_score(r)

        rows.append(
            {
                "Name": r.get("title", "Unknown"),
                "Rating": rating,
                "Reviews": reviews,
                "Trend Boost": round(trend, 2),
                "Score": round(sc, 2),
                "Address": r.get("address", ""),
                "Price": r.get("price", "N/A"),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    return df.sort_values("Score", ascending=False).reset_index(drop=True)


# ── Streamlit UI ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Pre-Viral Restaurant Finder",
    page_icon="🍽",
    layout="centered",
)

st.title("Pre-Viral Restaurant Finder")
st.caption(
    "Surfaces hidden gems: high rating, low review count, strong trend signal."
)

with st.form("search_form"):
    col1, col2 = st.columns(2)
    city = col1.text_input("City", placeholder="e.g. Chennai", value="Chennai")
    cuisine = col2.text_input("Cuisine", placeholder="e.g. Coffee, Biriyani, Dosa", value="Coffee")
    submitted = st.form_submit_button("Find Hidden Gems")

if submitted:
    if not city or not cuisine:
        st.warning("Please enter both a city and a cuisine type.")
        st.stop()

    with st.spinner(f"Querying SerpAPI for {cuisine} in {city}..."):
        try:
            raw = get_local_restaurants(city, cuisine)
        except ValueError as e:
            st.error(str(e))
            st.stop()
        except requests.HTTPError as e:
            st.error(f"SerpAPI request failed: {e}")
            st.stop()

    if not raw:
        st.info("No results returned. Try a different city or cuisine.")
        st.stop()

    df = build_dataframe(raw)

    if df.empty:
        st.info("Results came back but lacked rating/review data to score.")
        st.stop()

    st.subheader(f"Top picks for {cuisine} in {city}")
    st.caption(
        "Sorted by score. Higher = better hidden gem candidate."
    )

    # Color-code the score column so the gem tier pops visually
    def highlight_score(val):
        if val >= 40:
            return "background-color: #d4edda; color: #155724"
        elif val >= 35:
            return "background-color: #fff3cd; color: #856404"
        else:
            return ""

    styled = df.style.map(highlight_score, subset=["Score"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    with st.expander("How is this scored?"):
        st.markdown(
            """
**Formula:**
```
score = (avg_rating × 10) - log(review_count + 1) + trend_multiplier
```

- `avg_rating × 10` — rewards quality
- `- log(review_count + 1)` — penalizes already-popular spots
- `trend_multiplier` — boosts newly opened, high photo activity, or labeled-popular places

A score above 40 is a strong pre-viral signal.
"""
        )

    with st.expander(f"Raw API results ({len(raw)} returned)"):
        st.json(raw)
