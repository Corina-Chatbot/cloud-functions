from orchestrator import orchestrator
from discovery import do_nlp_query, set_relevancy


print(orchestrator({
    'action': 'DISCOVERY',
    'query': 'Was ist ein RKI'
}))

exit()

print(orchestrator({
    'action': 'FEEDBACK',
    'text': 'Was ist ein RKI',
    'feedback': 2,
    'document_id': 'web_crawl_aec17f80-02b3-5a8c-adab-7604e690f495'
}))
