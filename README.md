# Pre-Viral Restaurant Finder

A Streamlit app that queries SerpAPI's Google Maps Local Results and scores restaurants by their "hidden gem" potential.

## Setup

```bash
cp .env.example .env
# Add your SerpAPI key to .env

uv sync
uv run streamlit run app.py
```

## Scoring Formula

```
score = (avg_rating × 10) - log(review_count + 1) + trend_multiplier
```

High rating + few reviews + trend signal = pre-viral candidate.
