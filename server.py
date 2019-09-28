from flask import Flask, request, abort, jsonify

import elastic
from data_store import buildings

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
        loc = buildings.find_human_readable(id)
        if not loc:
            continue

        loc['text'] = obj['name'] + '\n' + loc['text']
        return jsonify(loc)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8888)
