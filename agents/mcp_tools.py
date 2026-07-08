from __future__ import annotations

import sqlite3
from typing import Any, Callable

import requests
from geopy.geocoders import Nominatim
from langchain_core.tools import StructuredTool

from src.retrieval import hybrid_retriever

DB_PATH = "crop_insurance.db"

try:
    from fastmcp import FastMCP

    mcp = FastMCP("agri-claimguard-tools")
    FASTMCP_READY = True
    FASTMCP_IMPORT_ERROR = ""
except ImportError as exc:
    mcp = None
    FASTMCP_READY = False
    FASTMCP_IMPORT_ERROR = str(exc)


def mcp_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    tool_name = func.__name__.removesuffix("_func")
    if mcp is not None:
        mcp.tool(func, name=tool_name)
    return func


def lc_tool(func: Callable[..., Any]) -> StructuredTool:
    return StructuredTool.from_function(func, name=func.__name__.removesuffix("_func"))


@mcp_tool
def validate_claim_func(claim: dict) -> str:
    """Validate mandatory claim fields."""
    required_fields = [
        "farmer_name",
        "policy_id",
        "crop",
        "district",
        "loss_reason",
        "loss_date",
    ]
    missing = [field for field in required_fields if not claim.get(field)]

    if missing:
        return f"Missing fields: {', '.join(missing)}"

    return "Claim is valid."


@mcp_tool
def normalize_crop_func(crop: str) -> str:
    """Normalize crop names."""
    crop_map = {
        "paddy": "Rice",
        "rice": "Rice",
        "maize": "Maize",
        "corn": "Maize",
        "cotton": "Cotton",
        "wheat": "Wheat",
    }

    return crop_map.get(crop.lower(), crop.title())


@mcp_tool
def normalize_location_func(location: str) -> str:
    """Normalize district names."""
    location_map = {
        "hyd": "Hyderabad",
        "blr": "Bengaluru",
        "vizag": "Visakhapatnam",
    }

    return location_map.get(location.lower(), location.title())


@mcp_tool
def check_policy_func(policy_id: str) -> str:
    """Look up policy status."""
    policies = {
        "POL123": "Active",
        "POL456": "Expired",
        "POL789": "Active",
    }

    return policies.get(policy_id.upper(), "Policy Not Found")


@mcp_tool
def hybrid_search_tool_func(query: str) -> list:
    """Perform hybrid search using semantic search, BM25, and RRF."""
    return hybrid_retriever(query)


@mcp_tool
def get_weather_func(city: str) -> str:
    """Get current weather information for a city."""
    geolocator = Nominatim(user_agent="weather-agent")
    location = geolocator.geocode(city)

    if location is None:
        return f"Could not find location: {city}"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "precipitation",
                "weather_code",
            ]
        ),
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    weather = response.json()["current"]

    return f"""
City: {city}
Temperature: {weather["temperature_2m"]} C
Humidity: {weather["relative_humidity_2m"]} %
Wind Speed: {weather["wind_speed_10m"]} km/h
Precipitation: {weather["precipitation"]} mm
Weather Code: {weather["weather_code"]}
"""


@mcp_tool
def search_historical_claims_func(crop: str, district: str, loss_reason: str) -> str:
    """Search historical agricultural insurance claims from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            claim_id,
            farmer_name,
            crop,
            district,
            loss_reason,
            claim_status,
            payout_percentage,
            claim_amount,
            approved_amount,
            claim_date
        FROM historical_claims
        WHERE
            LOWER(crop)=LOWER(?)
            AND LOWER(district)=LOWER(?)
            AND LOWER(loss_reason)=LOWER(?)
        ORDER BY claim_date DESC
        LIMIT 5
        """,
        (crop, district, loss_reason),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No similar historical claims found."

    results = []
    for row in rows:
        results.append(
            f"""
Claim ID : {row['claim_id']}
Farmer : {row['farmer_name']}
Crop : {row['crop']}
District : {row['district']}
Loss Reason : {row['loss_reason']}
Claim Status : {row['claim_status']}
Claim Amount : {row['claim_amount']}
Approved Amount : {row['approved_amount']}
Payout % : {row['payout_percentage']}
Claim Date : {row['claim_date']}
"""
        )

    return "\n".join(results)


@mcp_tool
def historical_statistics_func(crop: str, district: str) -> str:
    """Return statistics about previous claims."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*),
            AVG(payout_percentage),
            SUM(
                CASE
                WHEN claim_status='Approved'
                THEN 1
                ELSE 0
                END
            )
        FROM historical_claims
        WHERE
            LOWER(crop)=LOWER(?)
            AND LOWER(district)=LOWER(?)
        """,
        (crop, district),
    )
    total, avg_payout, approved = cursor.fetchone()
    conn.close()

    avg_payout = avg_payout or 0
    approved = approved or 0

    return f"""
Total Claims : {total}
Approved Claims : {approved}
Average Payout : {avg_payout:.2f}%
"""


@mcp_tool
def collect_evidence_func(
    claim_result: str,
    policy_result: str,
    weather_result: str,
    historical_result: str,
) -> dict:
    """Collect outputs from all specialist agents."""
    return {
        "Claim Agent": claim_result,
        "Policy Agent": policy_result,
        "Weather Agent": weather_result,
        "Historical Agent": historical_result,
    }


@mcp_tool
def inspect_claim_information_func(
    claim: dict,
    policy_result: str,
    weather_result: str,
    historical_result: str,
    evidence_result: str,
) -> dict:
    """Return all specialist outputs for reasoning."""
    return {
        "claim": claim,
        "policy": policy_result,
        "weather": weather_result,
        "historical": historical_result,
        "evidence": evidence_result,
    }


@mcp_tool
def validate_compliance_func(
    claim: dict,
    reasoning_result: str,
    evidence_result: str,
) -> dict:
    """Validate final recommendation against compliance rules."""
    return {
        "claim": claim,
        "reasoning": reasoning_result,
        "evidence": evidence_result,
    }


validate_claim = lc_tool(validate_claim_func)
normalize_crop = lc_tool(normalize_crop_func)
normalize_location = lc_tool(normalize_location_func)
check_policy = lc_tool(check_policy_func)
hybrid_search_tool = lc_tool(hybrid_search_tool_func)
get_weather = lc_tool(get_weather_func)
search_historical_claims = lc_tool(search_historical_claims_func)
historical_statistics = lc_tool(historical_statistics_func)
collect_evidence = lc_tool(collect_evidence_func)
inspect_claim_information = lc_tool(inspect_claim_information_func)
validate_compliance = lc_tool(validate_compliance_func)
