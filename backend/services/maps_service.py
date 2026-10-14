"""
maps_service.py
---------------
Provides distance, ETA, and routing functionality.
Integrates with Google Maps API if credentials are provided.
Falls back to Haversine distance and simulated ETA (assuming average city speeds)
if the API key is absent, ensuring zero downtime for the platform.
"""

import math
import os
import httpx
from typing import Dict, Any, Tuple
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Constants for Haversine Fallback
AVERAGE_CITY_SPEED_KMH = 35.0  # Approx city speed


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth (in km)."""
    # Convert decimal degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Radius of earth in kilometers
    r = 6371.0
    return r * c


def get_distance_and_eta(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Tuple[float, int]:
    """
    Get the distance (in km) and ETA (in minutes) between two coordinates.
    Uses Google Maps if API key is present; otherwise falls back to Haversine.
    
    Returns:
        Tuple containing (distance_in_km, eta_in_minutes)
    """
    api_key = getattr(settings, "google_maps_api_key", os.getenv("GOOGLE_MAPS_API_KEY"))

    if api_key:
        try:
            # Sync HTTP call for simplicity in this utility, or use async if needed by caller
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_lat},{origin_lng}&destinations={dest_lat},{dest_lng}&key={api_key}"
            response = httpx.get(url, timeout=5.0)
            data = response.json()
            
            if data.get("status") == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
                element = data["rows"][0]["elements"][0]
                distance_m = element["distance"]["value"]
                duration_s = element["duration"]["value"]
                
                return round(distance_m / 1000.0, 2), int(duration_s / 60)
            else:
                logger.warning(f"Google Maps API returned non-OK status: {data.get('status')}. Falling back to Haversine.")
        except Exception as e:
            logger.error(f"Error calling Google Maps API: {e}. Falling back to Haversine.")
            
    # Fallback: Haversine distance
    distance_km = _haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    # Add a 20% routing overhead since roads are not straight lines
    routing_distance_km = distance_km * 1.2
    
    # Calculate ETA in minutes
    eta_hours = routing_distance_km / AVERAGE_CITY_SPEED_KMH
    eta_minutes = max(1, int(eta_hours * 60))
    
    return round(routing_distance_km, 2), eta_minutes

