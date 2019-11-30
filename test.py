import json

request_str =  '{ "type":"here", "devices":["2c:fd:a1:9d:ec:c9"]}'

req = json.loads(request_str)

print(req["type"])
