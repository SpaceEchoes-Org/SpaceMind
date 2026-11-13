
"""
NASA SpaceMind
NASA Real Image Search Service

Uses the official NASA Image and Video Library API.
No API key and no LLM required.
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

NASA_API_URL = "https://images-api.nasa.gov/search"
NASA_DETAILS_URL = "https://images.nasa.gov/details/"

class NASAImageSearchError(Exception):
    """Raised when NASA image search fails."""

def search_nasa_images(
    query: str,
    page: int = 1,
    page_size: int = 12
) -> dict:

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if page < 1:
        raise ValueError("Page must be at least 1.")

    if not 1 <= page_size <= 30:
        raise ValueError("Page size must be between 1 and 30.")

    params = {
        "q": query,
        "media_type": "image",
        "page": page,
        "page_size": page_size
    }

    url = f"{NASA_API_URL}?{urlencode(params)}"

    request = Request(
        url,
        headers={
            "User-Agent": "NASA-SpaceMind/1.0",
            "Accept": "application/json"
        }
    )

    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        raise NASAImageSearchError(
            f"NASA API returned HTTP {error.code}."
        ) from error

    except URLError as error:
        raise NASAImageSearchError(
            f"Could not connect to NASA: {error.reason}"
        ) from error

    except (TimeoutError, json.JSONDecodeError) as error:
        raise NASAImageSearchError(
            "NASA returned an invalid response or timed out."
        ) from error

    collection = payload.get("collection", {})

    items = collection.get("items", [])

    metadata = collection.get("metadata", {})

    images = []

    for item in items:

        data_list = item.get("data", [])

        if not data_list:
            continue

        data = data_list[0]

        nasa_id = data.get("nasa_id")

        if not nasa_id:
            continue

        preview_url = None

        for link in item.get("links", []):

            if (
                link.get("rel") == "preview"
                and link.get("render") == "image"
            ):
                preview_url = link.get("href")
                break

        images.append({

            "nasa_id": nasa_id,

            "title": data.get("title"),

            "description": data.get("description"),

            "date_created": data.get("date_created"),

            "center": data.get("center"),

            "photographer": data.get("photographer"),

            "preview_url": preview_url,

            "nasa_details_url": (
                NASA_DETAILS_URL + nasa_id
            ),

            "media_type": data.get("media_type")

        })

    return {

        "success": True,

        "query": query,

        "total_hits": metadata.get("total_hits", 0),

        "page": page,

        "page_size": page_size,

        "returned_images": len(images),

        "images": images

    }
