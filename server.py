from flask import Flask, request, abort, jsonify

import elastic
from data_store import buildings

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
