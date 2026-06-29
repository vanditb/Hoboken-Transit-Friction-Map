import requests


LAT = 40.7433
LON = -74.0324
POINTS_URL = f"https://api.weather.gov/points/{LAT},{LON}"

HEADERS = {
    "User-Agent": "Hoboken Transit Friction Map student prototype (contact: vanditb)",
}


def fetch_json(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.json()


def main():
    try:
        point_data = fetch_json(POINTS_URL)
        forecast_url = point_data["properties"]["forecast"]
        forecast_data = fetch_json(forecast_url)
    except requests.RequestException as error:
        print(f"Could not fetch National Weather Service data: {error}")
        return
    except KeyError as error:
        print(f"Weather response did not include expected field: {error}")
        return

    periods = forecast_data["properties"]["periods"][:5]

    print("National Weather Service forecast periods for Hoboken:")
    for period in periods:
        name = period.get("name", "Unknown period")
        temperature = period.get("temperature", "unknown")
        unit = period.get("temperatureUnit", "")
        forecast = period.get("shortForecast", "No short forecast")
        print(f"- {name}: {temperature}{unit}, {forecast}")


if __name__ == "__main__":
    main()
