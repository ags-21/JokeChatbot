import requests
import json
import time

"""
Fetch exactly 100 random jokes from JokeAPI v2 with NSFW filtering.
Stores them in jokes_database.json for use in the chatbot.
"""


def fetch_jokes():
    """
    Fetch 100 unique jokes from JokeAPI with NSFW flag disabled.
    Makes multiple requests to ensure we get 100 distinct jokes.
    """
    base_url = "https://v2.jokeapi.dev/joke/Any"

    # Parameters to fetch jokes without NSFW content
    params = {
        "amount": 30,  # Request 30 per batch
        "blacklistFlags": "nsfw,religious,political,racist,sexist,explicit"  # Valid JokeAPI flags
    }

    jokes_set = {}  # Use dict with joke ID to avoid duplicates

    try:
        print("Fetching 100 unique jokes from JokeAPI...")

        # Fetch in batches until we have 100 unique jokes
        batch_count = 0
        while len(jokes_set) < 100 and batch_count < 20:  # Max 20 batches to get to 100
            batch_count += 1
            print(f"  Batch {batch_count}... ", end="", flush=True)

            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "error" in data and data["error"]:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                break

            batch_jokes = data.get("jokes", [])

            if len(batch_jokes) == 0:
                print("No more jokes available")
                break

            # Add jokes using their ID as key to avoid duplicates
            # Also filter out Dark category jokes
            for joke in batch_jokes:
                joke_id = joke.get("id")
                category = joke.get("category", "")
                # Skip if duplicate or if it's a Dark joke
                if joke_id and joke_id not in jokes_set and category != "Dark":
                    jokes_set[joke_id] = joke

            print(f"got {len(batch_jokes)}, total unique: {len(jokes_set)}")

            # Small delay to be respectful to the API
            time.sleep(0.5)

        jokes = list(jokes_set.values())[:100]  # Trim to exactly 100

        if len(jokes) == 0:
            print("No jokes retrieved. Check API status or parameters.")
            return None

        print(f"\n✓ Successfully fetched {len(jokes)} unique jokes")

        # Save to local JSON file
        with open("jokes_database.json", "w") as f:
            json.dump(jokes, f, indent=2)

        print(f"✓ Saved to jokes_database.json")
        print(f"\nSample joke:")
        sample = jokes[0]
        if sample.get("type") == "single":
            print(f"  {sample.get('joke')}")
        else:
            print(f"  Setup: {sample.get('setup')}")
            print(f"  Delivery: {sample.get('delivery')}")

        return jokes

    except requests.exceptions.RequestException as e:
        print(f"Error fetching jokes: {e}")
        return None


def analyze_jokes(jokes):
    """
    Quick analysis of fetched jokes.
    """
    if not jokes:
        return

    print("\n--- Jokes Database Analysis ---")
    print(f"Total jokes: {len(jokes)}")

    # Count by type
    types = {}
    categories = {}

    for joke in jokes:
        joke_type = joke.get("type", "unknown")
        category = joke.get("category", "unknown")

        types[joke_type] = types.get(joke_type, 0) + 1
        categories[category] = categories.get(category, 0) + 1

    print(f"\nJoke Types:")
    for jtype, count in sorted(types.items()):
        print(f"  {jtype}: {count}")

    print(f"\nCategories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    jokes = fetch_jokes()
    if jokes:
        analyze_jokes(jokes)
        print("\n✅ Data fetch complete! You can now build the Flask app.")
    else:
        print("\n❌ Failed to fetch jokes. Check your internet connection and try again.")