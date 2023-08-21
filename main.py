from bottle import default_app, get, run, HTTPResponse, request, TEMPLATE_PATH, jinja2_template as template, static_file, route

app = default_app()
TEMPLATE_PATH.append("./template")


class Context:
    def __init__(self):
        self.context = {}

    def add(self, name, data):
        self.context[name] = data

    def get(self, name):
        return self.context[name]

    def to_template(self):
        return self.context


@route('/static/<file_path:path>')
def static(file_path):
    return static_file(file_path, root='./static')


@app.route('<any:path>', method='OPTIONS')
def response_for_options(**kwargs):
    re = HTTPResponse(status=200, body={})
    re.set_header('Content-Type', 'application/json')

    if 'Origin' in request.headers.keys():
        re.set_header('Access-Control-Allow-Origin', request.headers['Origin'])
        re.set_header('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
        re.set_header('Access-Control-Allow-Headers', 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization')

    return re


@get("/")
def index():
    context = Context()
    context.add("msg", "hello world")
    return template("index.html", ctx=context.to_template())


if __name__ == "__main__":
    run(host="0.0.0.0", port=8000)
