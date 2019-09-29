import random

from flask import Flask, request, abort, jsonify

import elastic
from data_store import buildings
import qa
from utils import normalize_coord


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/ping')
def ping():
    return "ok"


@app.route('/search')
def search():
    query = request.args["query"]
    entity = request.args.get("entity", default="object")

    if entity == 'object':
        return jsonify(elastic.search_objects(query))
    elif entity == 'building':
        return jsonify(elastic.search_buildings(query))
    elif entity == 'event':
        return jsonify(elastic.search_events(query))
    else:
        return abort(400)


@app.route('/building_by_id')
def building_by_id():
    res = buildings.find_human_readable(request.args["id"])
    if 'ref' not in res:
        return abort(404)
    else:
        return jsonify(res)


@app.route('/where_is_it')
def where_is_it():
    query = request.args["query"]
    found_objects = elastic.search_objects(query)
    if not found_objects:
        return jsonify({'text': 'Кажется, в нашем музее нет такого экспоната'})

    for obj in found_objects:
        bld_id = obj.get('building')
        hall_id = obj.get('hall')

        id = hall_id or bld_id
        if not id:
            continue
        res = buildings.find_human_readable(id)
        if not res:
            continue

        res['text'] = f'{obj["name"]}. {res["text"]}'
        if obj['author']:
            res['text'] = f'{obj["author"]}, {res["text"]}'
        res['img'] = obj['img']
        res['object'] = obj
        res['building'] = buildings.find_building(bld_id).dict()
        if 'coords' in res['building']:
            res['coords'] = normalize_coord(res['building']['coords'])
        return jsonify(res)


@app.route('/find_event')
def find_event():
    query = request.args["query"]
    found_events = elastic.search_events(query)
    for event in found_events:
        bld = event.get('building')
        coords = normalize_coord(bld.get('coords'))
        resp = event.copy()
        resp['desc'] = resp.get('text')
        resp['text'] = f'Найдено событие: {resp["name"]}. Место проведения: {bld["name"]}.'
        resp['coords'] = coords
        return jsonify(resp)
    abort(404)


@app.route('/qa')
def question_answering():
    question = request.args["query"]

    answer = qa.get_answer(question)
    if answer:
        return answer
    else:
        return 'Не могу найти ответа'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
