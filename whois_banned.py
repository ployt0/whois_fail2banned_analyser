#!/usr/bin/env python3
import datetime
import ipaddress
import subprocess
import sys

from ipwhois import IPWhois, HTTPLookupError
import json


def main():
    result = subprocess.run(
        "sudo fail2ban-client status sshd",
        shell=True, capture_output=True, text=True
    )
    for line in result.stdout.split("\n"):
        if "Banned IP list:" in line:
            ips = map(ipaddress.ip_address, line.split(":")[-1].strip().split(" "))
            break
    else:
        return

    sorted_ips = sorted(ips)

    tstamp = datetime.datetime.utcnow().strftime("%b%d%H")
    # Don't bother to request more than hourly.
    try:
        with open(f"{tstamp}.json") as f:
            whois_result = json.load(f)
    except FileNotFoundError:
        whois_result = get_fresh_whois_data(sorted_ips, tstamp, whois_result)

    short_recs = [(x["asn_country_code"], x["asn_date"], x["asn"].rjust(6), x["asn_cidr"].rjust(19), x["asn_description"]) for x in whois_result]

    # We've sorted by IP address, quite revealing, how much is CHINANET-BACKBONE.
    for x in sorted(short_recs, key=lambda y: (y[0], y[2])):
        print(*x)
    # Patterns, in a space of 2**32, smh.


def get_fresh_whois_data(sorted_ips, tstamp, whois_result):
    whois_result = []
    bad_ips = []
    print()
    cnt = len(sorted_ips) - 1
    bar_len = 80
    for i, ip in enumerate(sorted_ips):
        prcnt_done = i / float(cnt) * 100.0
        steps_done = int(prcnt_done * bar_len)
        steps_left = bar_len - steps_done
        sys.stdout.write(
            f'\r{int(prcnt_done):>3}% [' + '█' * steps_done + ' ' * steps_left + ']')
        try:
            whois_result.append(IPWhois(ip).lookup_rdap())
        except HTTPLookupError as hle:
            bad_ips.append(ip)
    # 5 out of 200 escaped, why? Try looking elsewhere for them?
    print(f"These addresses escaped whois: {bad_ips}")
    with open(f"{tstamp}.json", "w") as f:
        json.dump(whois_result, f)
    return whois_result


if __name__ == "__main__":
    main()

