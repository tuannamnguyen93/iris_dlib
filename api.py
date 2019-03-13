# -*- coding:utf8 -*-
# !/usr/bin/env python
from __future__ import print_function
from future.standard_library import install_aliases
import json
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS, cross_origin
import os
from detect_blinks import save_csv
install_aliases()
app = Flask(__name__)
cors = CORS(app)

threshold_confidence = 0.5
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request! Thiếu thông tin'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Some thing wrong with models'}), 500)

@app.route('/conversation', methods=['POST'])
@cross_origin()
def conversation():
    req = request.get_json(silent=True, force=True)
    # print(json.dumps(req,encoding='utf8',ensure_ascii=False,indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print('OK')
    return r

def processRequest(req):
    # query = req["query"]
    try:
        save_csv()
    except ValueError:
        print('Something wrong')
    response = {
        'response':  "OK",
    }
    return response

if __name__ == '__main__':
    # processRequest({})
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port,host ='0.0.0.0')
