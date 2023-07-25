import json
import random
import string
import sys
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

class HttpProxy(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/help':
            return self.__help_message()

        if self.path == '/send-request':
            return self.__send_request()

        return self.__send_not_found_error()

    def __send_request(self):
        try:
            self.__check_json_request_content_type()
        except Exception as err:
            return self.__send_bad_request_error(err)

        data = self.__get_request_body()

        try:
            self.__validate_request_body(data)
        except Exception as err:
            return self.__send_bad_request_error(err)

        try:
            target = data['target']
            method = data['method']
            headers = data.get('headers', dict())
            payload = data.get('payload', None)
            param = data.get('param', None)

            if payload and param:
                self.__update_param_in_payload(payload, param)

            response = self.__sent_http_request(target, method, headers, payload)

            request_info = self.__get_request_info(data)
            print(request_info)
            response_info = self.__get_response_info(response)
            print(response_info)

            return self.__send_result(request_info + response_info)
        except Exception as err:
            return self.__send_internal_server_error(err)

    def __sent_http_request(self, target, method, headers, payload):
        match method.upper():
            case 'GET':
                return requests.get(target, headers=headers, data=payload)
            case 'POST':
                return requests.post(target, headers=headers, data=payload)
            case 'PUT':
                return requests.put(target, headers=headers, data=payload)
            case 'PATCH':
                return requests.patch(target, headers=headers, data=payload)
            case 'DELETE':
                return requests.delete(target, headers=headers, data=payload)

    def __update_param_in_payload(self, payload, param):
        value = payload[param]

        if type(value) == int:
            payload[param] = self.__get_random_int()
        elif type(value) == float:
            payload[param] = self.__get_random_float()
        elif type(value) == str:
            payload[param] = self.__get_random_string(value)
        elif type(value) == bool:
            payload[param] = self.__get_random_bool(value)
        elif type(value) == dict:
            for key in value:
                self.__update_param_in_payload(payload[param], key)
        elif type(value) == list:
            for idx, v in enumerate(value):
                self.__update_param_in_payload(payload[param], idx)

    def __get_random_int(self):
        return int(random.randint(0, sys.maxsize) // 1e15)

    def __get_random_float(self):
        return random.uniform(0, sys.maxsize)

    def __get_random_string(self, value):
        return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(len(value)))

    def __get_random_bool(self, value):
        return not value

    def __get_request_info(self, data):
        target = data['target']
        method = data['method']
        payload = data.get('payload', '{}')
        headers = data.get('headers', '{}')

        target_message = f'[#] Request target: {target}\n'
        method_message = f'[#] Request method: {method}\n'
        headers_message = f'[#] Request headers: {json.dumps(headers, indent=4, sort_keys=True)}\n'
        payload_message = f'[#] Request payload: {json.dumps(payload, indent=4, sort_keys=True)}\n'

        return target_message + method_message + headers_message + payload_message

    def __get_response_info(self, response):
        return (f'[#] Response status code: {response.status_code}\n'
            f'[#] Response headers: {json.dumps(dict(response.headers), indent=4, sort_keys=True)}\n'
            f'[#] Response content:\n{response.text}')

    def __help_message(self):
        message = ('Welcome to HTTP Proxy\n'
            'To send request use GET "/send-request" path with JSON body\n'
            '\n'
            'Body fields:\n'
            'target - target to sending HTTP request - REQUIRED\n'
            'method - HTTP request method (GET|POST|PUT|PATCH|DELETE) - REQUIRED\n'
            'headers - HTTP request headers - OPTIONAL\n'
            'payload - body for HTTP request - OPTIONAL\n'
            'param - param for update to random value for HTTP request modification - OPTIONAL\n'
            '\n'
            'JSON body format example:\n'
            '{\n'
            '    "target": "https://blabla.free.beeceptor.com/my/api/path",\n'
            '    "method": "POST",\n'
            '    "headers": {\n'
            '        "Content-Type": "application/json"\n'
            '    },\n'
            '    "payload": {\n'
            '        "data": "Hello Beeceptor"\n'
            '    },\n'
            '    "param": "data"\n'
            '}\n')

        self.__send_result(message)

    def __do_response(self, status_code=200, content=''):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        response = bytes(f'{content}', 'utf8')
        self.wfile.write(response)

    def __send_not_found_error(self):
        self.__do_response(404, 'Invalid path')

    def __send_bad_request_error(self, err):
        self.__do_response(400, err)

    def __send_internal_server_error(self, err):
        print(err)
        self.__do_response(500, 'Internal server error')

    def __send_result(self, result):
        self.__do_response(200, result)

    def __get_content_type_header(self):
        return self.headers.get('Content-Type')

    def __get_request_body(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

        body = json.loads(post_body)

        return { k.lower(): v for k, v in body.items() }

    def __is_json_content_type(self, content_type):
        return content_type == 'application/json'
    
    def __check_json_request_content_type(self):
        content_type = self.__get_content_type_header()

        if not self.__is_json_content_type(content_type):
            raise Exception('Invalid Header Type: Send JSON\nFor more info send GET request to "/help" path')

    def __check_required_fields(self, data):
        if not 'target' in data and not 'method' in data:
            raise Exception('Missed "target" and "method" params')
        if not 'target' in data:
            raise Exception('Missed "target" param')
        if not 'method' in data:
            raise Exception('Missed "method" param')

    def __check_method_type(self, data):
        method = data['method'].upper()
        if not (method == 'GET' or
                method == 'POST' or
                method == 'PUT' or
                method == 'PATCH' or
                method == 'DELETE'
            ):
            raise Exception(f'Unsupported method "{method}"')

    def __check_headers(self, data):
        headers = data.get('headers', None)

        if headers:
            if not (type(headers) == dict):
                raise Exception('Invalid headers format')

    def __check_payload(self, data):
        payload = data.get('payload', None)

        if payload:
            if not (type(payload) == dict):
                raise Exception('Invalid payload format')

    def __check_param(self, data):
        param = data.get('param', None)
        payload = data['payload']

        if param:
            if not param in payload:
                raise Exception(f'Param "{param}" does not exist in payload')

    def __validate_request_body(self, data):
        self.__check_required_fields(data)
        self.__check_method_type(data)
        self.__check_headers(data)
        self.__check_payload(data)
        self.__check_param(data)


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, host='0.0.0.0', port=3000):
    print(f'Server started at port {port}. Press CTRL+C to close the server.')
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server Closed')

run(socketserver.TCPServer, HttpProxy)