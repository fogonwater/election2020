# election2020

Harvester and data parser for NZ Election website.

This is a single Python script that requests XML from [https://media.election.net.nz/xml](https://media.election.net.nz/xml) on a regular basis and transforms it into JSON.

### Dependencies

Python 3.x
[Requests](https://requests.readthedocs.io/en/master/)



### Executing program

* Make sure URL_ROOT is configured to correct URL (should be "https://media.election.net.nz/xml")
* Make sure SLEEP_INTERVAL is appropriate number of seconds (20 is default)
* run `election_harvester.py`


On startup, the harvester will request a copy of all parties from the elections data service. It builds an internal dictionary, keyed by party IDs, to enable the harvester to easily look up election results.

It requests fresh election results, parses the results to JSON, and then sleeps for 20 seconds.

Party results are an array of parties, sorted by total_seats. The data looks like this when live.


```
[
    {
        "candidate_seats": 30,
        "party_name": "Labour Party",
        "party_seats": 17,
        "percent_votes": 37.2,
        "registered": "yes",
        "short_name": "Labour Party",
        "total_seats": 47,
        "votes": 840528
    },
    {
        "candidate_seats": 22,
        "party_name": "And so on....",
    }
]
```