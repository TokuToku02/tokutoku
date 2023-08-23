from bottle import default_app, get, post, run, HTTPResponse, request, TEMPLATE_PATH, jinja2_template as template, static_file, route, redirect
from dotenv import load_dotenv
import os
import openai
import backtrace

app = default_app()
TEMPLATE_PATH.append("./template")

backtrace.hook(
    reverse=True,
    strip_path=True
)


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


@app.route("/")
def index():
    context = Context()
    context.add("msg", "hello world")
    return template("index.html", ctx=context.to_template())


@get("/setting")
def setting():
    context = Context()
    with open("./rule.txt", mode="r") as rule_file:
        context.add("rule", "".join(rule_file.readlines()))
    return template("setting.html", ctx=context.to_template())


@post("/setting")
def setting():
    rule = request.forms.rule
    with open("./rule.txt", mode="w") as rule_file:
        rule_file.writelines(rule.split("\n"))
    redirect('/')


@post("/ingen")
def ingen():
    try:
        context = Context()

        org = request.forms.input
        model = request.forms.model
        with open("./rule.txt", mode="r") as rule_file:
            rule = "".join(rule_file.readlines())
            prompt = f"""
下記手順に従って、入力文を変換してください。

手順
{rule}

入力文：
{org}

変換後：
        """

        load_dotenv()
        openai.api_key = os.environ.get('OPENAI_API_KEY')

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        context.add("result", response.choices[0]["message"]["content"].strip())

        return template("result.html", ctx=context.to_template())
    except Exception as e:
        return e.error.message

if __name__ == "__main__":
    run(host="0.0.0.0", port=8000)
