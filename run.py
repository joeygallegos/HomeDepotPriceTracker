#!/usr/bin/env python3
import requests
import json
import re
from datetime import datetime


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"

item_links = [
    "https://www.homedepot.com/p/Deckmate-2-in-Green-Exterior-Self-Starting-Star-Flat-Head-Wood-Deck-Screws-8-1-lb-126-Pieces-2DMG1/305418731",
    "https://www.homedepot.com/p/Nexgrill-29-in-Barrel-Charcoal-Grill-Smoker-in-Black-810-0029/306148311",
    "https://www.homedepot.com/p/Everbilt-3-4-in-FHT-x-3-4-in-FIP-Brass-Adapter-Fitting-801659/300096153",
]

stores = [534, 618, 6561]
API_URL = "https://www.homedepot.com/federation-gateway/graphql?opname=productClientOnlyProduct"


class bot:
    session = None


def setup(obj):
    obj.session = requests.Session()
    obj.session.cookies.update({})
    obj.session.headers.update({})
    return obj


print("Setting up worker bot")
worker = setup(bot())

# using graph query and JSON payload, make POST to hydration API to get the data for an item
def get_item_payload(store=0, item=000000, write_to_log=False):
    ql_query = None
    with open("query.dat", "r") as file:
        ql_query = file.read().splitlines(True)

    # TODO: Fix payload string variable replacement and string replacement
    payload = (
        '{"operationName":"productClientOnlyProduct","variables":{"skipSpecificationGroup":false,"skipSubscribeAndSave":false,"skipKPF":false,"itemId":"'
        + str(item)
        + '","storeId":"'
        + str(store)
        + '","zipCode":"77449"},"query":"'
        + str(ql_query).replace("['", "").replace("']", "").replace("', '", "")
        + '"}'
    )
    headers = {
        "authority": "www.homedepot.com",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www.homedepot.com",
        "pragma": "no-cache",
        "user-agent": user_agent,
        "x-experience-name": "general-merchandise",
        "accept-encoding": "gzip, deflate, br",
        "x-hd-dc": "origin",
    }
    result = requests.post(
        API_URL,
        data=payload,
        headers=headers,
    )

    if write_to_log:
        nonce = str(int(datetime.now().timestamp()))
        with open(
            nonce + "_response.json",
            "a+",
            encoding="utf-8",
        ) as f:
            f.write(result.text)
            f.close()

    return json.loads(result.text)


# get item price from payload
def get_price(response_json):
    if response_json.get("data"):
        if response_json.get("data").get("product"):
            price = response_json.get("data").get("product").get("pricing").get("value")
            return price
    return None


# get item name from payload
def get_name(response_json):
    if response_json.get("data"):
        if response_json.get("data").get("product"):
            name = (
                response_json.get("data")
                .get("product")
                .get("identifiers")
                .get("productLabel")
            )
            return name
    return None


# get item id from store link
def get_item_id_from_url(url):
    return re.search(r"(\d+)(/*)$", url).group(0)


# examples
for link in item_links:
    item_id = get_item_id_from_url(link)
    payload = get_item_payload(534, item_id, False)
    print("$" + str(get_price(payload)) + " - " + str(get_name(payload)))
