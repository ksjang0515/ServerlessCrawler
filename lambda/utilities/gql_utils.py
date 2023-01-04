from constants import PROXY


def get_total_data(bounds_list, keyword):
    data = [
        {
            "operationName": "getPlacesList",
            "query": """query getPlacesList($input: PlacesInput, ) {
  businesses: places(input: $input) {
    total
  }
}
""",
            "variables": {
                "input": {
                    "query": keyword,
                    "bounds": bounds,
                },
                "isBounds": True,
            },
        }
        for bounds in bounds_list
    ]

    return data


def get_items_data(query_string, bounds, start=1, amt=50):
    data = [
        {
            "operationName": "getPlacesList",
            "query": """query getPlacesList($input: PlacesInput, ) {
  businesses: places(input: $input) {
    items {
      id
      name
      category
      roadAddress
      fullAddress
      phone
    }
  }
}
""",
            "variables": {
                "input": {
                    "display": amt,
                    "bounds": bounds,
                    "query": query_string,
                    "start": start,
                },
            },
        }
    ]

    return data


def get_header():
    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ko",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    }

    return header


def get_proxy():
    return {"https": PROXY, "http": PROXY}
