from chalice import Chalice, Response
"""
GET        /v2/timereport/user/<user_id>
GET        /v2/timereport/user/<user_id>?startDate=YYYYMMDD&endDate=YYYYMMDD
POST       /v2/timereport/event
GET        /v2/timereport/event/?startDate=YYYYMMDD&endDate=YYYYMMDD
GET        /v2/timereport/event/<_id>
PUT        /v2/timereport/event/<_id>
DELETE     /v2/timereport/event/<_id>

{'user_id': 'U2FGC795G', 'user_name': 'kamger', 'reason': 'vab', 'event_date': datetime.datetime(2018, 12, 5, 0, 0), 'hours': '8'}
{"user_id": "U2FGC795G", "user_name": "kamger", "reason": "vab", "event_date": "2018-12-03", "hours":8}
"""

app = Chalice(app_name='backend_api')
app.debug = True

@app.route('/timereport/user/{user_id}', methods=['GET'])
def get_user_by_id(user_id):
    return {"user_id": user_id}

@app.route('/timereport/event', methods=['POST'])
def create_event():
    return Response(body=app.current_request.raw_body.decode(),
                    status_code=200,
                    headers={'Content-Type': 'application/json'})

@app.route('/timereport/event/{_id}', methods=['GET'])
def get_event_by_id(_id):
    return {'event_id': _id}

@app.route('/timereport/event/{_id}', methods=['PUT'])
def put_event_by_id(_id):
    return app.current_request.json_body

@app.route('/timereport/event/{_id}', methods=['DELETE'])
def delete_event_by_id(_id):
    return {'event_id': _id}
