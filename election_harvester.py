import json
from datetime import datetime
from operator import itemgetter
from pprint import pprint as pp
from time import sleep

import requests
from xml.etree import ElementTree

# URL_ROOT = "https://media.election.net.nz/electionresults_2017/xml"
URL_ROOT = "https://media.election.net.nz/xml"
URL_PARTIES = "{}/parties.xml".format(URL_ROOT)
URL_ELECTION = "{}/election.xml".format(URL_ROOT)
SLEEP_INTERVAL = 20  # seconds to sleep


def message(s):
    print("{}: {}".format(datetime.now().strftime("%H:%M:%S"), s))


def harvest_xml(url, dst_file, verbose=True):
    response = requests.get(url)
    if response.status_code == 200:
        with open(dst_file, "wb") as file:
            file.write(response.content)
        if verbose:
            message("Harvested: {}".format(dst_file))
        return response.content
    else:
        message("* ERROR {} returned status {}".format(url, response.status_code))
    return None


def write_json(data, f_path):
    with open(f_path, "w") as outfile:
        json.dump(data, outfile, indent=2, sort_keys=True)
    print("{} written.".format(f_path))


class Harvester:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.parties = {}  # parties keyed by id
        self.statistics = {}
        self.party_votes = []
        self.initialise_parties()

    def harvest(self, url, dst_file, retry_delay=10.0):
        while True:
            xml = harvest_xml(url, dst_file)
            if xml:
                break
            sleep(retry_delay)
        document = ElementTree.parse(dst_file)
        return document

    def initialise_parties(self):
        document = self.harvest(URL_PARTIES, "data/parties.xml")
        for party in document.findall("party"):
            pid = party.attrib["p_no"]
            self.parties[pid] = {
                "short_name": party.find("short_name").text,
                "party_name": party.find("party_name").text,
                "registered": party.find("registered").text,
            }
        print(
            [
                p["short_name"]
                for p in self.parties.values()
                if p["registered"].lower() == "yes"
            ]
        )

    def update_election(self):
        document = self.harvest(URL_ELECTION, "data/election.xml")
        stats = document.find("statistics")
        self.statistics = {
            "total_voting_places_counted": int(
                stats.find("total_voting_places_counted").text
            ),
            "percent_voting_places_counted": float(
                stats.find("percent_voting_places_counted").text
            ),
            "total_votes_cast": int(stats.find("total_votes_cast").text),
            "percent_votes_cast": float(stats.find("percent_votes_cast").text),
            "total_electorates_final": int(stats.find("total_electorates_final").text),
            "percent_electorates_final": float(
                stats.find("percent_electorates_final").text
            ),
            "total_minimal_votes": int(stats.find("total_minimal_votes").text),
            "total_special_votes": int(stats.find("total_special_votes").text),
            "total_registered_parties": int(
                stats.find("total_registered_parties").text
            ),
        }
        self.party_votes = []
        partystatus = document.find("partystatus")
        for party in partystatus.findall("party"):
            pid = party.attrib["p_no"]
            status = self.parties[pid].copy()
            status["votes"] = int(party.find("votes").text)
            status["percent_votes"] = float(party.find("percent_votes").text)
            status["party_seats"] = int(party.find("party_seats").text)
            status["candidate_seats"] = int(party.find("candidate_seats").text)
            status["total_seats"] = int(party.find("total_seats").text)
            self.party_votes.append(status)
        self.party_votes.sort(key=itemgetter("total_seats"), reverse=True)

    def console_update(self):
        print(
            "There are {:,} votes counted ({}%)".format(
                self.statistics["total_votes_cast"],
                self.statistics["percent_votes_cast"],
            )
        )
        for party in self.party_votes[:4]:
            print(
                "  {}: {} party seats, {} candidate seats, {:,} votes ({}%)".format(
                    party["short_name"],
                    party["party_seats"],
                    party["candidate_seats"],
                    party["votes"],
                    party["percent_votes"],
                )
            )
        print("")

    def export(self):
        write_json(self.statistics, 'data/statistics.json')
        write_json(self.party_votes, 'data/party_votes.json')


def main():
    harvester = Harvester()
    while True:
        harvester.update_election()
        harvester.console_update()
        harvester.export()
        sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()