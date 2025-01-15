import re
import subprocess
import sys

from flask import Flask, jsonify, request

app = Flask(__name__)


# language=pythonregexp
LIST_REGEX = r"^\s*(?!UNIT)(?P<filename>[\w.@:\\-]+)\.service\s*(?P<load>\w+) (?P<active>\w+) (?P<sub>\w+)\s*(?P<description>.*)$"
# language=pythonregexp
DETAIL_REGEX = r"^\s*(?P<name>.*?): (?P<value>.*)$"


try:
    from . import secret
except ImportError:
    print("No secret.py found. Please create it using sample.secret.py as a template.")
    sys.exit(1)


@app.route("/")
def index():
    return "Welcome to the Systemd API"


@app.route("/list")
def list():
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {secret.TOKEN}":
        return "Unauthorized", 401

    output = subprocess.run(["systemctl", "list-units", "--type", "service"], stdout=subprocess.PIPE, text=True)

    result = []

    for service in output.stdout.splitlines():
        if match := re.match(LIST_REGEX, service):
            result.append(match.groupdict())
        else:
            print(service)

    return jsonify(result)


@app.route("/<int:service_id>")
def detail(service_id: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {secret.TOKEN}":
        return "Unauthorized", 401

    output = subprocess.run(["systemctl", "list-units", "--type", "service"], stdout=subprocess.PIPE, text=True)

    result = []

    for service in output.stdout.splitlines():
        if match := re.match(LIST_REGEX, service):
            result.append(match.groupdict())

    service = result[service_id]

    output = subprocess.run(["systemctl", "status", service["filename"]], stdout=subprocess.PIPE, text=True)

    output_lines = output.stdout.splitlines()
    output_lines = output_lines[:output_lines.index("")]  # Everything until the blank line (exclude logs)

    result = {}

    for line in output_lines:
        if match := re.match(DETAIL_REGEX, line):
            field = match.groupdict()
            result[field["name"]] = field["value"]

    return result


@app.route("/<int:service_id>/logs", defaults={"line_count": 10})
@app.route("/<int:service_id>/logs/<int:line_count>")
def logs(service_id: int, line_count: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {secret.TOKEN}":
        return "Unauthorized", 401

    output = subprocess.run(["systemctl", "list-units", "--type", "service"], stdout=subprocess.PIPE, text=True)

    result = []

    for service in output.stdout.splitlines():
        if match := re.match(LIST_REGEX, service):
            result.append(match.groupdict())

    service = result[service_id]

    output = subprocess.run(["journalctl", "-u", service["filename"], "-n", str(line_count)], stdout=subprocess.PIPE, text=True)

    return jsonify({"result": output.stdout.splitlines()})


@app.route("/<int:service_id>/start", methods=["POST"])
def start(service_id: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {secret.TOKEN}":
        return "Unauthorized", 401

    output = subprocess.run(["systemctl", "list-units", "--type", "service"], stdout=subprocess.PIPE, text=True)

    result = []

    for service in output.stdout.splitlines():
        if match := re.match(LIST_REGEX, service):
            result.append(match.groupdict())

    service = result[service_id]

    output = subprocess.run(["sudo", "systemctl", "start", service["filename"]], stdout=subprocess.PIPE, text=True)

    return jsonify({"result": output.stdout.splitlines()})


@app.route("/<int:service_id>/stop", methods=["POST"])
def stop(service_id: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {secret.TOKEN}":
        return "Unauthorized", 401

    output = subprocess.run(["systemctl", "list-units", "--type", "service"], stdout=subprocess.PIPE, text=True)

    result = []

    for service in output.stdout.splitlines():
        if match := re.match(LIST_REGEX, service):
            result.append(match.groupdict())

    service = result[service_id]

    output = subprocess.run(["sudo", "systemctl", "stop", service["filename"]], stdout=subprocess.PIPE, text=True)

    return jsonify({"result": output.stdout.splitlines()})


@app.route("/<int:service_id>/restart", methods=["POST"])
def restart(service_id: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {secret.TOKEN}":
        return "Unauthorized", 401

    output = subprocess.run(["systemctl", "list-units", "--type", "service"], stdout=subprocess.PIPE, text=True)

    result = []

    for service in output.stdout.splitlines():
        if match := re.match(LIST_REGEX, service):
            result.append(match.groupdict())

    service = result[service_id]

    output = subprocess.run(["sudo", "systemctl", "restart", service["filename"]], stdout=subprocess.PIPE, text=True)

    return jsonify({"result": output.stdout.splitlines()})


if __name__ == '__main__':
    app.run()
