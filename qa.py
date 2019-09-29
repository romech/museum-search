import json
from pprint import pprint
import random
import time

import requests


def qa(knowledge, question):
    resp = requests.post('https://7005.lnsigo.mipt.ru/answer',
                         json={'text1': [knowledge], 'text2': [question]})
    return tuple(reversed(resp.json()[0]))


def qa_multiple(knowledge, question, ttl=4):
    start = time.time()
    res = []
    for k in knowledge:
        res.append(qa(k, question))
        print(qa(k, question))
        if time.time() + 1.2 > start + ttl:
            break
    return sorted(res, reverse=True)
    # return resp.content.decode(encoding='unicode-escape')

headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

def find_context_in(question, index):
    query = json.dumps({
        "query": {
            "match": {
                "text": question
            }
        },
        "highlight": {
            "fragment_size": 512,
            # "phrase_limit": 10,
            "pre_tags": [""],
            "post_tags": [""],
            "fields": {
                "text": {}
            }
        }
    })
    resp = requests.get(f'http://demo6.charlie.vkhackathon.com:9200/{index}/_search', data=query, headers=headers).json()
    # pprint(resp.json()['hits']['hits'])
    highlights = ['\n'.join(h['highlight']['text']) for h in resp['hits']['hits']]
    pprint(resp['hits'])
    scores = [h['_score'] for h in resp['hits']['hits']]
    return list(zip(scores, highlights))


def find_context(question):
    candidates = []
    # for index in ['various', 'events']:
    for index in ['wiki', 'various', 'events', 'objects']:
        candidates += find_context_in(question, index)[:2]
    if not candidates:
        return [], 0

    candidates = sorted(candidates, reverse=True)
    return [h[1] for h in candidates], candidates[0][0]


intros = ['Возможно, что ', 'Думаю, могу ответить: ', 'Нашла такой ответ: ']


def get_answer(q, verbose=False):
    contexts, top_score = find_context(q)
    if verbose:
        print(*contexts, sep='\n-------\n')
        print('Max elastic score', top_score)

    if top_score > 1:
        print('Querying Pavlov')
        answers = qa_multiple(contexts, q)
        return random.choice(intros) + answers[0][-1]

    return None


if __name__ == '__main__':
    q = "Где посмотреть картины Айвазовского?"
    print(get_answer(q, verbose=True))
