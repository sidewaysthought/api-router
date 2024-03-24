import requests
import yaml
from flask import Flask, request, jsonify

app = Flask(__name__)
config = {}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def pass_thru(path):
    global config
    response = None
    for route in config['routes']:
        possible_methods = route['method'].split(', ')
        
        endpoint = route['endpoint']
        if '{' in route['endpoint'] and '}' in route['endpoint']:
            # for each {...} pair, replace with the corresponding value in the request path
            # /v1/{resource}/{id} -> /v1/users/123
            for key in route['endpoint'].split('/'):
                if key.startswith('{') and key.endswith('}'):
                    key = key[1:-1]
                    if key in path.split('/'):
                        endpoint = endpoint.replace(f'{{{key}}}', path.split('/')[path.split('/').index(key)])          

        if endpoint == path and request.method in possible_methods:
            if route['method'] == 'GET':
                response = requests.get(endpoint, headers=request.headers)
            elif route['method'] == 'POST':
                response = requests.post(endpoint, headers=request.headers, json=request.json)
            break
        if response is None:
            return jsonify({'error': 'Route not found'}), 404
        else:
            return jsonify(response.json()), response.status_code

def main():
    global config
    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    app.run(host=config['listen_ip'], port=config['listen_port'])

if __name__ == '__main__':
    main()
