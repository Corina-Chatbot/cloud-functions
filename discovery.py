import json
from datetime import datetime
from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from secrets import DISCOVERY_API_KEY

# define the IDS and URLS from Watson Discovery Service
DISCOVERY_URL = 'https://api.eu-gb.discovery.watson.cloud.ibm.com/instances/738047c5-5416-4845-8d23-c7ebd4d0c7e7'
DISCOVERY_VERSION = '2019-04-30'
ENVIRONMENT_ID = 'f3055480-a528-4b3d-bc9a-7e45e428b615'
COLLECTION_ID = '304d4569-672f-47ad-9445-0becdd0cd381'

# create an authenticator object
authenticator = IAMAuthenticator(DISCOVERY_API_KEY)
discovery = DiscoveryV1(
    version = DISCOVERY_VERSION,
    authenticator = authenticator
)
# connect to the discovery endpont
discovery.set_service_url(DISCOVERY_URL)
discovery.set_default_headers({'x-watson-learning-opt-out': "true"})
discovery.set_disable_ssl_verification(True)


def set_relevancy(query, document_id, relevance):
    """
    Set the relevance of a document for a given query.
    The relevance can be an integer between 0 and 10.
    """
    return discovery.add_training_data(
        environment_id=ENVIRONMENT_ID, 
        collection_id=COLLECTION_ID, 
        natural_language_query=query,
        examples=[
            {
                "document_id": document_id,
                "relevance": relevance
            }
        ]
    )


def do_nlp_query(query):
    """
    Perform a NLP Query on the Discovery API.
    """
    query_result = discovery.query(
        environment_id=ENVIRONMENT_ID,
        collection_id=COLLECTION_ID,
        natural_language_query=query,
        count=1,
        passages=True
    ).get_result()

    best_results = []

    # loop results
    for result in query_result["results"]:
        # save the document id and get corresponding passages for this document
        result_id = result["id"]
        passages = []
        if 'passages' in query_result:
            for passage in query_result["passages"]:
                if passage["document_id"] == result_id:
                    passages.append(passage)
                if len(passages) == 1:
                    break
        
        # get a title if available
        title = result["extracted_metadata"]["filename"] if 'title' not in result["extracted_metadata"] else result["extracted_metadata"]['title']
        # add to result list
        prev = {
            "id": result["id"],
            "url": result["metadata"]["source"]["url"],
            "title": title,
            "concepts": result["enriched_text"]["concepts"],
            "passages": passages
        }
        best_results.append(prev)
        
    return {
        "session": query_result["session_token"],
        "results": best_results,
        "retrieved": datetime.now().strftime("%c")
    }
