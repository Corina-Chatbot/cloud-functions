import sys
import requests
import json
import datetime
from dateutil import parser
import re

from translation_countries import TRANSLATION_COUNTRIES
from discovery import do_nlp_query
from risikogebiete import RISIKO_GEBIETE

cache = {}


def cached(name, data_fn):
    now = datetime.datetime.now()
    data = None
    if name not in cache or cache[name] is None or cache[name]['retrieved'] + datetime.timedelta(hours=4) < now:
        data = data_fn()
        cache[name] = {
            'data': data,
            'retrieved': now
        }
    else:
        data = cache[name]['data']
        now = cache[name]['retrieved']
    
    now_str = now.strftime("%c")
    return data, now_str


def get_openmedical_de():
    response1 = requests.get("https://covid-19.openmedical.de/index.json")
    out = response1.json()
    return out

def get_openmedical_world():
    response1 = requests.get("https://covid-19.openmedical.de/world.json")
    out = response1.json()
    return out

def get_alerts_bund():
    response1 = requests.get("https://warnung.bund.de/bbk.mowas/gefahrendurchsagen.json")
    out = response1.json()

    current = datetime.datetime.now()
    meldungen = []

    try:
        for alert in out[::-1]:
            time_sent = parser.parse(alert['sent'])
            time_sent = time_sent.replace(tzinfo=None)
            if time_sent + datetime.timedelta(days=2) < current:
                continue
            info = alert['info'][0]

            meldungen.append({
                'id': alert['identifier'],
                'time': time_sent.strftime("%c"),
                'area': info['area'][0]['areaDesc'],
                'title': info['headline'],
                'description': info['description']
            })
    except:
        return []

    return meldungen


def get_relevance(entity):
    return entity['relevance']


def orchestrator(dict):

    if dict['action'] == "FALLZAHLEN":

        bundeslandList = ["BadenWuerttemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland","Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thueringen", "Deutschland"]
        land = dict['bundesland']
        
        out = None
        retrieved = None
        
        if land in bundeslandList:
            out, retrieved = cached('openmedical_de', get_openmedical_de)
            if land == "BadenWuerttemberg":
                land = "Baden-W\u00fcrttemberg"
            if land == "Thueringen":
                land = "Th\u00fcringen"
            quelle = "https://covid-19.openmedical.de/ (Robert Koch Institut)"
        else:
            out, retrieved = cached('openmedical_world', get_openmedical_world)
            quelle = "https://covid-19.openmedical.de/international.html (World Health Organization)"
        infectedTOT=0
        deadTOT = 0
        infectedTOTdiff=0
        deadTOTdiff = 0
        infiziert=0
        tot=0
        datum=""
        infiziert_diff=0
        tot_diff=0
        for state in out:
            if state['data'] != []:
                infectedTOT=infectedTOT + int(state['data'][-1]['infected'])
                deadTOT=deadTOT + int(state['data'][-1]['dead'])
                infectedTOTdiff=infectedTOTdiff + int(state['data'][-1]['infected_diff'])
                deadTOTdiff=deadTOTdiff + int(state['data'][-1]['dead_diff'])
                date_ger = state['data'][-1]['date']
                if state['state']==land:
                    infiziert=state['data'][-1]['infected']
                    tot=state['data'][-1]['dead']
                    datum=state['data'][-1]['date']
                    infiziert_diff=state['data'][-1]['infected_diff']
                    tot_diff=state['data'][-1]['dead_diff']
        if land == "Deutschland":
            return {"state" : land, "infected" : infectedTOT, "dead": deadTOT, "infected_diff": infectedTOTdiff, "dead_diff": deadTOTdiff, "date": date_ger, "quelle": quelle, 'retrieved': retrieved}
        else:
            land_german = TRANSLATION_COUNTRIES[land] if land in TRANSLATION_COUNTRIES else land
            return {"state" : land_german, "infected" : infiziert, "dead": tot, "infected_diff": infiziert_diff, "dead_diff": tot_diff, "date": datum, "quelle": quelle, "retrieved": retrieved}
    
    if dict['action'] == "RISIKOGEBIETE":
        if 'country' in dict:
            if dict['country'] in RISIKO_GEBIETE:
                return {
                    'results': RISIKO_GEBIETE[dict['country']]['areas'],
                    'retrieved': RISIKO_GEBIETE[dict['country']]['date']
                }
            else:
                return {
                    "results": None,
                    "retrieved": datetime.datetime.now().strftime("%c")
                }
        else:
            countries = list(RISIKO_GEBIETE.keys())
            date = RISIKO_GEBIETE[countries[0]]['date']
            countries_str = countries[0] if len(countries) == 1 else ', '.join(countries[:-1]) + ' und '+countries[-1]
            return {
                'results': countries_str,
                'retrieved': date
            }

    if dict['action'] == "MELDUNGEN":
        place_query = '' if 'place' not in dict else dict['place']
        out, retrieved = cached("meldungen_bund", get_alerts_bund)
        relevant = list(filter(lambda meldung: re.search(place_query, meldung["area"], re.IGNORECASE), out))
        return {
            "alerts": relevant,
            "retrieved": retrieved
        }
    
    if dict['action'] == "NLU":
        jsonToSend = {"text": dict['text'],"features": {"sentiment": {},"categories": {},"concepts": {},"entities": {},"keywords": {}}}
        response = requests.post('https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/db856ffe-f2ed-47f3-800e-93a0faaaa0b4/v1/analyze?version=2018-11-16', json=jsonToSend, auth=('apikey', 'cF9dVhGHc4408lmaLjyse831NK_vzYtaEZXYk8ygJGFK'))
        if response.status_code != 200:
            return {}
        entities =  response.json()['entities']
        filteredEntities = list(filter(lambda entity : entity['type'] == dict['type'], entities))
        filteredEntities.sort(key = get_relevance)
        if filteredEntities != []:
            return {"entity" : filteredEntities[0]['text'] }
        else:
            return {}

    if dict['action'] == "DISCOVERY":
        response = do_nlp_query(dict['query'])
        return response