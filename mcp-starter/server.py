"""
Demo MCP server — your Week 1 "hello world".

It exposes all three MCP primitives so you can watch each one work:
  • tools     — actions the AI can call        (add, get_weather)
  • resources — data the AI can read on demand  (about)
  • prompts   — reusable templates              (outdoor_check)

Run it:
  fastmcp dev server.py                       # opens the MCP Inspector in your browser
  fastmcp install claude-desktop server.py    # wires it into Claude Desktop
"""

import httpx
from fastmcp import FastMCP

# The name shows up in the AI client's tool list.
mcp = FastMCP("Demo Server 🚀")


@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


@mcp.tool
async def get_weather(city: str) -> str:
    """Get the current weather for a city by name.

    This is the skill that pays: wrapping an external API so the AI can call it.
    Uses Open-Meteo — free, no API key, reliable.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        # 1) Turn the city name into coordinates.
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
        )
        results = geo.json().get("results")
        if not results:
            return f"Couldn't find a place called {city!r}."
        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        label = f"{place['name']}, {place.get('country', '')}".strip(", ")

        # 2) Fetch current conditions for those coordinates.
        forecast = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m",
            },
        )
        current = forecast.json()["current"]

    return (
        f"{label}: {current['temperature_2m']}°C, "
        f"wind {current['wind_speed_10m']} km/h."
    )


@mcp.resource("demo://about")
def about() -> str:
    """A static piece of data the AI can read on demand."""
    return "Demo MCP server built with FastMCP — your first one. Edit me!"


@mcp.prompt
def outdoor_check(city: str) -> str:
    """A reusable prompt that tells the AI how to chain your tools."""
    return (
        f"Use the get_weather tool for {city}, then tell me in one sentence "
        f"whether it's a good time to go outside."
    )


if __name__ == "__main__":
    # No transport argument = stdio, which is what Claude Desktop expects.
    mcp.run()
