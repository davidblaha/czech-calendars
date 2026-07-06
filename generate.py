from icalendar import Calendar, Event
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
import os


BASE_URLS = {
    "state": "https://www.kurzy.cz/kalendar/statni-svatky/",
    "important": "https://www.kurzy.cz/kalendar/vyznamne-dny/",
    "easter": "https://www.kurzy.cz/kalendar/velikonoce/",
    "christmas": "https://www.kurzy.cz/kalendar/vanoce/",
}


def fetch_events(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    events = []

    # Kurzy.cz má tabulky → bereme řádky
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 2:
            continue

        try:
            raw_date = cols[0].get_text(strip=True)
            title = cols[1].get_text(strip=True)

            # přeskočíme hlavičky
            if not raw_date or not title:
                continue

            # jednoduchý parse (např. 1.1.2026)
            parts = raw_date.split(".")
            if len(parts) < 2:
                continue

            day = int(parts[0])
            month = int(parts[1])
            year = 2026  # Kurzy.cz často neuvádí rok → fixní

            events.append({
                "title": title,
                "date": date(year, month, day)
            })

        except:
            continue

    return events


def build_calendar(events):
    cal = Calendar()

    for e in events:
        event = Event()
        event.add("summary", e["title"])
        event.add("dtstart", e["date"])
        event.add("dtend", e["date"])
        cal.add_component(event)

    return cal


def save(cal, filename):
    os.makedirs("output", exist_ok=True)

    with open(f"output/{filename}", "wb") as f:
        f.write(cal.to_ical())


def main():
    # státní svátky
    state_events = fetch_events(BASE_URLS["state"])
    save(build_calendar(state_events), "state-holidays.ics")

    # významné dny
    important_events = fetch_events(BASE_URLS["important"])
    save(build_calendar(important_events), "important-days.ics")

    # Vánoce
    christmas_events = fetch_events(BASE_URLS["christmas"])
    save(build_calendar(christmas_events), "christmas.ics")

    # Velikonoce
    easter_events = fetch_events(BASE_URLS["easter"])
    save(build_calendar(easter_events), "easter.ics")

    print("OK: calendars generated")


if __name__ == "__main__":
    main()