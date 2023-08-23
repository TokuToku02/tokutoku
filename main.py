from bottle import default_app, get, post, run, HTTPResponse, request, TEMPLATE_PATH, jinja2_template as template, \
    static_file, route, redirect, auth_basic
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


def basic_authorization(input_id, input_password):
    with open("./basic.txt", mode="r") as basic:
        try:
            basic_id, basic_password = basic.readline().split(':')
            return input_id == basic_id and input_password == basic_password
        except ValueError:
            return True


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
        re.set_header('Access-Control-Allow-Headers',
                      'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization')

    return re


@app.route("/")
@auth_basic(basic_authorization)
def index():
    return template("index.html")


@get("/setting")
@auth_basic(basic_authorization)
def setting():
    context = Context()
    with open("./rule.txt", mode="r") as rule_file:
        context.add("rule", "".join(rule_file.readlines()))
        with open("./basic.txt", mode="r") as basic:
            try:
                basic_id, basic_password = basic.readline().split(':')
            except ValueError:
                basic_id = ''
                basic_password = ''
            context.add("basic_id", basic_id)
            context.add("basic_password", basic_password)
    return template("setting.html", ctx=context.to_template())


@post("/setting")
def setting():
    rule = request.forms.rule
    with open("./rule.txt", mode="w") as rule_file:
        rule_file.writelines(rule.split("\n"))

    basic_id = request.forms.basic_id
    basic_password = request.forms.basic_password
    with open("./basic.txt", mode="w") as basic:
        if basic_id and basic_password:
            basic.writelines([basic_id + ':' + basic_password])
        else:
            basic.writelines([])
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
