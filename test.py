from orchestrator import orchestrator
from discovery import do_nlp_query, set_relevancy

print(orchestrator({
    'action': 'FEEDBACK',
    'text': 'yolo',
    'feedback': 324,
    'document_id': 'ehhh'
}))