import json
from datetime import datetime, timedelta
from pathlib import Path

import requests
from icalendar import Calendar, Event

json_url = "https://www.framundanibeinni.is/api/schedule"


def get_json():
    response = requests.get(json_url)
    return response.json()


def extract_values(key, flattened_list):
    grouped_by_provider = {}
    for item in flattened_list:
        provider = item.get(key)
        if provider:
            if provider not in grouped_by_provider:
                grouped_by_provider[provider] = []
            grouped_by_provider[provider].append(item)
    return grouped_by_provider


def write_ical(group, folder):
    for provider, items in group.items():
        calendar = Calendar()
        calendar.add("prodid", f"-//Framundan í beinni// - {provider} - ical")
        calendar.add("version", "2.0")
        for item in items:
            date_string = " ".join((item["date"], item["time"]))
            item_date_time = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            item_event = Event()
            item_event.add(
                "summary", f"{item['name']} - {item['sport']} - {item['channel']}"
            )
            item_event.add("description", f"{item['name']} - {item['sport']}")
            item_event.add("dtstart", item_date_time)
            item_event.add("dtend", item_date_time + timedelta(hours=1))
            item_event.add("dtstamp", item_date_time)
            item_event["uid"] = f"{item_date_time.isoformat()}/{item['name']}"
            calendar.add_component(item_event)
        filename = f"icals/{folder}/{provider}.ics"
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "wb") as ics_file:
            ics_file.write(calendar.to_ical())


def parse_json(json_doc):
    flattened_list = []
    for key, value in json_doc["schedule"].items():
        for item in value:
            flattened_list.append(item)

    providers = extract_values("provider", flattened_list)
    sports = extract_values("sport", flattened_list)
    sportgroups = extract_values("sportGroup", flattened_list)
    write_ical(providers, "stodvar")
    write_ical(sports, "flokkar")
    write_ical(sportgroups, "ithrottaflokkar")
    write_ical({"allt": flattened_list}, "allt")
    # write_ical(sportgroups)


json_doc = get_json()
parse_json(json_doc)
