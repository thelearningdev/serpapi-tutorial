import os
import serpapi
from dotenv import load_dotenv

load_dotenv()

try:
    client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
except KeyError:
    raise ValueError("SERPAPI_KEY is not set in the environment variables")


def get_local_restaurants(city: str, cuisine: str) -> list[dict]:
    results = client.search(
        engine="google_maps",
        q=f"{cuisine} restaurants in {city}",
        type="search",
    )
    return results.get("local_results", [])
