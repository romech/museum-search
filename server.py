from flask import Flask, request, abort, jsonify

import elastic

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
    else:
        return abort(401)


if __name__ == '__main__':
    app.run(port=8888)
