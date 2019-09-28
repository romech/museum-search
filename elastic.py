import json
from functools import reduce

import elasticsearch
import elasticsearch_dsl as dsl
from elasticsearch import Elasticsearch

from utils import *
import data_store.buildings

client = Elasticsearch('95.213.38.6:9200')


def upload_file(src, index, doc, fn):
    with open(src, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for i, content in data.items():
        client.index(index=index, doc_type=doc, id=i, body=fn(content))
        print('indexed', i)


def normalize_objects(content):
    obj = {}
    obj['name'] = content['name'].get('ru', '')
    obj['text'] = content['text'].get('ru', '')
    obj['path'] = content['path']
    # OPTIONAL
    obj['year'] = content.get('year')
    obj['hall'] = content.get('hall')
    obj['building'] = content.get('building')
    obj['annotation'] = content.get('annotation')
    obj['from'] = content.get('from').get('ru')
    obj['seakeys'] = content.get('seakeys').get('ru')

    field = content.get('authors', {})
    if isinstance(field, dict):
        obj['author'] = ', '.join(filter(None, (v.get('ru') or v.get('name_ru') for k, v in field.items())))
    else:
        obj['author'] = field

    field = content['gallery']
    if field and field.get('1'):
        obj['img'] = field['1']['id02']
    else:
        obj['img'] = None

    return obj


def normalize_building(content):
    return {
        'address': maybe_get(content, 'adress'),
        'img': maybe_get(content, 'img'),
        'name': maybe_get(content, 'name'),
        'tel': maybe_get(content, 'tel'),
        'brief': maybe_get(content, 'brief'),
        'coords': maybe_get(content, 'yamapcoords'),
        'audiog': maybe_get(content, 'audiog'),
        'svg': maybe_get(content, 'img'),
        'path': maybe_get(content, 'path')
    }


def normalize_event(content):
    struct = {
        'name': maybe_get(content, 'name'),
        'path': maybe_get(content, 'path'),
        'date': maybe_get(content, 'dateBegin'),
        'price': maybe_get(content, 'price'),
    }
    if 'circ_img' in content and 'id02' in content['circ_img']:
        struct['img'] = content['circ_img']['id02']
    elif 'headimg' in content:
        struct['img'] = maybe_get(content, 'headimg')
    buildings = maybe_get(content, 'building')
    if isinstance(buildings, dict):
        buildings = next(iter(buildings.items()))[1]
    if buildings:
        bld = data_store.buildings.find_building(buildings)
        struct['building'] = bld.dict()
    return struct


def as_Q(field, query, fuzziness=1):
    return dsl.Q('match', **{field: {'query': query, 'fuzziness': fuzziness}})


def hit_to_dict(hit):
    d = hit._d_.copy()
    d['meta'] = hit.meta._d_.copy()
    return d


def search(query, index='objects', fields=('name', 'author', 'seakeys', 'text')):
    print('query:', query)
    s = dsl.Search(using=client, index=index)
    for fuzziness in range(2):
        for field in fields:
            res = s.query(as_Q(field, query, fuzziness=fuzziness)).execute()
            if res:
                return [hit_to_dict(hit) for hit in res]
        # q = reduce(lambda a, b: a | b,
        #            [as_Q(field, query) for field in fields])
        # s = dsl.Search(using=client, index=index).query(q)
        # res = s.query(q).execute()
        # if res:
        #     return [hit_to_dict(hit) for hit in res]
    return []


def search_objects(query):
    return search(query, index='objects', fields=('name', 'author', 'seakeys', 'text'))


def search_buildings(query):
    return search(query, index='buildings', fields=('name', 'brief', 'address'))


def search_events(query):
    return search(query, index='events', fields=('name', 'text'))


def index_things():
    upload_file('/home/roman/Downloads/MuseumData/objects.json', index='objects', doc='object', fn=normalize_objects)
    upload_file('/home/roman/Downloads/MuseumData/buildings.json', index='buildings', doc='building', fn=normalize_building)
    upload_file('/home/roman/Downloads/MuseumData/events.json', index='events', doc='event', fn=normalize_event)



def sample_search(text='картины Пискассо'):
    for hit in search_objects('картины Пикассо'):
        print(json.dumps(hit, ensure_ascii=False))


if __name__ == '__main__':
    # print(sample_search())
    print(search('египетская империя', index='events', fields=('name', 'text')))
    # print(len(search_buildings('главное здание')))
    # index_things()

