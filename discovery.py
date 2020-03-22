import json
from datetime import datetime
# Watson Services
from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

DISCOVERY_URL = 'https://api.eu-gb.discovery.watson.cloud.ibm.com/instances/738047c5-5416-4845-8d23-c7ebd4d0c7e7'
DISCOVERY_API_KEY = 'yXjkDlDkhCAVdjMI5y3E3zzhUJyggW04EJHzqrp73WEw'
DISCOVERY_VERSION = '2019-04-30'
ENVIRONMENT_ID = 'f3055480-a528-4b3d-bc9a-7e45e428b615'

COLLECTION_ID = '304d4569-672f-47ad-9445-0becdd0cd381'

authenticator = IAMAuthenticator(DISCOVERY_API_KEY)
discovery = DiscoveryV1(
    version = DISCOVERY_VERSION,
    authenticator = authenticator
)

discovery.set_service_url(DISCOVERY_URL)
discovery.set_default_headers({'x-watson-learning-opt-out': "true"})
discovery.set_disable_ssl_verification(True)

def do_nlp_query(query):
    query_result = discovery.query(
        environment_id=ENVIRONMENT_ID,
        collection_id=COLLECTION_ID,
        natural_language_query=query,
        count=1,
        passages=True
    ).get_result()

    best_results = []

    for result in query_result["results"]:

        result_id = result["id"]
        passages = []
        if 'passages' in query_result:
            for passage in query_result["passages"]:
                if passage["document_id"] == result_id:
                    passages.append(passage)
                if len(passages) == 3:
                    break

        
        title = result["extracted_metadata"]["filename"] if 'title' not in result["extracted_metadata"] else result["extracted_metadata"]['title']

        prev = {
            "id": result["id"],
            "url": result["metadata"]["source"]["url"],
            "title": title,
            "concepts": result["enriched_text"]["concepts"],
            "passages": passages
        }

        best_results.append(prev)
        
    return {
        "results": best_results,
        "retrieved": datetime.now().strftime("%c")
    }
