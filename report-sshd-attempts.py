import re
import requests
import json
from statsd import StatsClient
from datetime import datetime
from pprint import pprint
from dateutil.parser import parse

IP_REGEX = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
DATE_REGEX = re.compile(r"(\w{3}\s{1,2}\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})")
CONNECTION_ATTEMPT_REGEX = re.compile(
    r"(\w{3}\s{1,2}\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}) hyrule sshd\[\d{1,}\]: Connection from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .*"
)


def read_auth_log_file_last_24_hours():
    sshd_connection_attempts = []
    with open("/var/log/auth.log") as f:
        for line in reversed(f.readlines()):

            has_date_line = DATE_REGEX.search(line)
            if has_date_line:
                date = parse(has_date_line.group(0))

                if not log_date_is_within_24_hours(date):
                    continue
                if CONNECTION_ATTEMPT_REGEX.search(line):
                    ip = IP_REGEX.search(line).group(0)
                    sshd_connection_attempts.append(ip)
    print(f"Total of {len(sshd_connection_attempts)} connection attempts")
    return sshd_connection_attempts


def log_date_is_within_24_hours(log_datetime):
    one_day_in_seconds = 24 * 60 * 60
    delta = datetime.now() - log_datetime
    return delta.days * 24 * 60 * 60 + delta.seconds <= one_day_in_seconds


def get_location_from_ips(ips):
    responses = []
    for chunk in chunker(ips, 99):
        responses += requests.post(
            "http://ip-api.com/batch?fields=country,regionName,lat,lon",
            params={"fields": "country,regionName"},
            json=chunk,
        ).json()
    return responses

def filter_empty_locations(locations):
    return list(filter(lambda location: location.get('country') != None, locations))


def send_metrics_to_telegraf(statsd_client, metrics):
    pass


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


if __name__ == "__main__":
    statsd_client = StatsClient(
        host="localhost", port=8125, prefix="hyrule", maxudpsize=512, ipv6=False
    )
    connection_attempts = read_auth_log_file_last_24_hours()
    locations = filter_empty_locations(get_location_from_ips(connection_attempts))
    for location in locations:
        pprint(location)
        try:
            statsd_client.incr(
                "ssh_attempts",
                tags={
                    "country": location.get("country"),
                    "region": location.get("regionName"),
                    "latitude": location.get("lat"),
                    "longitude": location.get("lon")
                },
            )
        except UnicodeEncodeError as error:
            pprint(f"Could not ascii encode {json.dumps(location)}")
