"""Course spec: API asoslari: Postman va OpenAPI — 6 lessons, UZ + RU.

Everything below was run against a live Notes API (Flask): the OpenAPI file passes `redocly lint`
and openapi-spec-validator, the Postman collection runs under newman (14 requests, 23 assertions,
exit codes 0/1 checked), openapi2postmanv2 converts the spec, and contract_test.py checks 12 real
responses against the spec (and catches two kinds of drift). The Postman desktop UI itself cannot be
run from a script, so lessons describe it in general terms and rely on the collection/environment
files (which Postman imports) for everything that was verified. API messages are English so the
code is identical in UZ and RU.
"""
from __future__ import annotations

import json

# ── Verified artefacts (single source of truth for lessons 1-6) ──────────────

API_APP_PY = '''import datetime as dt
import os
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-use-a-long-random-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = dt.timedelta(minutes=30)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080"]}}, allow_headers=["Content-Type", "Authorization"])

users = {}   # username -> {"id", "password_hash", "role"}
notes = []   # {"id", "text", "owner_id"}


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if len(username) < 3 or len(password) < 6:
        return jsonify(error="username needs 3+ and password 6+ characters"), 400
    if username in users:
        return jsonify(error="username is taken"), 409
    role = "admin" if username == os.environ.get("ADMIN_USERNAME") else "user"
    users[username] = {"id": len(users) + 1, "password_hash": generate_password_hash(password), "role": role}
    return jsonify(message="registered"), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    user = users.get(username)
    if user is None or not check_password_hash(user["password_hash"], data.get("password") or ""):
        return jsonify(error="invalid username or password"), 401
    token = create_access_token(identity=str(user["id"]), additional_claims={"role": user["role"]})
    return jsonify(token=token, username=username)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt().get("role") != "admin":
            return jsonify(error="admin only"), 403
        return fn(*args, **kwargs)
    return wrapper


@app.get("/api/notes")
@jwt_required()
def list_notes():
    if get_jwt().get("role") == "admin":
        return jsonify(notes)
    owner_id = int(get_jwt_identity())
    return jsonify([n for n in notes if n["owner_id"] == owner_id])


@app.post("/api/notes")
@jwt_required()
def create_note():
    text = ((request.get_json(silent=True) or {}).get("text") or "").strip()
    if not text:
        return jsonify(error="text is required"), 400
    note = {"id": len(notes) + 1, "text": text, "owner_id": int(get_jwt_identity())}
    notes.append(note)
    return jsonify(note), 201


@app.delete("/api/notes/<int:note_id>")
@jwt_required()
def delete_note(note_id):
    note = next((n for n in notes if n["id"] == note_id), None)
    if note is None:
        return jsonify(error="note not found"), 404
    if note["owner_id"] != int(get_jwt_identity()) and get_jwt().get("role") != "admin":
        return jsonify(error="not your note"), 403
    notes.remove(note)
    return jsonify(message="deleted")


@app.get("/api/admin/users")
@admin_required
def list_users():
    return jsonify([{"id": u["id"], "username": name, "role": u["role"]} for name, u in users.items()])


@jwt.unauthorized_loader
def missing_token(reason):
    return jsonify(error="authorization token is required", code="token_missing"), 401


@jwt.invalid_token_loader
def invalid_token(reason):
    return jsonify(error="token is invalid", code="token_invalid"), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify(error="token has expired", code="token_expired"), 401


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", "5000")))
'''

OPENAPI_YAML = '''openapi: 3.0.3
info:
  title: Notes API
  version: 1.0.0
  description: Register, log in and keep personal notes. Every notes route needs a Bearer token.
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
servers:
  - url: http://127.0.0.1:5000
    description: Local development
security:
  - bearerAuth: []
tags:
  - name: auth
    description: Registration and login
  - name: notes
    description: The caller's notes
  - name: admin
    description: Administrator tools
paths:
  /api/register:
    post:
      tags: [auth]
      operationId: register
      summary: Create an account
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Credentials'
      responses:
        '201':
          description: Account created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Message'
        '400':
          description: Username shorter than 3 or password shorter than 6 characters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Username is already taken
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
  /api/login:
    post:
      tags: [auth]
      operationId: login
      summary: Log in and get a token
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Credentials'
      responses:
        '200':
          description: Token for the Authorization header
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResult'
        '401':
          description: Wrong username or password
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
  /api/notes:
    get:
      tags: [notes]
      operationId: listNotes
      summary: List my notes (an admin sees everyone's)
      responses:
        '200':
          description: The notes
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Note'
        '401':
          $ref: '#/components/responses/Unauthorized'
    post:
      tags: [notes]
      operationId: createNote
      summary: Create a note
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NoteInput'
      responses:
        '201':
          description: The created note
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Note'
        '400':
          description: The text is missing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          $ref: '#/components/responses/Unauthorized'
  /api/notes/{noteId}:
    delete:
      tags: [notes]
      operationId: deleteNote
      summary: Delete a note
      parameters:
        - name: noteId
          in: path
          required: true
          description: Id of the note
          schema:
            type: integer
            minimum: 1
      responses:
        '200':
          description: Deleted
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Message'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          description: The note belongs to someone else
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: No such note
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
  /api/admin/users:
    get:
      tags: [admin]
      operationId: listUsers
      summary: List all users (admin only)
      responses:
        '200':
          description: The users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          description: Not an administrator
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  responses:
    Unauthorized:
      description: Token missing, invalid or expired
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TokenError'
  schemas:
    Credentials:
      type: object
      required: [username, password]
      properties:
        username:
          type: string
          minLength: 3
          example: ali
        password:
          type: string
          minLength: 6
          example: secret12
    LoginResult:
      type: object
      required: [token, username]
      properties:
        token:
          type: string
        username:
          type: string
    NoteInput:
      type: object
      required: [text]
      properties:
        text:
          type: string
          example: buy bread
    Note:
      type: object
      required: [id, text, owner_id]
      properties:
        id:
          type: integer
        text:
          type: string
        owner_id:
          type: integer
    User:
      type: object
      required: [id, username, role]
      properties:
        id:
          type: integer
        username:
          type: string
        role:
          type: string
          enum: [user, admin]
    Message:
      type: object
      required: [message]
      properties:
        message:
          type: string
    Error:
      type: object
      required: [error]
      properties:
        error:
          type: string
    TokenError:
      type: object
      required: [error, code]
      properties:
        error:
          type: string
        code:
          type: string
          enum: [token_missing, token_invalid, token_expired]
'''

CONTRACT_TEST_PY = '''"""Contract test: every real response must be documented in openapi.yaml and match its schema.

    python contract_test.py http://127.0.0.1:5000 openapi.yaml
"""
import json
import sys
import urllib.error
import urllib.request
import uuid

import jsonschema
import yaml

BASE = sys.argv[1].rstrip("/")
SPEC = yaml.safe_load(open(sys.argv[2] if len(sys.argv) > 2 else "openapi.yaml"))
checks = 0


def resolve(node):
    """Replace every {"$ref": "#/components/..."} by the object it points to."""
    if isinstance(node, dict):
        if "$ref" in node:
            target = SPEC
            for part in node["$ref"].removeprefix("#/").split("/"):
                target = target[part]
            return resolve(target)
        return {key: resolve(value) for key, value in node.items()}
    if isinstance(node, list):
        return [resolve(item) for item in node]
    return node


def call(method, path, body=None, token=None):
    request = urllib.request.Request(BASE + path, method=method)
    if body is not None:
        request.add_header("Content-Type", "application/json")
        request.data = json.dumps(body).encode()
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        response = err
    return response.status, json.loads(response.read() or "null")


def check(method, template, path, body=None, token=None, expect=None):
    """Call the API and compare the answer with the spec for `template` (the path as written in openapi.yaml)."""
    global checks
    status, data = call(method, path, body, token)
    documented = resolve(SPEC["paths"][template][method.lower()]["responses"])
    assert str(status) in documented, f"{method} {template}: status {status} is not documented (documented: {sorted(documented)})"
    if expect is not None:
        assert status == expect, f"{method} {template}: expected {expect}, got {status}"
    schema = documented[str(status)]["content"]["application/json"]["schema"]
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as err:
        raise AssertionError(f"{method} {template} -> {status}: {err.message}") from None
    checks += 1
    print(f"ok  {method:6} {template:22} -> {status}")
    return data


name = "contract_" + uuid.uuid4().hex[:8]
creds = {"username": name, "password": "secret12"}
check("POST", "/api/register", "/api/register", creds, expect=201)
check("POST", "/api/register", "/api/register", creds, expect=409)
check("POST", "/api/register", "/api/register", {"username": "a", "password": "1"}, expect=400)
token = check("POST", "/api/login", "/api/login", creds, expect=200)["token"]
check("POST", "/api/login", "/api/login", {**creds, "password": "wrong-password"}, expect=401)
check("GET", "/api/notes", "/api/notes", expect=401)
note = check("POST", "/api/notes", "/api/notes", {"text": "buy bread"}, token, expect=201)
check("GET", "/api/notes", "/api/notes", token=token, expect=200)
check("POST", "/api/notes", "/api/notes", {"text": ""}, token, expect=400)
check("GET", "/api/admin/users", "/api/admin/users", token=token, expect=403)
check("DELETE", "/api/notes/{noteId}", f"/api/notes/{note['id']}", token=token, expect=200)
check("DELETE", "/api/notes/{noteId}", f"/api/notes/{note['id']}", token=token, expect=404)
print(f"{checks} contract checks passed")
'''

WORKFLOW_YML = '''name: api-checks

on:
  push:
    branches: [main]
  pull_request:

jobs:
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install the API and the checkers
        run: pip install flask flask-jwt-extended flask-cors pyyaml jsonschema
      - name: Lint openapi.yaml
        run: npx --yes @redocly/cli lint openapi.yaml
      - name: Start the API
        run: |
          ADMIN_USERNAME=boss python app.py &
          for i in $(seq 1 30); do curl -s -o /dev/null http://127.0.0.1:5000/api/notes && break; sleep 1; done
      - name: Run the Postman collection
        run: npx --yes newman run collection.json -e environment.json -r cli,junit --reporter-junit-export newman-results.xml
      - name: Contract test
        run: python contract_test.py http://127.0.0.1:5000 openapi.yaml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: newman-results
          path: newman-results.xml
'''

# Postman collection and environment, generated from this small builder so JSON stays consistent.
SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
def _lines(text):
    return [line for line in text.strip("\n").split("\n")]


def request(name, method, path, *, body=None, auth="bearer", token_var="token", tests="", pre=""):
    item = {"name": name, "request": {"method": method, "header": [], "url": {
        "raw": "{{base_url}}" + path, "host": ["{{base_url}}"], "path": [p for p in path.split("/") if p]}}}
    req = item["request"]
    if body is not None:
        req["header"].append({"key": "Content-Type", "value": "application/json"})
        req["body"] = {"mode": "raw", "raw": body, "options": {"raw": {"language": "json"}}}
    if auth == "none":
        req["auth"] = {"type": "noauth"}
    elif auth == "bearer" and token_var != "token":
        req["auth"] = {"type": "bearer", "bearer": [{"key": "token", "value": "{{" + token_var + "}}", "type": "string"}]}
    events = []
    if pre:
        events.append({"listen": "prerequest", "script": {"type": "text/javascript", "exec": _lines(pre)}})
    if tests:
        events.append({"listen": "test", "script": {"type": "text/javascript", "exec": _lines(tests)}})
    if events:
        item["event"] = events
    return item


NOTE_SCHEMA = '{ type: "object", required: ["id", "text", "owner_id"], properties: { id: { type: "integer" }, text: { type: "string" }, owner_id: { type: "integer" } } }'

COLLECTION = {
    "info": {"name": "Notes API", "description": "Requests and tests for the Notes API (see openapi.yaml)", "schema": SCHEMA},
    "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}]},
    "item": [
        {"name": "Auth", "item": [
            request("Register", "POST", "/api/register", auth="none",
                    body='{\n  "username": "{{username}}",\n  "password": "{{password}}"\n}',
                    pre='pm.environment.set("username", "user_" + Date.now());',
                    tests='''
pm.test("status is 201", function () {
  pm.response.to.have.status(201);
});
pm.test("answers with JSON", function () {
  pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
  pm.expect(pm.response.json().message).to.eql("registered");
});'''),
            request("Register: password too short", "POST", "/api/register", auth="none",
                    body='{\n  "username": "{{username}}_x",\n  "password": "123"\n}',
                    tests='''
pm.test("status is 400", function () {
  pm.response.to.have.status(400);
});
pm.test("explains the problem", function () {
  pm.expect(pm.response.json().error).to.be.a("string").and.not.empty;
});'''),
            request("Login", "POST", "/api/login", auth="none",
                    body='{\n  "username": "{{username}}",\n  "password": "{{password}}"\n}',
                    tests='''
pm.test("status is 200", function () {
  pm.response.to.have.status(200);
});
const body = pm.response.json();
pm.test("returns a token and the username", function () {
  pm.expect(body.token).to.be.a("string").and.not.empty;
  pm.expect(body.username).to.eql(pm.environment.get("username"));
});
pm.test("responds quickly", function () {
  pm.expect(pm.response.responseTime).to.be.below(1000);
});
pm.environment.set("token", body.token);'''),
            request("Login: wrong password", "POST", "/api/login", auth="none",
                    body='{\n  "username": "{{username}}",\n  "password": "wrong-password"\n}',
                    tests='''
pm.test("status is 401 and no token", function () {
  pm.response.to.have.status(401);
  pm.expect(pm.response.json()).to.not.have.property("token");
});'''),
        ]},
        {"name": "Notes", "item": [
            request("List notes without a token", "GET", "/api/notes", auth="none",
                    tests='''
pm.test("status is 401", function () {
  pm.response.to.have.status(401);
});
pm.test("code says the token is missing", function () {
  pm.expect(pm.response.json().code).to.eql("token_missing");
});'''),
            request("Create note", "POST", "/api/notes", body='{\n  "text": "buy bread"\n}',
                    tests='''
pm.test("status is 201", function () {
  pm.response.to.have.status(201);
});
const note = pm.response.json();
pm.test("note has the text we sent", function () {
  pm.expect(note.text).to.eql("buy bread");
  pm.expect(note.id).to.be.a("number");
});
pm.environment.set("note_id", note.id);'''),
            request("List notes", "GET", "/api/notes",
                    tests='''
pm.test("status is 200", function () {
  pm.response.to.have.status(200);
});
const schema = {
  type: "array",
  items: { type: "object", required: ["id", "text", "owner_id"], properties: {
    id: { type: "integer" }, text: { type: "string" }, owner_id: { type: "integer" } } }
};
pm.test("matches the Note schema", function () {
  pm.response.to.have.jsonSchema(schema);
});
pm.test("contains the note we created", function () {
  const ids = pm.response.json().map((n) => n.id);
  pm.expect(ids).to.include(Number(pm.environment.get("note_id")));
});'''),
            request("Create note: empty text", "POST", "/api/notes", body='{\n  "text": ""\n}',
                    tests='''
pm.test("status is 400", function () {
  pm.response.to.have.status(400);
});'''),
            request("Delete note", "DELETE", "/api/notes/{{note_id}}",
                    tests='''
pm.test("status is 200", function () {
  pm.response.to.have.status(200);
  pm.expect(pm.response.json().message).to.eql("deleted");
});'''),
            request("Delete note again", "DELETE", "/api/notes/{{note_id}}",
                    tests='''
pm.test("status is 404", function () {
  pm.response.to.have.status(404);
});'''),
        ]},
        {"name": "Admin", "item": [
            request("Users as a regular user", "GET", "/api/admin/users",
                    tests='''
pm.test("status is 403", function () {
  pm.response.to.have.status(403);
});'''),
            request("Register the admin", "POST", "/api/register", auth="none",
                    body='{\n  "username": "boss",\n  "password": "{{password}}"\n}',
                    tests='''
pm.test("created, or already there from an earlier run", function () {
  pm.expect(pm.response.code).to.be.oneOf([201, 409]);
});'''),
            request("Login as the admin", "POST", "/api/login", auth="none",
                    body='{\n  "username": "boss",\n  "password": "{{password}}"\n}',
                    tests='''
pm.test("status is 200", function () {
  pm.response.to.have.status(200);
});
pm.environment.set("admin_token", pm.response.json().token);'''),
            request("Users as the admin", "GET", "/api/admin/users", token_var="admin_token",
                    tests='''
pm.test("status is 200", function () {
  pm.response.to.have.status(200);
});
pm.test("every user has a role", function () {
  const users = pm.response.json();
  pm.expect(users).to.be.an("array").that.is.not.empty;
  users.forEach((u) => pm.expect(u.role).to.be.oneOf(["user", "admin"]));
});'''),
        ]},
    ],
}

ENVIRONMENT = {
    "id": "notes-api-local", "name": "Notes API (local)", "_postman_variable_scope": "environment",
    "values": [
        {"key": "base_url", "value": "http://127.0.0.1:5000", "type": "default", "enabled": True},
        {"key": "username", "value": "", "type": "default", "enabled": True},
        {"key": "password", "value": "secret12", "type": "secret", "enabled": True},
        {"key": "token", "value": "", "type": "secret", "enabled": True},
        {"key": "admin_token", "value": "", "type": "secret", "enabled": True},
        {"key": "note_id", "value": "", "type": "default", "enabled": True},
    ],
}

COLLECTION_JSON = json.dumps(COLLECTION, indent=2) + "\n"
ENVIRONMENT_JSON = json.dumps(ENVIRONMENT, indent=2) + "\n"

COURSE = {
    "title": "API asoslari: Postman va OpenAPI",
    "title_ru": "Основы API: Postman и OpenAPI",
    "description": (
        "API bilan professional ishlashni o'rganasiz: HTTP so'rov va javobni o'qish, Postman'da kolleksiya, muhit va avtomatik "
        "testlar, newman bilan buyruq qatorida va CI'da ishga tushirish, OpenAPI hujjati, hujjat va API mosligini tekshirish. "
        "Kurs oxirida o'z API'ngiz uchun hujjat, test kolleksiyasi va GitHub Actions tekshiruvini yozasiz."
    ),
    "description_ru": (
        "Вы научитесь профессионально работать с API: читать HTTP-запрос и ответ, делать коллекции, окружения и автоматические "
        "тесты в Postman, запускать их через newman в командной строке и в CI, описывать API в OpenAPI и проверять, что "
        "описание совпадает с реальным API. В конце курса вы напишете описание, коллекцию тестов и проверку GitHub Actions "
        "для собственного API."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 8,
    "prerequisite_course_id": 21,
    "display_order": 311,
    "is_active": True,
    "is_published": False,
}


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


def _item(*path_names: str) -> dict:
    """A request of the collection by its folder/name, e.g. _item("Auth", "Login")."""
    node = {"item": COLLECTION["item"]}
    for name in path_names:
        node = next(entry for entry in node["item"] if entry["name"] == name)
    return node


_LOGIN_ITEM = json.dumps(_item("Auth", "Login"), indent=2) + "\n"
_CREATE_NOTE_TESTS = "\n".join(_item("Notes", "Create note")["event"][0]["script"]["exec"]) + "\n"
_LIST_NOTES_TESTS = "\n".join(_item("Notes", "List notes")["event"][0]["script"]["exec"]) + "\n"
_REGISTER_PRE = "\n".join(_item("Auth", "Register")["event"][0]["script"]["exec"]) + "\n"
_COLLECTION_HEAD = json.dumps({k: COLLECTION[k] for k in ("info", "auth")}, indent=2) + "\n"

CMD_INSTALL_API = '''pip install flask flask-jwt-extended flask-cors
python app.py
'''

CMD_INSTALL_API_PORT = '''PORT=5055 ADMIN_USERNAME=boss python app.py
'''

CMD_CURL = '''curl -i http://127.0.0.1:5000/api/notes
curl -i -X POST http://127.0.0.1:5000/api/register -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
curl -X POST http://127.0.0.1:5000/api/login -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
curl -i -X POST http://127.0.0.1:5000/api/notes -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"text": "buy bread"}'
'''

OUT_401 = '''HTTP/1.1 401 UNAUTHORIZED
Content-Type: application/json

{"code":"token_missing","error":"authorization token is required"}
'''

OUT_201 = '''HTTP/1.1 201 CREATED
Content-Type: application/json

{"id":1,"owner_id":1,"text":"buy bread"}
'''

CMD_NEWMAN = '''npm install --save-dev newman
npx newman run collection.json -e environment.json
'''

CMD_NEWMAN_OPTIONS = '''npx newman run collection.json -e environment.json --env-var base_url=http://127.0.0.1:5055
npx newman run collection.json -e environment.json --bail
npx newman run collection.json -e environment.json -r cli,junit --reporter-junit-export newman-results.xml
'''

OUT_NEWMAN_SUMMARY = '''requests          14 executed    0 failed
test-scripts      14 executed    0 failed
assertions        23 executed    0 failed
'''

CMD_LINT = '''npx @redocly/cli lint openapi.yaml
'''

OUT_LINT_OK = '''validating openapi.yaml...
openapi.yaml: validated in 14ms

Woohoo! Your API description is valid.
'''

OUT_LINT_ERRORS = '''[1] broken.yaml:2:1 at #/info
The field `version` must be present on this level.
Error was generated by the struct rule.

[2] broken.yaml:68:9 at #/paths/~1api~1login/post/responses/200
The field `description` must be present on this level.
Error was generated by the struct rule.

[3] broken.yaml:95:11 at #/paths/~1api~1notes/get/responses/401
Can't resolve $ref
Error was generated by the no-unresolved-refs rule.
'''

OUT_LINT_WARN = '''warn.yaml:2:1 at #/info
Info object should contain `license` field.
Warning was generated by the info-license rule.

Woohoo! Your API description is valid.
You have 1 warning.
'''

PY_VALIDATE = '''import yaml
from openapi_spec_validator import validate

validate(yaml.safe_load(open("openapi.yaml")))
print("openapi-spec-validator: OK")
'''

CMD_CONVERT = '''npx openapi-to-postmanv2 -s openapi.yaml -o generated.json -p -O folderStrategy=Tags
'''

OUT_CONVERT = '''auth
  POST   {{baseUrl}}/api/register   (Create an account)
  POST   {{baseUrl}}/api/login      (Log in and get a token)
notes
  GET    {{baseUrl}}/api/notes      (List my notes)
  POST   {{baseUrl}}/api/notes      (Create a note)
  DELETE {{baseUrl}}/api/notes/:noteId   (Delete a note)
admin
  GET    {{baseUrl}}/api/admin/users   (List all users)
'''

CMD_CONTRACT = '''pip install pyyaml jsonschema
python contract_test.py http://127.0.0.1:5000 openapi.yaml
'''

OUT_CONTRACT_OK = '''ok  POST   /api/register          -> 201
ok  POST   /api/register          -> 409
ok  POST   /api/login             -> 200
ok  GET    /api/notes             -> 401
ok  DELETE /api/notes/{noteId}    -> 404
12 contract checks passed
'''

OUT_CONTRACT_DRIFT = '''AssertionError: POST /api/notes -> 201: 'created_at' is a required property
AssertionError: DELETE /api/notes/{noteId}: status 404 is not documented (documented: ['200', '401', '403'])
'''

CMD_FASTAPI_SPEC = '''uvicorn main:app --reload
curl http://127.0.0.1:8000/openapi.json
'''

OUT_FASTAPI_LINT = '''error    no-empty-servers        Servers must be present.
error    security-defined        Every operation should have security defined on it or on the root level.
warning  info-license            Info object should contain `license` field.
warning  operation-4xx-response  Operation must have at least one `4XX` response.
'''

CMD_PIPELINE = '''npx @redocly/cli lint openapi.yaml
ADMIN_USERNAME=boss python app.py &
for i in 1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30; do curl -s -o /dev/null http://127.0.0.1:5000/api/notes && break; sleep 1; done
npx newman run collection.json -e environment.json
python contract_test.py http://127.0.0.1:5000 openapi.yaml
'''


# ── 1-dars: HTTP va REST ─────────────────────────────────────────────────────

_L1_TEXT_UZ = """<h3>API bilan gaplashish</h3>
<p>Frontend, mobil ilova va boshqa servislar serverga <strong>HTTP</strong> orqali murojaat qiladi. Har murojaat — <strong>so'rov</strong> (request), serverning qaytishi — <strong>javob</strong> (response). API bilan ishlash uchun avvalo shu ikkalasini ichidan o'qishni bilish kerak.</p>
<pre class="mermaid">
sequenceDiagram
  participant C as Mijoz (Postman, brauzer, curl)
  participant S as Server (API)
  C->>S: So'rov: metod + URL + sarlavhalar + tana
  S->>S: Marshrutni topadi, tekshiradi, bajaradi
  S-->>C: Javob: status kodi + sarlavhalar + tana
</pre>

<h3>So'rov tarkibi</h3>
<ul>
  <li><strong>Metod</strong> — nima qilish kerak: <code>GET</code> (o'qish), <code>POST</code> (yaratish), <code>PUT</code> yoki <code>PATCH</code> (yangilash), <code>DELETE</code> (o'chirish).</li>
  <li><strong>URL</strong> — qayerga: <code>http://127.0.0.1:5000/api/notes/3</code>. Yo'l (<code>/api/notes/3</code>) resursni ko'rsatadi.</li>
  <li><strong>Sarlavhalar</strong> (headers) — qo'shimcha ma'lumot: <code>Content-Type: application/json</code> (tana JSON), <code>Authorization: Bearer &lt;token&gt;</code> (kimligingiz).</li>
  <li><strong>Tana</strong> (body) — yuboriladigan ma'lumot, odatda JSON: <code>{"text": "buy bread"}</code>. <code>GET</code> va <code>DELETE</code> da odatda tana bo'lmaydi.</li>
</ul>

<h3>Javob tarkibi</h3>
<ul>
  <li><strong>Status kodi</strong>: <code>2xx</code> — muvaffaqiyat (<code>200</code> OK, <code>201</code> yaratildi), <code>4xx</code> — <em>mijoz</em> xatosi (<code>400</code> noto'g'ri so'rov, <code>401</code> kimligingiz noma'lum, <code>403</code> ruxsat yo'q, <code>404</code> topilmadi, <code>405</code> metod mumkin emas), <code>5xx</code> — <em>server</em> xatosi (<code>500</code>).</li>
  <li><strong>Sarlavhalar</strong>: eng muhimi <code>Content-Type</code>.</li>
  <li><strong>Tana</strong>: JSON, masalan xato tavsifi.</li>
</ul>
<p><strong>401 va 403 farqi:</strong> 401 — server kimligingizni bilmaydi (token yo'q yoki yaroqsiz), 403 — kimligingiz ma'lum, lekin bu amalga ruxsatingiz yo'q.</p>

<h3>REST qoidalari</h3>
<ul>
  <li>URL <em>ot</em> (resurs) bo'ladi, fe'l emas: <code>/api/notes</code>, <code>/api/notes/3</code>; «<code>/api/createNote</code>» emas. Amalni metod bildiradi.</li>
  <li>Bir xil URL'da turli metodlar turli amal: <code>GET /api/notes</code> ro'yxat, <code>POST /api/notes</code> yaratish, <code>DELETE /api/notes/3</code> o'chirish.</li>
  <li><code>GET</code> ma'lumotni o'zgartirmasligi kerak. <code>PUT</code> va <code>DELETE</code> <em>idempotent</em>: ikki marta chaqirsangiz, natijadagi holat bir xil. <code>POST</code> esa har chaqirilganda yangi resurs yaratishi mumkin.</li>
</ul>

<h3>Mashq uchun server</h3>
<p>Butun kurs davomida bitta <strong>Notes API</strong> bilan ishlaymiz: ro'yxatdan o'tish, login (token), yozuvlar va admin. Uni ishga tushirish:</p>
<pre><code>__INSTALL__</code></pre>
<pre><code>__APP__</code></pre>
<p>Agar 5000-port band bo'lsa (macOS'da AirPlay Receiver ba'zan uni egallaydi), boshqa port bering: <code>PORT=5055 python app.py</code>. Quyidagi misollarda <code>http://127.0.0.1:5000</code> yozilgan, o'z portingizga almashtiring.</p>

<h3>curl bilan o'qish</h3>
<pre><code>__CURL__</code></pre>
<p><code>-i</code> javob sarlavhalarini ham ko'rsatadi. Tokensiz birinchi so'rov quyidagini qaytaradi:</p>
<pre><code>__OUT401__</code></pre>
<p>Ro'yxatdan o'tib, login qilib, tokenni <code>&lt;token&gt;</code> o'rniga qo'ysangiz, yozuv yaratadigan so'rov:</p>
<pre><code>__OUT201__</code></pre>
<p>Qaytgan <code>owner_id</code> yozuv egasini ko'rsatadi. Yana: mavjud bo'lmagan yo'l (<code>/nope</code>) <code>404</code>, ro'yxatdan o'tish yo'liga <code>DELETE</code> yuborish <code>405</code>, oddiy foydalanuvchining <code>/api/admin/users</code> ga so'rovi <code>403</code> qaytaradi. Postman bularning hammasini qulayroq qiladi, keyingi darsda unga o'tamiz.</p>"""

_L1_TEXT_RU = """<h3>Разговор с API</h3>
<p>Фронтенд, мобильное приложение и другие сервисы обращаются к серверу по <strong>HTTP</strong>. Каждое обращение — это <strong>запрос</strong> (request), а ответ сервера — <strong>ответ</strong> (response). Чтобы работать с API, нужно уметь читать их изнутри.</p>
<pre class="mermaid">
sequenceDiagram
  participant C as Клиент (Postman, браузер, curl)
  participant S as Сервер (API)
  C->>S: Запрос: метод + URL + заголовки + тело
  S->>S: Находит маршрут, проверяет, выполняет
  S-->>C: Ответ: код статуса + заголовки + тело
</pre>

<h3>Из чего состоит запрос</h3>
<ul>
  <li><strong>Метод</strong> — что сделать: <code>GET</code> (прочитать), <code>POST</code> (создать), <code>PUT</code> или <code>PATCH</code> (обновить), <code>DELETE</code> (удалить).</li>
  <li><strong>URL</strong> — куда: <code>http://127.0.0.1:5000/api/notes/3</code>. Путь (<code>/api/notes/3</code>) указывает на ресурс.</li>
  <li><strong>Заголовки</strong> (headers) — дополнительные данные: <code>Content-Type: application/json</code> (тело в формате JSON), <code>Authorization: Bearer &lt;token&gt;</code> (кто вы).</li>
  <li><strong>Тело</strong> (body) — отправляемые данные, обычно JSON: <code>{"text": "buy bread"}</code>. У <code>GET</code> и <code>DELETE</code> тела обычно нет.</li>
</ul>

<h3>Из чего состоит ответ</h3>
<ul>
  <li><strong>Код статуса</strong>: <code>2xx</code> — успех (<code>200</code> OK, <code>201</code> создано), <code>4xx</code> — ошибка <em>клиента</em> (<code>400</code> неверный запрос, <code>401</code> вы неизвестны, <code>403</code> нет прав, <code>404</code> не найдено, <code>405</code> метод недопустим), <code>5xx</code> — ошибка <em>сервера</em> (<code>500</code>).</li>
  <li><strong>Заголовки</strong>: важнее всего <code>Content-Type</code>.</li>
  <li><strong>Тело</strong>: JSON, например описание ошибки.</li>
</ul>
<p><strong>Разница между 401 и 403:</strong> 401 — сервер не знает, кто вы (токена нет или он недействителен), 403 — вы известны, но на это действие у вас нет прав.</p>

<h3>Правила REST</h3>
<ul>
  <li>URL — это <em>существительное</em> (ресурс), а не глагол: <code>/api/notes</code>, <code>/api/notes/3</code>, а не «<code>/api/createNote</code>». Действие задаёт метод.</li>
  <li>Один и тот же URL с разными методами — разные действия: <code>GET /api/notes</code> — список, <code>POST /api/notes</code> — создание, <code>DELETE /api/notes/3</code> — удаление.</li>
  <li><code>GET</code> не должен менять данные. <code>PUT</code> и <code>DELETE</code> <em>идемпотентны</em>: если вызвать дважды, итоговое состояние то же. А <code>POST</code> при каждом вызове может создавать новый ресурс.</li>
</ul>

<h3>Сервер для практики</h3>
<p>Весь курс мы работаем с одним <strong>Notes API</strong>: регистрация, вход (токен), записи и админ. Запуск:</p>
<pre><code>__INSTALL__</code></pre>
<pre><code>__APP__</code></pre>
<p>Если порт 5000 занят (в macOS его иногда занимает AirPlay Receiver), задайте другой: <code>PORT=5055 python app.py</code>. В примерах ниже указан <code>http://127.0.0.1:5000</code>, замените его на свой порт.</p>

<h3>Читаем через curl</h3>
<pre><code>__CURL__</code></pre>
<p>Флаг <code>-i</code> показывает и заголовки ответа. Первый запрос без токена возвращает:</p>
<pre><code>__OUT401__</code></pre>
<p>Если зарегистрироваться, войти и подставить токен вместо <code>&lt;token&gt;</code>, запрос создания записи вернёт:</p>
<pre><code>__OUT201__</code></pre>
<p>Поле <code>owner_id</code> показывает владельца записи. Также: несуществующий путь (<code>/nope</code>) даёт <code>404</code>, <code>DELETE</code> на путь регистрации — <code>405</code>, запрос обычного пользователя к <code>/api/admin/users</code> — <code>403</code>. В Postman всё это удобнее, к нему мы перейдём в следующем уроке.</p>"""

_L1_BLOCKS = dict(INSTALL=CMD_INSTALL_API, APP=API_APP_PY, CURL=CMD_CURL, OUT401=OUT_401, OUT201=OUT_201)

LESSON_1 = {
    "order": 0,
    "title": "1-HTTP va REST: so'rov va javobni o'qish",
    "title_ru": "1-HTTP и REST: читаем запрос и ответ",
    "points_reward": 10,
    "text_content": _fill(_L1_TEXT_UZ, **_L1_BLOCKS),
    "text_content_ru": _fill(_L1_TEXT_RU, **_L1_BLOCKS),
    "code_content": CMD_CURL,
    "code_content_ru": CMD_CURL,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: mashq uchun Notes API va curl so'rovlari",
        "title_ru": "Пример: учебный Notes API и запросы curl",
        "description": "Postman va OpenAPI darslari uchun Flask Notes API (register, login, notes, admin) va uni curl bilan o'qish.",
        "description_ru": "Flask Notes API (register, login, notes, admin) для уроков по Postman и OpenAPI и чтение его через curl.",
        "sample_type": "code",
        "code_files": [
            {"filename": "app.py", "language": "python", "code": API_APP_PY},
            {"filename": "commands.sh", "language": "bash", "code": CMD_INSTALL_API + "\n" + CMD_CURL},
        ],
    },
    "exercises": [
        {
            "title": "Yaratish metodi", "title_ru": "Метод создания",
            "description": "Yangi resurs yaratish uchun odatda qaysi HTTP metodi ishlatiladi?",
            "description_ru": "Какой HTTP-метод обычно используют для создания нового ресурса?",
            "exercise_type": "multiple_choice",
            "options": ["GET", "POST", "DELETE", "OPTIONS"],
            "options_ru": ["GET", "POST", "DELETE", "OPTIONS"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "GET faqat o'qiydi, DELETE o'chiradi.",
            "hint_ru": "GET только читает, DELETE удаляет.",
            "explanation": "POST yangi resurs yaratadi (masalan, POST /api/notes). GET o'qish, DELETE o'chirish uchun.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Topilmadi kodi", "title_ru": "Код «не найдено»",
            "description": "Mavjud bo'lmagan resurs so'ralganda server qaytaradigan status kodi: ___",
            "description_ru": "Код статуса, который сервер возвращает, если запрошенного ресурса нет: ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "404",
            "hint": "Eng mashhur xato kodi.",
            "hint_ru": "Самый известный код ошибки.",
            "explanation": "404 Not Found resurs topilmaganini bildiradi. 405 esa metod bu yo'lda mumkin emasligini ko'rsatadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "So'rov yo'li", "title_ru": "Путь запроса",
            "description": "So'rov va javob bosqichlarini tartibga soling.",
            "description_ru": "Расположите этапы запроса и ответа по порядку.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Mijoz metod, URL, sarlavha va tanani yig'adi", "So'rov serverga yuboriladi", "Server marshrutni topib, so'rovni bajaradi", "Server status kodi, sarlavha va tana bilan javob qaytaradi"],
            "drag_items_ru": ["Клиент собирает метод, URL, заголовки и тело", "Запрос отправляется на сервер", "Сервер находит маршрут и выполняет запрос", "Сервер возвращает ответ с кодом статуса, заголовками и телом"],
            "correct_order": ["Mijoz metod, URL, sarlavha va tanani yig'adi", "So'rov serverga yuboriladi", "Server marshrutni topib, so'rovni bajaradi", "Server status kodi, sarlavha va tana bilan javob qaytaradi"],
            "hint": "Avval mijoz yuboradi, keyin server javob beradi.",
            "hint_ru": "Сначала отправляет клиент, потом отвечает сервер.",
            "explanation": "HTTP har doim so'rov-javob juftligi: mijoz so'rovni tayyorlab yuboradi, server uni bajarib status kodi bilan qaytaradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Status kodlari", "title_ru": "Коды статуса",
            "description": "Status kodlari haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о кодах статуса верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "201 resurs yaratilganini bildiradi",
                "401 — token yo'q yoki yaroqsiz",
                "403 — kimligingiz ma'lum, lekin ruxsat yo'q",
                "500 — mijoz noto'g'ri so'rov yuborgan",
            ],
            "options_ru": [
                "201 означает, что ресурс создан",
                "401 — токена нет или он недействителен",
                "403 — вы известны, но прав нет",
                "500 — клиент отправил неверный запрос",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "5xx — server xatosi, mijozniki emas.",
            "hint_ru": "5xx — ошибка сервера, а не клиента.",
            "explanation": "201, 401 va 403 to'g'ri. 500 server xatosi: mijoz xatolari 4xx guruhida.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "401 va 403", "title_ru": "401 и 403",
            "description": "401 va 403 status kodlarining farqini o'z so'zingiz bilan yozing.",
            "description_ru": "Объясните своими словами разницу между кодами статуса 401 и 403.",
            "exercise_type": "text_input",
            "expected_answer": "401 Unauthorized: server kimligingizni bilmaydi, token yo'q yoki yaroqsiz. 403 Forbidden: kimligingiz ma'lum, lekin bu amalga ruxsatingiz yo'q, masalan oddiy foydalanuvchi admin yo'liga kirdi.",
            "hint": "Qaysi birida server sizni taniydi?",
            "hint_ru": "В каком из случаев сервер вас знает?",
            "explanation": "401 — autentifikatsiya muammosi (kim ekaningiz noma'lum), 403 — avtorizatsiya muammosi (kim ekaningiz ma'lum, ruxsat yo'q).",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 2-dars: Postman ──────────────────────────────────────────────────────────

_L2_TEXT_UZ = """<h3>Postman nima</h3>
<p><strong>Postman</strong> — API'ga so'rov yuborib, javobni qulay ko'rish dasturi. <code>curl</code> bilan har safar uzun buyruq yozish o'rniga so'rovni bir marta tuzib saqlaysiz, keyin bosh bilan qayta yuborasiz. Asosiy tushunchalar: <strong>so'rov</strong> (request), <strong>kolleksiya</strong> (so'rovlar to'plami, papkalarga bo'linadi), <strong>muhit</strong> (environment, o'zgaruvchilar to'plami) va <strong>o'zgaruvchi</strong>. Eslatma: Postman interfeysi vaqt o'tishi bilan o'zgaradi, shuning uchun bu darsda dugmalar nomidan ko'ra tushunchalar va fayl formatiga e'tibor beramiz.</p>

<h3>So'rov oynasi</h3>
<p>So'rov oynasida metod va URL tanlanadi, so'ng sozlamalar yorliqlari: <em>Params</em> (so'rov parametrlari), <em>Authorization</em> (token), <em>Headers</em>, <em>Body</em> (JSON uchun <em>raw</em> → <em>JSON</em> tanlanadi, <code>Content-Type: application/json</code> sarlavhasi o'zi qo'shiladi). Pastda javob: status, vaqt, hajm va tana (<em>Pretty</em> ko'rinishida chiroyli JSON).</p>

<h3>Muhit va o'zgaruvchilar</h3>
<p>Server manzilini har so'rovga qo'lda yozmang: <code>{{base_url}}</code> o'zgaruvchisini ishlating. Qo'sh jingalak qavs ichidagi nom Postman tomonidan qiymat bilan almashtiriladi. Manzil o'zgarsa (lokal → test server), faqat bitta joyda tuzatasiz.</p>
<ul>
  <li><strong>Muhit</strong> (environment): <code>base_url</code>, <code>username</code>, <code>token</code> kabi qiymatlar. «Lokal» va «Test server» uchun alohida muhit yaratib, ro'yxatdan tanlaysiz.</li>
  <li><strong>O'zgaruvchi doiralari</strong> (scope): global, kolleksiya, muhit, ma'lumotlar (data) va lokal. Bir nom bir nechta doirada bo'lsa, <em>torroq doira</em> ustun keladi (lokal muhitdan, muhit kolleksiyadan, kolleksiya globaldan).</li>
  <li>Token kabi maxfiy qiymatlarni muhitda <em>secret</em> turi bilan saqlang va kolleksiyani boshqalarga yuborishdan oldin haqiqiy tokenlarni olib tashlang.</li>
</ul>

<h3>Kolleksiya fayli</h3>
<p>Kolleksiya JSON fayl (v2.1) sifatida eksport va import qilinadi: jamoadoshingiz <em>Import</em> orqali uni ochadi, <code>newman</code> (3-dars) esa buyruq qatorida ishga tushiradi. Bizning kolleksiyada uchta papka (<code>Auth</code>, <code>Notes</code>, <code>Admin</code>) va 14 ta so'rov bor. Faylning boshi: kolleksiya nomi va <em>butun kolleksiyaga</em> tegishli Bearer token. Uni <code>{{token}}</code> muhit o'zgaruvchisidan oladi:</p>
<pre><code>__HEAD__</code></pre>
<p>Bitta so'rov (login) shunday ko'rinadi: metod, URL (<code>{{base_url}}</code>), tana va <code>noauth</code> (login uchun token kerak emas, shuning uchun kolleksiya tokenini bekor qilamiz):</p>
<pre><code>__LOGIN__</code></pre>
<p>Hozircha <code>event</code> (testlar) qismiga e'tibor bermang: u 3-darsda. Muhit fayli oddiy: o'zgaruvchilar ro'yxati. Parol va tokenlar <code>secret</code> turida:</p>
<pre><code>__ENV__</code></pre>

<h3>O'zingiz sinab ko'ring</h3>
<ol>
  <li>1-darsdagi serverni ishga tushiring.</li>
  <li>Postman'da <em>Import</em> orqali <code>collection.json</code> va <code>environment.json</code> ni oching, muhitni tanlang. Server boshqa portda bo'lsa, muhitdagi <code>base_url</code> ni o'zgartiring.</li>
  <li><code>Auth</code> papkasidagi <em>Register</em>, keyin <em>Login</em> so'rovini yuboring.</li>
  <li>Kolleksiya papkalarini birma-bir yuborib, har javobning status va tanasini o'qing.</li>
</ol>
<p>Tokenni qo'lda nusxalamaysiz: 3-darsda <em>Login</em> javobidan uni avtomatik saqlaymiz va keyingi so'rovlar <code>{{token}}</code> orqali o'zi oladi.</p>"""

_L2_TEXT_RU = """<h3>Что такое Postman</h3>
<p><strong>Postman</strong> — программа, чтобы отправлять запросы к API и удобно смотреть ответ. Вместо того чтобы каждый раз писать длинную команду <code>curl</code>, вы один раз составляете запрос, сохраняете его и отправляете повторно одним нажатием. Основные понятия: <strong>запрос</strong> (request), <strong>коллекция</strong> (набор запросов, делится на папки), <strong>окружение</strong> (environment, набор переменных) и <strong>переменная</strong>. Примечание: интерфейс Postman со временем меняется, поэтому в этом уроке мы смотрим не на названия кнопок, а на понятия и формат файла.</p>

<h3>Окно запроса</h3>
<p>В окне запроса выбираются метод и URL, затем вкладки настроек: <em>Params</em> (параметры запроса), <em>Authorization</em> (токен), <em>Headers</em>, <em>Body</em> (для JSON выбирается <em>raw</em> → <em>JSON</em>, заголовок <code>Content-Type: application/json</code> добавляется сам). Внизу ответ: статус, время, размер и тело (вид <em>Pretty</em> показывает красивый JSON).</p>

<h3>Окружение и переменные</h3>
<p>Не пишите адрес сервера в каждом запросе вручную: используйте переменную <code>{{base_url}}</code>. Имя внутри двойных фигурных скобок Postman заменяет значением. Если адрес меняется (локальный → тестовый сервер), вы правите только одно место.</p>
<ul>
  <li><strong>Окружение</strong> (environment): значения вроде <code>base_url</code>, <code>username</code>, <code>token</code>. Можно создать отдельные окружения «Локальный» и «Тестовый сервер» и выбирать из списка.</li>
  <li><strong>Области переменных</strong> (scope): глобальная, коллекции, окружения, данных (data) и локальная. Если одно имя есть в нескольких областях, побеждает <em>более узкая</em> (локальная сильнее окружения, окружение сильнее коллекции, коллекция сильнее глобальной).</li>
  <li>Секретные значения вроде токена храните в окружении с типом <em>secret</em> и убирайте настоящие токены, прежде чем отправлять коллекцию другим.</li>
</ul>

<h3>Файл коллекции</h3>
<p>Коллекция экспортируется и импортируется как JSON-файл (v2.1): коллега открывает её через <em>Import</em>, а <code>newman</code> (урок 3) запускает в командной строке. В нашей коллекции три папки (<code>Auth</code>, <code>Notes</code>, <code>Admin</code>) и 14 запросов. Начало файла: имя коллекции и Bearer-токен, относящийся ко <em>всей коллекции</em>. Он берётся из переменной окружения <code>{{token}}</code>:</p>
<pre><code>__HEAD__</code></pre>
<p>Один запрос (вход) выглядит так: метод, URL (<code>{{base_url}}</code>), тело и <code>noauth</code> (для входа токен не нужен, поэтому мы отменяем токен коллекции):</p>
<pre><code>__LOGIN__</code></pre>
<p>Часть <code>event</code> (тесты) пока пропустите: она в уроке 3. Файл окружения простой: список переменных. Пароль и токены имеют тип <code>secret</code>:</p>
<pre><code>__ENV__</code></pre>

<h3>Попробуйте сами</h3>
<ol>
  <li>Запустите сервер из урока 1.</li>
  <li>Через <em>Import</em> откройте в Postman <code>collection.json</code> и <code>environment.json</code> и выберите окружение. Если сервер на другом порту, измените <code>base_url</code> в окружении.</li>
  <li>Отправьте в папке <code>Auth</code> запрос <em>Register</em>, затем <em>Login</em>.</li>
  <li>Отправляйте запросы папок по очереди и читайте статус и тело каждого ответа.</li>
</ol>
<p>Токен вручную копировать не нужно: в уроке 3 мы автоматически сохраним его из ответа <em>Login</em>, и следующие запросы сами возьмут его через <code>{{token}}</code>.</p>"""

_L2_BLOCKS = dict(HEAD=_COLLECTION_HEAD, LOGIN=_LOGIN_ITEM, ENV=ENVIRONMENT_JSON)

LESSON_2 = {
    "order": 1,
    "title": "2-Postman: kolleksiya, muhit va o'zgaruvchilar",
    "title_ru": "2-Postman: коллекция, окружение и переменные",
    "points_reward": 10,
    "text_content": _fill(_L2_TEXT_UZ, **_L2_BLOCKS),
    "text_content_ru": _fill(_L2_TEXT_RU, **_L2_BLOCKS),
    "code_content": ENVIRONMENT_JSON,
    "code_content_ru": ENVIRONMENT_JSON,
    "code_language": "json",
    "sample": {
        "title": "Namuna: Postman kolleksiyasi va muhit fayli",
        "title_ru": "Пример: коллекция Postman и файл окружения",
        "description": "Notes API uchun 14 so'rovli kolleksiya (Auth, Notes, Admin) va {{base_url}}, {{token}} o'zgaruvchilari bilan muhit.",
        "description_ru": "Коллекция из 14 запросов для Notes API (Auth, Notes, Admin) и окружение с переменными {{base_url}}, {{token}}.",
        "sample_type": "code",
        "code_files": [
            {"filename": "collection.json", "language": "json", "code": COLLECTION_JSON},
            {"filename": "environment.json", "language": "json", "code": ENVIRONMENT_JSON},
        ],
    },
    "exercises": [
        {
            "title": "O'zgaruvchi yozuvi", "title_ru": "Запись переменной",
            "description": "Postman'da o'zgaruvchi qo'sh jingalak qavs bilan yoziladi: ___base_url}}",
            "description_ru": "В Postman переменная записывается в двойных фигурных скобках: ___base_url}}",
            "exercise_type": "fill_in_blank",
            "correct_answers": "{{",
            "hint": "Ochuvchi jingalak qavslar, ikkita.",
            "hint_ru": "Две открывающие фигурные скобки.",
            "explanation": "{{base_url}} — Postman qiymatni so'rov yuborilganda almashtiradigan o'zgaruvchi yozuvi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Nega muhit", "title_ru": "Зачем окружение",
            "description": "Server manzilini har so'rovga yozish o'rniga {{base_url}} ishlatishning asosiy foydasi nima?",
            "description_ru": "В чём главная польза использования {{base_url}} вместо адреса сервера в каждом запросе?",
            "exercise_type": "multiple_choice",
            "options": [
                "Manzil o'zgarsa, faqat bitta joyda tuzatiladi",
                "So'rovlar tezroq bajariladi",
                "Server o'zi tezlashadi",
                "Token avtomatik yaratiladi",
            ],
            "options_ru": [
                "Если адрес меняется, правится только одно место",
                "Запросы выполняются быстрее",
                "Сервер сам ускоряется",
                "Токен создаётся автоматически",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Gap tezlik haqida emas, qulaylik haqida.",
            "hint_ru": "Речь не о скорости, а об удобстве.",
            "explanation": "O'zgaruvchi manzilni bir joyda saqlaydi: lokaldan test serverga o'tishda faqat muhit almashtiriladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Boshlash tartibi", "title_ru": "Порядок начала работы",
            "description": "Tayyor kolleksiya bilan ishlashni boshlash tartibini joylashtiring.",
            "description_ru": "Расположите порядок начала работы с готовой коллекцией.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Serverni ishga tushirish", "collection.json va environment.json ni import qilish", "Muhitni tanlash", "Register, keyin Login so'rovini yuborish"],
            "drag_items_ru": ["Запустить сервер", "Импортировать collection.json и environment.json", "Выбрать окружение", "Отправить Register, затем Login"],
            "correct_order": ["Serverni ishga tushirish", "collection.json va environment.json ni import qilish", "Muhitni tanlash", "Register, keyin Login so'rovini yuborish"],
            "hint": "So'rov yuborishdan oldin server va tanlangan muhit tayyor bo'lishi kerak.",
            "hint_ru": "Перед отправкой запросов сервер и выбранное окружение должны быть готовы.",
            "explanation": "Avval server ishlab turishi kerak, keyin fayllar import qilinadi va muhit tanlanadi; shundan so'ng so'rovlar to'g'ri manzilga ketadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Yaxshi amaliyot", "title_ru": "Хорошая практика",
            "description": "Postman bilan ishlashda qaysi qoidalar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие правила работы с Postman верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "base_url ni muhit o'zgaruvchisi qilib saqlash",
                "Token kabi qiymatlarni muhitda secret turida saqlash",
                "Kolleksiyani yuborishdan oldin haqiqiy tokenlarni olib tashlash",
                "Haqiqiy tokenni har bir so'rovga qo'lda yozib chiqish",
            ],
            "options_ru": [
                "Хранить base_url как переменную окружения",
                "Хранить токены и подобные значения в окружении с типом secret",
                "Убирать настоящие токены перед отправкой коллекции",
                "Вписывать настоящий токен вручную в каждый запрос",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Maxfiy qiymat qo'lda ko'p joyga yozilmaydi.",
            "hint_ru": "Секретное значение не вписывают вручную во множество мест.",
            "explanation": "O'zgaruvchi, secret turi va tozalangan kolleksiya xavfsiz va qulay. Tokenni har so'rovga qo'lda yozish xato va sizib chiqish xavfini oshiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Doiralar ustunligi", "title_ru": "Приоритет областей",
            "description": "Agar bir xil nomli o'zgaruvchi ham kolleksiyada, ham muhitda bo'lsa, qaysi biri ishlatiladi va nima uchun? O'z so'zingiz bilan yozing.",
            "description_ru": "Если переменная с одним именем есть и в коллекции, и в окружении, какая будет использована и почему? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Muhitdagi qiymat ishlatiladi: torroq doira kengroq doiradan ustun turadi (lokal muhitdan, muhit kolleksiyadan, kolleksiya globaldan). Shuning uchun muhit orqali kolleksiyadagi standart qiymatni bekor qilish mumkin.",
            "hint": "Qaysi doira torroq: muhitmi yoki kolleksiyami?",
            "hint_ru": "Какая область уже: окружение или коллекция?",
            "explanation": "Postman torroq doirani afzal ko'radi, shuning uchun muhit o'zgaruvchisi kolleksiya o'zgaruvchisini bekor qiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3-dars: testlar va newman ────────────────────────────────────────────────

_L3_TEXT_UZ = """<h3>Nega testlar</h3>
<p>Javobni ko'zga qarab tekshirish bir marta yaxshi, lekin yuzta so'rov va har kodni o'zgartirishdan keyin yaramaydi. Postman'da har so'rovga <strong>test skripti</strong> yoziladi: JavaScript kodi javob kelgach avtomatik bajariladi va nimalar to'g'ri ekanini tekshiradi. Skriptlar so'rovning <em>Tests</em> yorlig'ida (kolleksiya faylida <code>event</code> → <code>"listen": "test"</code>) yoziladi, <em>Pre-request Script</em> esa so'rov <em>yuborilishidan oldin</em> ishlaydi.</p>

<h3>pm.test va pm.expect</h3>
<pre><code>__CREATE__</code></pre>
<ul>
  <li><code>pm.test("nomi", function () { ... })</code> — bitta tekshiruv. Ichida xato bo'lsa, shu test «yiqildi» deb belgilanadi, qolganlari davom etadi.</li>
  <li><code>pm.response.to.have.status(201)</code> — status kodi; <code>pm.response.json()</code> — tanani JS obyektiga aylantiradi; <code>pm.response.headers.get("Content-Type")</code> — sarlavha; <code>pm.response.responseTime</code> — javob vaqti (ms).</li>
  <li><code>pm.expect(qiymat).to...</code> — Chai kutubxonasi: <code>.to.eql</code> (teng), <code>.to.be.a("string")</code>, <code>.to.include</code>, <code>.to.be.oneOf([...])</code>, <code>.to.be.below(1000)</code>.</li>
  <li><code>pm.environment.set("note_id", note.id)</code> qiymatni muhitga yozadi: keyingi so'rov uni <code>{{note_id}}</code> sifatida ishlatadi.</li>
</ul>

<h3>So'rovlarni zanjirga ulash</h3>
<p>Login javobidan token olib, muhitga saqlaymiz (<code>pm.environment.set("token", body.token)</code>), keyin himoyalangan so'rovlar kolleksiya darajasidagi <code>{{token}}</code> orqali uni o'zi ishlatadi. Pre-request skripti esa har yurishda yangi foydalanuvchi nomini yasaydi: shunda qayta yurgizganda «nom band» (409) xatosi chiqmaydi:</p>
<pre><code>__PRE__</code></pre>
<pre class="mermaid">
flowchart LR
  A["Register (yangi username)"] --> B["Login: token muhitga"]
  B --> C["Create note: note_id muhitga"]
  C --> D["List notes: ro'yxatda note_id bor"]
  D --> E["Delete note → 200"]
  E --> F["Delete note again → 404"]
</pre>

<h3>Sxema bilan tekshirish</h3>
<p>Maydonlarni birma-bir tekshirish o'rniga butun javobni JSON sxemaga solishtirish mumkin: <code>pm.response.to.have.jsonSchema(schema)</code>. Sxema OpenAPI'dagi <code>components/schemas</code> bilan bir xil g'oya (4-dars).</p>
<pre><code>__LIST__</code></pre>

<h3>Salbiy testlar</h3>
<p>Faqat «hammasi yaxshi» holatni tekshirish yetarli emas. Kolleksiyada xato holatlari ham bor: tokensiz so'rov <code>401</code> (<code>code: token_missing</code>), noto'g'ri parol <code>401</code>, qisqa parol <code>400</code>, bo'sh matn <code>400</code>, begona yo'l <code>403</code>, ikkinchi marta o'chirish <code>404</code>. Aynan shu yerlarda xatolar yashiriladi.</p>

<h3>newman: kolleksiyani buyruq qatorida yurgizish</h3>
<p><strong>newman</strong> — Postman kolleksiyasini Postman dasturisiz ishga tushiradigan buyruq qatori vositasi. Serverni ishga tushiring (admin hisob <code>boss</code> bo'lishi uchun <code>ADMIN_USERNAME=boss python app.py</code>), so'ng:</p>
<pre><code>__NEWMAN__</code></pre>
<p>Natijada har so'rov va test ro'yxati, oxirida xulosa chiqadi. Bizning kolleksiyada:</p>
<pre><code>__SUMMARY__</code></pre>
<pre><code>__OPTIONS__</code></pre>
<ul>
  <li><code>--env-var base_url=...</code> muhitdagi qiymatni bekor qiladi (boshqa port yoki test server uchun).</li>
  <li><code>--bail</code> birinchi xatoda to'xtatadi.</li>
  <li><code>-r cli,junit</code> konsolga va JUnit XML faylga hisobot beradi: CI tizimlari uni o'qiydi.</li>
  <li><strong>Chiqish kodi</strong>: hamma tekshiruv o'tsa <code>0</code>, birortasi yiqilsa yoki server ishlamasa <code>1</code>. CI aynan shu kod bo'yicha «yashil» yoki «qizil» bo'ladi.</li>
</ul>

<h3>Tez-tez uchraydigan xatolar</h3>
<ul>
  <li>Test skriptida <code>data</code> nomli o'zgaruvchi e'lon qilish: Postman'da bu nom band, «Identifier 'data' has already been declared» xatosi chiqadi. <code>body</code> yoki <code>payload</code> deng.</li>
  <li><code>pm.response.to.have.header("Content-Type", /regex/)</code> ikkinchi argument sifatida regex emas, aniq qiymat kutadi; qismini tekshirish uchun <code>pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json")</code> yozing.</li>
  <li>Tokenni saqlamagan so'rovdan keyin hammasi 401 bilan yiqiladi: zanjirning birinchi yiqilgan testidan boshlab qarang.</li>
</ul>"""

_L3_TEXT_RU = """<h3>Зачем тесты</h3>
<p>Проверять ответ глазами хорошо один раз, но не годится, когда запросов сто и код меняется постоянно. В Postman к каждому запросу пишется <strong>тестовый скрипт</strong>: код JavaScript автоматически выполняется после получения ответа и проверяет, что именно верно. Скрипты пишутся на вкладке <em>Tests</em> запроса (в файле коллекции это <code>event</code> → <code>"listen": "test"</code>), а <em>Pre-request Script</em> срабатывает <em>до отправки</em> запроса.</p>

<h3>pm.test и pm.expect</h3>
<pre><code>__CREATE__</code></pre>
<ul>
  <li><code>pm.test("название", function () { ... })</code> — одна проверка. Если внутри ошибка, этот тест помечается как упавший, остальные продолжают выполняться.</li>
  <li><code>pm.response.to.have.status(201)</code> — код статуса; <code>pm.response.json()</code> — превращает тело в объект JS; <code>pm.response.headers.get("Content-Type")</code> — заголовок; <code>pm.response.responseTime</code> — время ответа (мс).</li>
  <li><code>pm.expect(значение).to...</code> — библиотека Chai: <code>.to.eql</code> (равно), <code>.to.be.a("string")</code>, <code>.to.include</code>, <code>.to.be.oneOf([...])</code>, <code>.to.be.below(1000)</code>.</li>
  <li><code>pm.environment.set("note_id", note.id)</code> записывает значение в окружение: следующий запрос использует его как <code>{{note_id}}</code>.</li>
</ul>

<h3>Связываем запросы в цепочку</h3>
<p>Из ответа на вход берём токен и сохраняем в окружение (<code>pm.environment.set("token", body.token)</code>), после чего защищённые запросы сами используют его через <code>{{token}}</code> на уровне коллекции. А pre-request скрипт при каждом запуске придумывает новое имя пользователя: так при повторном запуске не возникает ошибки «имя занято» (409):</p>
<pre><code>__PRE__</code></pre>
<pre class="mermaid">
flowchart LR
  A["Register (новый username)"] --> B["Login: токен в окружение"]
  B --> C["Create note: note_id в окружение"]
  C --> D["List notes: в списке есть note_id"]
  D --> E["Delete note → 200"]
  E --> F["Delete note again → 404"]
</pre>

<h3>Проверка по схеме</h3>
<p>Вместо проверки полей по одному можно сравнить весь ответ с JSON-схемой: <code>pm.response.to.have.jsonSchema(schema)</code>. Схема — та же идея, что и <code>components/schemas</code> в OpenAPI (урок 4).</p>
<pre><code>__LIST__</code></pre>

<h3>Негативные тесты</h3>
<p>Проверять только «всё хорошо» недостаточно. В коллекции есть и случаи ошибок: запрос без токена даёт <code>401</code> (<code>code: token_missing</code>), неверный пароль — <code>401</code>, короткий пароль — <code>400</code>, пустой текст — <code>400</code>, обычный пользователь на админский путь — <code>403</code>, повторное удаление — <code>404</code>. Именно здесь прячутся ошибки.</p>

<h3>newman: запуск коллекции из командной строки</h3>
<p><strong>newman</strong> — инструмент командной строки, который запускает коллекцию Postman без самого Postman. Запустите сервер (чтобы появился админ <code>boss</code>, используйте <code>ADMIN_USERNAME=boss python app.py</code>) и выполните:</p>
<pre><code>__NEWMAN__</code></pre>
<p>В результате выводится список запросов и тестов, а в конце итог. В нашей коллекции:</p>
<pre><code>__SUMMARY__</code></pre>
<pre><code>__OPTIONS__</code></pre>
<ul>
  <li><code>--env-var base_url=...</code> переопределяет значение из окружения (другой порт или тестовый сервер).</li>
  <li><code>--bail</code> останавливает запуск на первой ошибке.</li>
  <li><code>-r cli,junit</code> выдаёт отчёт в консоль и в XML-файл JUnit: его читают CI-системы.</li>
  <li><strong>Код завершения</strong>: <code>0</code>, если все проверки прошли, и <code>1</code>, если хоть одна упала или сервер недоступен. По этому коду CI становится «зелёным» или «красным».</li>
</ul>

<h3>Частые ошибки</h3>
<ul>
  <li>Объявлять в тестовом скрипте переменную с именем <code>data</code>: в Postman это имя занято, будет ошибка «Identifier 'data' has already been declared». Назовите её <code>body</code> или <code>payload</code>.</li>
  <li><code>pm.response.to.have.header("Content-Type", /regex/)</code> ожидает вторым аргументом не регулярное выражение, а точное значение; чтобы проверить часть, пишите <code>pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json")</code>.</li>
  <li>Если токен не сохранён, всё дальше падает с 401: смотрите с самого первого упавшего теста цепочки.</li>
</ul>"""

_L3_BLOCKS = dict(CREATE=_CREATE_NOTE_TESTS, PRE=_REGISTER_PRE, LIST=_LIST_NOTES_TESTS, NEWMAN=CMD_NEWMAN,
                  SUMMARY=OUT_NEWMAN_SUMMARY, OPTIONS=CMD_NEWMAN_OPTIONS)

LESSON_3 = {
    "order": 2,
    "title": "3-Postman testlari va newman",
    "title_ru": "3-Тесты Postman и newman",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, **_L3_BLOCKS),
    "text_content_ru": _fill(_L3_TEXT_RU, **_L3_BLOCKS),
    "code_content": _CREATE_NOTE_TESTS,
    "code_content_ru": _CREATE_NOTE_TESTS,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: testlar bilan kolleksiya va newman buyruqlari",
        "title_ru": "Пример: коллекция с тестами и команды newman",
        "description": "14 so'rov, 23 tekshiruv: pm.test, token zanjiri, sxema testi, salbiy testlar va newman bilan yurgizish.",
        "description_ru": "14 запросов, 23 проверки: pm.test, цепочка токена, тест по схеме, негативные тесты и запуск через newman.",
        "sample_type": "code",
        "code_files": [
            {"filename": "collection.json", "language": "json", "code": COLLECTION_JSON},
            {"filename": "environment.json", "language": "json", "code": ENVIRONMENT_JSON},
            {"filename": "commands.sh", "language": "bash", "code": CMD_NEWMAN + "\n" + CMD_NEWMAN_OPTIONS},
        ],
    },
    "exercises": [
        {
            "title": "Test funksiyasi", "title_ru": "Тестовая функция",
            "description": "Postman skriptida bitta tekshiruvni nomlab e'lon qiladigan funksiya: pm.___(\"status is 200\", function () { ... })",
            "description_ru": "Функция Postman, объявляющая одну именованную проверку: pm.___(\"status is 200\", function () { ... })",
            "exercise_type": "fill_in_blank",
            "correct_answers": "test",
            "hint": "Inglizcha «test», bitta so'z.",
            "hint_ru": "Английское слово «test».",
            "explanation": "pm.test(nom, funksiya) tekshiruvni ro'yxatdan o'tkazadi: ichidagi xato shu testni yiqitadi, boshqalar davom etadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Newman chiqish kodi", "title_ru": "Код завершения newman",
            "description": "Kolleksiyadagi bitta tekshiruv yiqilsa, newman qanday chiqish kodi bilan tugaydi? ___",
            "description_ru": "С каким кодом завершения заканчивается newman, если упала хотя бы одна проверка? ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "1",
            "hint": "Nol — muvaffaqiyat, noldan farqli — xato.",
            "hint_ru": "Ноль — успех, не ноль — ошибка.",
            "explanation": "Hammasi o'tsa 0, biror tekshiruv yiqilsa yoki server ishlamasa 1: CI aynan shu kod bilan qizil bo'ladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Zanjir tartibi", "title_ru": "Порядок цепочки",
            "description": "Tokenli zanjir bosqichlarini to'g'ri tartibga soling.",
            "description_ru": "Расположите этапы цепочки с токеном в правильном порядке.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Login javobidan token pm.environment.set bilan saqlanadi", "Create note so'rovi {{token}} bilan yuboriladi", "Javobdagi id note_id sifatida saqlanadi", "Delete note so'rovi {{note_id}} dan foydalanadi"],
            "drag_items_ru": ["Токен из ответа Login сохраняется через pm.environment.set", "Запрос Create note отправляется с {{token}}", "id из ответа сохраняется как note_id", "Запрос Delete note использует {{note_id}}"],
            "correct_order": ["Login javobidan token pm.environment.set bilan saqlanadi", "Create note so'rovi {{token}} bilan yuboriladi", "Javobdagi id note_id sifatida saqlanadi", "Delete note so'rovi {{note_id}} dan foydalanadi"],
            "hint": "Qiymat avval saqlanadi, keyin ishlatiladi.",
            "hint_ru": "Значение сначала сохраняется, потом используется.",
            "explanation": "Har bosqich oldingisining natijasiga tayanadi: token login'dan, note_id yaratishdan keyin olinadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi gaplar to'g'ri", "title_ru": "Какие утверждения верны",
            "description": "Postman testlari va newman haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о тестах Postman и newman верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "pm.environment.set bilan saqlangan qiymatni keyingi so'rov {{nom}} orqali ishlatadi",
                "Test skriptida data nomli o'zgaruvchini e'lon qilish xavfsiz",
                "newman assertion yiqilsa 1 kodi bilan tugaydi",
                "--bail birinchi xatodan keyin yurishni to'xtatadi",
            ],
            "options_ru": [
                "Значение, сохранённое через pm.environment.set, следующий запрос использует как {{имя}}",
                "Объявлять в тестовом скрипте переменную data безопасно",
                "newman завершается с кодом 1, если упала проверка",
                "--bail останавливает запуск после первой ошибки",
            ],
            "correct_answers": "A,C,D", "is_multiple_select": True,
            "hint": "data nomi Postman'da band.",
            "hint_ru": "Имя data в Postman занято.",
            "explanation": "Muhit o'zgaruvchisi, 1 chiqish kodi va --bail to'g'ri ishlaydi. data nomi Postman'da band, shuning uchun «already been declared» xatosi beradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Salbiy testlar", "title_ru": "Негативные тесты",
            "description": "Nega faqat muvaffaqiyatli holatni emas, 401, 403 va 404 kabi xatolarni ham test qilish kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему нужно тестировать не только успешный случай, но и ошибки вроде 401, 403 и 404? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Xavfsizlik va xato ishlovi aynan xato holatlarida buziladi: tokensiz so'rov, begona resurs yoki mavjud bo'lmagan yozuv noto'g'ri javob (masalan, 200 yoki 500) bersa, buni faqat salbiy testlar topadi. Ular API himoyasi va foydalanuvchiga tushunarli xato qaytarishini kafolatlaydi.",
            "hint": "Himoya qayerda sinaladi: to'g'ri so'rovdami yoki noto'g'ri so'rovdami?",
            "hint_ru": "Где проверяется защита: на правильном запросе или на неправильном?",
            "explanation": "Muvaffaqiyatli holat ishlasa ham himoya va xato ishlovi buzuq bo'lishi mumkin. Salbiy testlar aynan shuni tekshiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars: OpenAPI ──────────────────────────────────────────────────────────

_L4_TEXT_UZ = """<h3>OpenAPI nima</h3>
<p><strong>OpenAPI</strong> — API'ni mashina va odam o'qiy oladigan yagona formatda tasvirlash standarti (YAML yoki JSON fayl). U serverni yaratmaydi: u API <em>nima qila olishi</em>ni yozadi: qaysi yo'llar, metodlar, parametrlar, so'rov va javob shakllari, xatolar, autentifikatsiya. Bu fayl bitta haqiqat manbasiga aylanadi.</p>
<pre class="mermaid">
flowchart TD
  F["openapi.yaml"] --> D["Hujjat sahifasi (Swagger UI, Redoc)"]
  F --> P["Postman kolleksiyasi"]
  F --> C["Mijoz kodi va SDK generatsiyasi"]
  F --> T["Shartnoma testi: API hujjatga mosmi?"]
</pre>
<p>Bu darsda 1-darsdagi Notes API'ni OpenAPI 3.0 bilan tasvirlaymiz. Fayl quyida to'liq, so'ng qismlarga bo'lib tushuntiramiz.</p>
<pre><code>__SPEC__</code></pre>

<h3>Tuzilishi</h3>
<ul>
  <li><code>openapi</code> — standart versiyasi (<code>3.0.3</code>). <code>info</code> — nom, <code>version</code>, tavsif, litsenziya. <code>servers</code> — API manzillari.</li>
  <li><code>paths</code> — yo'llar. Har yo'lda metodlar (<code>get</code>, <code>post</code>, <code>delete</code>). Har metodda: <code>operationId</code> (noyob nom, kod generatsiyasida funksiya nomi bo'ladi), <code>summary</code>, <code>tags</code>, <code>requestBody</code>, <code>parameters</code> va eng muhimi <code>responses</code> — har status kodi uchun tavsif va sxema.</li>
  <li><strong>Yo'l parametri:</strong> <code>/api/notes/{noteId}</code> va <code>parameters</code> ichida <code>in: path</code>, <code>required: true</code> va turi (<code>integer</code>).</li>
  <li><code>components</code> — qayta ishlatiladigan qismlar: <code>schemas</code> (ma'lumot shakllari), <code>responses</code> (umumiy javob, masalan <code>Unauthorized</code>), <code>securitySchemes</code> (autentifikatsiya).</li>
  <li><code>$ref: '#/components/schemas/Note'</code> — «o'sha joydagi tavsifni shu yerga qo'y». Takrorlanishni yo'qotadi: <code>Note</code> o'zgarsa, bitta joyda tuzatasiz.</li>
</ul>

<h3>Autentifikatsiya</h3>
<p><code>securitySchemes</code> ichida <code>bearerAuth</code> (<code>type: http</code>, <code>scheme: bearer</code>) e'lon qilinadi, fayl darajasidagi <code>security</code> uni <em>hamma</em> yo'lga qo'llaydi. Ochiq yo'llar (<code>/api/register</code>, <code>/api/login</code>) uchun <code>security: []</code> yozib, himoyani bekor qilamiz. Bu 2-darsdagi kolleksiya <code>noauth</code> bilan bir xil g'oya.</p>

<h3>Sxema</h3>
<p><code>schemas</code> JSON Schema'ga asoslangan: <code>type</code>, <code>required</code> (majburiy maydonlar), <code>properties</code>, <code>enum</code> (ruxsat etilgan qiymatlar), <code>minLength</code>, <code>example</code>. Misol: <code>Note</code> da <code>id</code>, <code>text</code>, <code>owner_id</code> majburiy; <code>User.role</code> faqat <code>user</code> yoki <code>admin</code>. Xato javoblari ham sxemali: <code>Error</code> (<code>error</code>) va <code>TokenError</code> (<code>error</code> hamda <code>code</code>).</p>

<h3>Tekshirish: lint</h3>
<p>Fayl to'g'riligini asbob tekshiradi, ko'z emas. <strong>Redocly</strong> lint'i ham sintaksisni, ham yaxshi uslub qoidalarini (har operatsiyada <code>operationId</code>, xato javoblari, litsenziya, xavfsizlik) tekshiradi:</p>
<pre><code>__LINT__</code></pre>
<pre><code>__LINTOK__</code></pre>
<p>Xatolar chiqsa, chiqish kodi <code>1</code> bo'ladi (CI qizil). Masalan, <code>version</code> yo'q, javobda <code>description</code> yo'q va mavjud bo'lmagan <code>$ref</code>:</p>
<pre><code>__LINTERR__</code></pre>
<p>Qoida buzilishi <em>ogohlantirish</em> bo'lsa (masalan, <code>license</code> yo'q), fayl baribir yaroqli va chiqish kodi <code>0</code>:</p>
<pre><code>__LINTWARN__</code></pre>
<p>Sintaksisni Python'da ham tekshirish mumkin (<code>pip install openapi-spec-validator pyyaml</code>):</p>
<pre><code>__PYVALIDATE__</code></pre>
<p>Hujjatni brauzerda ko'rish uchun Swagger Editor, Swagger UI yoki Redoc kabi vositalarga faylni yuklaysiz, ular chiroyli, sinab ko'riladigan sahifa chizadi.</p>"""

_L4_TEXT_RU = """<h3>Что такое OpenAPI</h3>
<p><strong>OpenAPI</strong> — стандарт, позволяющий описать API в едином формате, который читают и машина, и человек (файл YAML или JSON). Он не создаёт сервер: он записывает, что API <em>умеет</em>: какие пути, методы, параметры, формы запросов и ответов, ошибки и аутентификацию. Этот файл становится единым источником правды.</p>
<pre class="mermaid">
flowchart TD
  F["openapi.yaml"] --> D["Страница документации (Swagger UI, Redoc)"]
  F --> P["Коллекция Postman"]
  F --> C["Генерация клиентского кода и SDK"]
  F --> T["Контрактный тест: API соответствует документу?"]
</pre>
<p>В этом уроке мы опишем Notes API из урока 1 по OpenAPI 3.0. Файл ниже целиком, затем разберём его по частям.</p>
<pre><code>__SPEC__</code></pre>

<h3>Структура</h3>
<ul>
  <li><code>openapi</code> — версия стандарта (<code>3.0.3</code>). <code>info</code> — название, <code>version</code>, описание, лицензия. <code>servers</code> — адреса API.</li>
  <li><code>paths</code> — пути. В каждом пути методы (<code>get</code>, <code>post</code>, <code>delete</code>). В каждом методе: <code>operationId</code> (уникальное имя, при генерации кода становится именем функции), <code>summary</code>, <code>tags</code>, <code>requestBody</code>, <code>parameters</code> и самое важное — <code>responses</code>: описание и схема для каждого кода статуса.</li>
  <li><strong>Параметр пути:</strong> <code>/api/notes/{noteId}</code> и в <code>parameters</code> запись с <code>in: path</code>, <code>required: true</code> и типом (<code>integer</code>).</li>
  <li><code>components</code> — переиспользуемые части: <code>schemas</code> (формы данных), <code>responses</code> (общий ответ, например <code>Unauthorized</code>), <code>securitySchemes</code> (аутентификация).</li>
  <li><code>$ref: '#/components/schemas/Note'</code> — «подставь сюда описание из того места». Убирает повторение: изменится <code>Note</code> — правите одно место.</li>
</ul>

<h3>Аутентификация</h3>
<p>В <code>securitySchemes</code> объявляется <code>bearerAuth</code> (<code>type: http</code>, <code>scheme: bearer</code>), а <code>security</code> на уровне файла применяет его ко <em>всем</em> путям. Для открытых путей (<code>/api/register</code>, <code>/api/login</code>) пишем <code>security: []</code>, отменяя защиту. Это та же идея, что <code>noauth</code> в коллекции из урока 2.</p>

<h3>Схема</h3>
<p><code>schemas</code> основаны на JSON Schema: <code>type</code>, <code>required</code> (обязательные поля), <code>properties</code>, <code>enum</code> (допустимые значения), <code>minLength</code>, <code>example</code>. Пример: в <code>Note</code> обязательны <code>id</code>, <code>text</code>, <code>owner_id</code>; <code>User.role</code> — только <code>user</code> или <code>admin</code>. Ответы с ошибками тоже имеют схему: <code>Error</code> (<code>error</code>) и <code>TokenError</code> (<code>error</code> и <code>code</code>).</p>

<h3>Проверка: lint</h3>
<p>Корректность файла проверяет инструмент, а не глаз. Линтер <strong>Redocly</strong> проверяет и синтаксис, и правила хорошего стиля (<code>operationId</code> в каждой операции, ответы с ошибками, лицензия, безопасность):</p>
<pre><code>__LINT__</code></pre>
<pre><code>__LINTOK__</code></pre>
<p>При ошибках код завершения равен <code>1</code> (CI станет красным). Например, нет <code>version</code>, нет <code>description</code> в ответе и несуществующий <code>$ref</code>:</p>
<pre><code>__LINTERR__</code></pre>
<p>Если нарушено правило уровня <em>предупреждения</em> (например, нет <code>license</code>), файл всё равно корректен, а код завершения <code>0</code>:</p>
<pre><code>__LINTWARN__</code></pre>
<p>Синтаксис можно проверить и на Python (<code>pip install openapi-spec-validator pyyaml</code>):</p>
<pre><code>__PYVALIDATE__</code></pre>
<p>Чтобы посмотреть документацию в браузере, загрузите файл в Swagger Editor, Swagger UI или Redoc: они нарисуют красивую страницу, на которой можно пробовать запросы.</p>"""

_L4_BLOCKS = dict(SPEC=OPENAPI_YAML, LINT=CMD_LINT, LINTOK=OUT_LINT_OK, LINTERR=OUT_LINT_ERRORS, LINTWARN=OUT_LINT_WARN,
                  PYVALIDATE=PY_VALIDATE)

LESSON_4 = {
    "order": 3,
    "title": "4-OpenAPI: API'ni hujjatlash",
    "title_ru": "4-OpenAPI: описываем API",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, **_L4_BLOCKS),
    "text_content_ru": _fill(_L4_TEXT_RU, **_L4_BLOCKS),
    "code_content": OPENAPI_YAML,
    "code_content_ru": OPENAPI_YAML,
    "code_language": "yaml",
    "sample": {
        "title": "Namuna: Notes API uchun openapi.yaml",
        "title_ru": "Пример: openapi.yaml для Notes API",
        "description": "OpenAPI 3.0.3: yo'llar, xato javoblari, $ref sxemalar, bearerAuth va lint buyrug'i. Redocly lint va validator'dan xatosiz o'tadi.",
        "description_ru": "OpenAPI 3.0.3: пути, ответы с ошибками, схемы через $ref, bearerAuth и команда lint. Проходит Redocly lint и валидатор без ошибок.",
        "sample_type": "code",
        "code_files": [
            {"filename": "openapi.yaml", "language": "yaml", "code": OPENAPI_YAML},
            {"filename": "validate.py", "language": "python", "code": PY_VALIDATE},
            {"filename": "commands.sh", "language": "bash", "code": CMD_LINT},
        ],
    },
    "exercises": [
        {
            "title": "Yo'llar bo'limi", "title_ru": "Раздел путей",
            "description": "OpenAPI faylida yo'llar va ularning metodlari qaysi kalit ostida yoziladi?",
            "description_ru": "Под каким ключом в файле OpenAPI записываются пути и их методы?",
            "exercise_type": "multiple_choice",
            "options": ["info", "paths", "components", "servers"],
            "options_ru": ["info", "paths", "components", "servers"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Inglizcha «yo'llar».",
            "hint_ru": "По-английски «пути».",
            "explanation": "paths yo'llarni va ularning metodlarini saqlaydi. info nom va versiya, servers manzillar, components esa qayta ishlatiladigan qismlar uchun.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Havola belgisi", "title_ru": "Ключ ссылки",
            "description": "Boshqa joydagi tavsifga havola qiladigan OpenAPI kaliti: ___",
            "description_ru": "Ключ OpenAPI, ссылающийся на описание в другом месте: ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "$ref", "correct_answers_ru": "$ref",
            "hint": "Dollar belgisi va «reference» qisqartmasi.",
            "hint_ru": "Знак доллара и сокращение «reference».",
            "explanation": "$ref '#/components/schemas/Note' kabi manzilga havola qiladi: tavsif bir joyda yoziladi va hamma joyda qayta ishlatiladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Hujjat yozish tartibi", "title_ru": "Порядок написания описания",
            "description": "OpenAPI faylini yozish va tekshirish bosqichlarini joylashtiring.",
            "description_ru": "Расположите этапы написания и проверки файла OpenAPI.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["openapi, info va servers ni yozish", "paths: yo'llar, metodlar va responses", "components/schemas va securitySchemes", "redocly lint bilan tekshirish"],
            "drag_items_ru": ["Написать openapi, info и servers", "paths: пути, методы и responses", "components/schemas и securitySchemes", "Проверить через redocly lint"],
            "correct_order": ["openapi, info va servers ni yozish", "paths: yo'llar, metodlar va responses", "components/schemas va securitySchemes", "redocly lint bilan tekshirish"],
            "hint": "Tekshirish oxirida, fayl yozilgach.",
            "hint_ru": "Проверка в конце, когда файл написан.",
            "explanation": "Avval umumiy ma'lumot, keyin yo'llar, keyin ular ishlatadigan sxemalar va xavfsizlik; oxirida lint xatolarni topadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Lint natijalari", "title_ru": "Результаты lint",
            "description": "Redocly lint haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о Redocly lint верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "info ichida version yo'q bo'lsa, xato beradi va chiqish kodi 1 bo'ladi",
                "Mavjud bo'lmagan $ref uchun xato beradi",
                "license yo'qligi ogohlantirish bo'lib, chiqish kodi 0 qoladi",
                "Lint serverni ishga tushirib, haqiqiy javoblarni tekshiradi",
            ],
            "options_ru": [
                "Если в info нет version, выдаёт ошибку, и код завершения равен 1",
                "Для несуществующего $ref выдаёт ошибку",
                "Отсутствие license — предупреждение, код завершения остаётся 0",
                "Lint запускает сервер и проверяет настоящие ответы",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Lint faqat faylni o'qiydi, serverga murojaat qilmaydi.",
            "hint_ru": "Lint читает только файл и не обращается к серверу.",
            "explanation": "Lint faylning o'zini tekshiradi: struktura xatolari va yaroqsiz havolalar xato, uslub qoidalari esa ogohlantirish. U haqiqiy API bilan solishtirmaydi: buning uchun shartnoma testi kerak (5-dars).",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "OpenAPI foydasi", "title_ru": "Польза OpenAPI",
            "description": "OpenAPI hujjatining jamoa uchun foydasini o'z so'zingiz bilan yozing.",
            "description_ru": "Объясните своими словами, какая польза от OpenAPI-описания для команды.",
            "exercise_type": "text_input",
            "expected_answer": "OpenAPI API'ning yagona, mashina o'qiy oladigan tavsifi: undan hujjat sahifasi, Postman kolleksiyasi va mijoz kodi yaratiladi, frontend va backend bir-biriga kutilgan shaklni oldindan biladi va shartnoma testi bilan API hujjatga mosligini avtomatik tekshirish mumkin.",
            "hint": "Bitta fayldan nimalar yaratish mumkin?",
            "hint_ru": "Что можно получить из одного файла?",
            "explanation": "Bitta haqiqat manbasi ikki tomon (frontend va backend) kelishuvini aniq qiladi va hujjat, kolleksiya va testlarni avtomatlashtirishga imkon beradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars: konvertatsiya va shartnoma testi ─────────────────────────────────

_L5_TEXT_UZ = """<h3>Hujjat, API va test: uchlik</h3>
<p>Hujjat bor, API bor, kolleksiya bor, lekin ular bir-biriga mosligiga kim kafolat beradi? Bu darsda uch narsani bog'laymiz: hujjatdan kolleksiya yasash, framework hujjatni o'zi yaratishi (FastAPI) va hujjat bilan <em>haqiqiy API</em> mosligini tekshiruvchi <strong>shartnoma testi</strong> (contract test).</p>
<pre class="mermaid">
flowchart LR
  S["openapi.yaml"] -->|"konvertatsiya"| P["Postman kolleksiyasi"]
  S -->|"shartnoma testi"| A["Haqiqiy API"]
  P -->|"newman"| A
</pre>

<h3>Hujjatdan kolleksiyaga</h3>
<p>Postman import qilganda OpenAPI faylini kolleksiyaga o'zi aylantira oladi. Buyruq qatorida shu ishni <code>openapi-to-postmanv2</code> bajaradi (Postman o'zi ishlatadigan kutubxona):</p>
<pre><code>__CONVERT__</code></pre>
<p>Natija: <code>tags</code> bo'yicha papkalarga bo'lingan 6 ta so'rov (<code>folderStrategy=Tags</code>), server manzili <code>baseUrl</code> o'zgaruvchisi, <code>bearerAuth</code> uchun kolleksiya darajasidagi Bearer token:</p>
<pre><code>__OUTCONVERT__</code></pre>
<p>Bu <em>boshlang'ich nuqta</em>, tayyor yechim emas. Tekshiring va tuzating:</p>
<ul>
  <li>Tana maydonlari <code>&lt;string&gt;</code> kabi o'rinbosar bilan keladi: haqiqiy qiymat yozing.</li>
  <li>Testlar yo'q: <code>pm.test</code> ni o'zingiz qo'shasiz (3-dars).</li>
  <li>O'zgaruvchi nomi boshqacha (<code>baseUrl</code>, bizniki <code>base_url</code>), yo'l parametri <code>:noteId</code> ko'rinishida.</li>
  <li>Ochiq yo'llar (<code>/api/register</code>, <code>/api/login</code>) uchun token bekor qilinganini tekshiring: konvertor kolleksiya tokenini ularga ham qo'llashi mumkin, bizning qo'lda yozilgan kolleksiyada esa ular <code>noauth</code>.</li>
</ul>

<h3>FastAPI hujjatni o'zi yaratadi</h3>
<p>FastAPI ilovasi kodingizdan (yo'llar, Pydantic modellari, status kodlari) OpenAPI faylini <strong>o'zi</strong> yig'adi: JSON <code>/openapi.json</code> da, interaktiv sahifa <code>/docs</code> da (Swagger UI) va <code>/redoc</code> da turadi. Kurs "FastAPI Asoslari"dagi kichik ilova uchun:</p>
<pre><code>__FASTAPI__</code></pre>
<p>Natijada <code>openapi: 3.1.0</code>, to'rt yo'l, <code>NoteCreate</code> va <code>NoteOut</code> sxemalari, <code>201</code> va <code>422</code> javoblari bor. <code>NoteCreate</code> da <code>minLength: 3</code> va <code>maxLength: 200</code> to'g'ridan-to'g'ri Pydantic cheklovlaridan olingan. Avtomatik hujjat yaroqli, lekin Redocly'ning <em>uslub</em> qoidalariga ba'zan javob bermaydi:</p>
<pre><code>__FASTAPILINT__</code></pre>
<p>Chunki bu ilovada <code>servers</code>, <code>license</code> va 4xx javoblar yo'q, autentifikatsiya ham yo'q. Xulosa: yaroqli hujjat va <em>yaxshi</em> hujjat boshqa-boshqa narsa; ikkinchisiga qo'lda to'ldirish kerak.</p>

<h3>Shartnoma testi</h3>
<p>Hujjat vaqt o'tishi bilan API'dan ajralib ketadi: kimdir javobga maydon qo'shadi, yangi status kodi paydo bo'ladi, hujjat esa eskicha qoladi. <strong>Shartnoma testi</strong> haqiqiy API'ga so'rov yuboradi va javob (1) hujjatda <em>mavjud status kodi</em> bilan, (2) shu javob uchun yozilgan <em>sxemaga mos tana</em> bilan kelganini tekshiradi. Quyidagi skript <code>jsonschema</code> kutubxonasi bilan buni qiladi:</p>
<pre><code>__CONTRACT__</code></pre>
<pre><code>__CMDCONTRACT__</code></pre>
<p>Tayyor API'da 12 ta tekshiruv o'tadi:</p>
<pre><code>__OUTCONTRACT__</code></pre>
<p>Endi hujjat va API ajralganda nima bo'lishini ko'ring. Hujjatda <code>Note</code> uchun majburiy <code>created_at</code> maydoni bor deb yozaylik (API qaytarmaydi) va <code>DELETE</code> dan <code>404</code> javobini o'chiraylik. Skript ikkala holatni aniq xabar bilan ushlaydi:</p>
<pre><code>__OUTDRIFT__</code></pre>

<h3>newman yoki shartnoma testi?</h3>
<ul>
  <li><strong>newman kolleksiyasi</strong> — <em>xatti-harakat</em>ni tekshiradi: login qilsa token keladimi, o'chirilgan yozuv yana o'chirilsa 404 beradimi (zanjirli stsenariylar, biznes qoidalar).</li>
  <li><strong>Shartnoma testi</strong> — <em>shaklni</em> tekshiradi: har javob hujjatdagi sxemaga va status kodlariga mosmi. Hujjat «yolg'on» gapirmasligini kafolatlaydi.</li>
  <li>Ikkalasini CI'da birga yurgizish (6-dars) eng yaxshi natija beradi.</li>
</ul>"""

_L5_TEXT_RU = """<h3>Документ, API и тест: тройка</h3>
<p>Есть описание, есть API, есть коллекция, но кто гарантирует, что они совпадают? В этом уроке мы свяжем три вещи: создание коллекции из описания, автоматическое создание описания фреймворком (FastAPI) и <strong>контрактный тест</strong> (contract test), который проверяет, что описание совпадает с <em>настоящим API</em>.</p>
<pre class="mermaid">
flowchart LR
  S["openapi.yaml"] -->|"конвертация"| P["Коллекция Postman"]
  S -->|"контрактный тест"| A["Настоящий API"]
  P -->|"newman"| A
</pre>

<h3>От описания к коллекции</h3>
<p>При импорте Postman умеет сам превращать файл OpenAPI в коллекцию. В командной строке то же делает <code>openapi-to-postmanv2</code> (библиотека, которой пользуется сам Postman):</p>
<pre><code>__CONVERT__</code></pre>
<p>Результат: 6 запросов, разложенных по папкам по <code>tags</code> (<code>folderStrategy=Tags</code>), адрес сервера в переменной <code>baseUrl</code>, Bearer-токен на уровне коллекции для <code>bearerAuth</code>:</p>
<pre><code>__OUTCONVERT__</code></pre>
<p>Это <em>отправная точка</em>, а не готовое решение. Проверьте и поправьте:</p>
<ul>
  <li>Поля тела приходят с заглушками вроде <code>&lt;string&gt;</code>: впишите настоящие значения.</li>
  <li>Тестов нет: <code>pm.test</code> вы добавляете сами (урок 3).</li>
  <li>Имя переменной другое (<code>baseUrl</code>, у нас <code>base_url</code>), параметр пути выглядит как <code>:noteId</code>.</li>
  <li>Проверьте, что для открытых путей (<code>/api/register</code>, <code>/api/login</code>) токен отменён: конвертер может применить к ним токен коллекции, а в нашей написанной вручную коллекции у них <code>noauth</code>.</li>
</ul>

<h3>FastAPI создаёт описание сам</h3>
<p>Приложение FastAPI <strong>само</strong> собирает файл OpenAPI из вашего кода (пути, модели Pydantic, коды статуса): JSON лежит по адресу <code>/openapi.json</code>, интерактивная страница — на <code>/docs</code> (Swagger UI) и <code>/redoc</code>. Для небольшого приложения из курса «Основы FastAPI»:</p>
<pre><code>__FASTAPI__</code></pre>
<p>В результате: <code>openapi: 3.1.0</code>, четыре пути, схемы <code>NoteCreate</code> и <code>NoteOut</code>, ответы <code>201</code> и <code>422</code>. В <code>NoteCreate</code> значения <code>minLength: 3</code> и <code>maxLength: 200</code> взяты прямо из ограничений Pydantic. Автоматическое описание корректно, но иногда не проходит правила <em>стиля</em> Redocly:</p>
<pre><code>__FASTAPILINT__</code></pre>
<p>Потому что в этом приложении нет <code>servers</code>, <code>license</code> и ответов 4xx, а также нет аутентификации. Вывод: корректное описание и <em>хорошее</em> описание — разные вещи; второе нужно доводить вручную.</p>

<h3>Контрактный тест</h3>
<p>Со временем описание расходится с API: кто-то добавляет поле в ответ, появляется новый код статуса, а описание остаётся старым. <strong>Контрактный тест</strong> отправляет запросы к настоящему API и проверяет, что ответ пришёл (1) с <em>кодом статуса, который есть в описании</em>, и (2) с <em>телом, соответствующим схеме</em> этого ответа. Скрипт ниже делает это с помощью библиотеки <code>jsonschema</code>:</p>
<pre><code>__CONTRACT__</code></pre>
<pre><code>__CMDCONTRACT__</code></pre>
<p>На рабочем API проходят 12 проверок:</p>
<pre><code>__OUTCONTRACT__</code></pre>
<p>Теперь посмотрите, что будет, когда описание и API разошлись. Допишем в описание обязательное поле <code>created_at</code> для <code>Note</code> (API его не возвращает) и удалим из <code>DELETE</code> ответ <code>404</code>. Скрипт ловит оба случая с понятным сообщением:</p>
<pre><code>__OUTDRIFT__</code></pre>

<h3>newman или контрактный тест?</h3>
<ul>
  <li><strong>Коллекция newman</strong> проверяет <em>поведение</em>: после входа приходит ли токен, даёт ли повторное удаление 404 (цепочки сценариев, бизнес-правила).</li>
  <li><strong>Контрактный тест</strong> проверяет <em>форму</em>: соответствует ли каждый ответ схеме и кодам статуса из описания. Гарантирует, что описание не «врёт».</li>
  <li>Лучший результат даёт запуск обоих в CI (урок 6).</li>
</ul>"""

_L5_BLOCKS = dict(CONVERT=CMD_CONVERT, OUTCONVERT=OUT_CONVERT, FASTAPI=CMD_FASTAPI_SPEC, FASTAPILINT=OUT_FASTAPI_LINT,
                  CONTRACT=CONTRACT_TEST_PY, CMDCONTRACT=CMD_CONTRACT, OUTCONTRACT=OUT_CONTRACT_OK, OUTDRIFT=OUT_CONTRACT_DRIFT)

LESSON_5 = {
    "order": 4,
    "title": "5-Hujjatdan kolleksiyaga va shartnoma testi",
    "title_ru": "5-От описания к коллекции и контрактный тест",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, **_L5_BLOCKS),
    "text_content_ru": _fill(_L5_TEXT_RU, **_L5_BLOCKS),
    "code_content": CONTRACT_TEST_PY,
    "code_content_ru": CONTRACT_TEST_PY,
    "code_language": "python",
    "sample": {
        "title": "Namuna: shartnoma testi (contract_test.py)",
        "title_ru": "Пример: контрактный тест (contract_test.py)",
        "description": "openapi.yaml bo'yicha haqiqiy API javoblarini tekshiradigan skript: 12 tekshiruv, hujjatdan ajralib ketishni ushlaydi.",
        "description_ru": "Скрипт, проверяющий настоящие ответы API по openapi.yaml: 12 проверок, ловит расхождение с описанием.",
        "sample_type": "code",
        "code_files": [
            {"filename": "contract_test.py", "language": "python", "code": CONTRACT_TEST_PY},
            {"filename": "openapi.yaml", "language": "yaml", "code": OPENAPI_YAML},
            {"filename": "commands.sh", "language": "bash", "code": CMD_CONVERT + "\n" + CMD_CONTRACT},
        ],
    },
    "exercises": [
        {
            "title": "FastAPI hujjat manzili", "title_ru": "Адрес описания FastAPI",
            "description": "FastAPI ilovasi OpenAPI JSON faylini qaysi yo'lda beradi? ___",
            "description_ru": "По какому пути приложение FastAPI отдаёт JSON-файл OpenAPI? ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "/openapi.json", "correct_answers_ru": "/openapi.json",
            "hint": "Yo'l fayl nomi bilan bir xil.",
            "hint_ru": "Путь совпадает с названием файла.",
            "explanation": "FastAPI /openapi.json da mashina o'qiydigan tavsifni, /docs da Swagger UI ni, /redoc da Redoc ni beradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Shartnoma testi nimani tutadi", "title_ru": "Что ловит контрактный тест",
            "description": "Hujjatda Note uchun majburiy created_at maydoni yozilgan, lekin API uni qaytarmaydi. Qaysi vosita buni topadi?",
            "description_ru": "В описании у Note указано обязательное поле created_at, но API его не возвращает. Какой инструмент это найдёт?",
            "exercise_type": "multiple_choice",
            "options": [
                "Shartnoma testi (haqiqiy javobni sxemaga solishtiradi)",
                "redocly lint (faqat faylni o'qiydi)",
                "curl -i (faqat javobni ko'rsatadi)",
                "Hech qaysi vosita topa olmaydi",
            ],
            "options_ru": [
                "Контрактный тест (сравнивает настоящий ответ со схемой)",
                "redocly lint (читает только файл)",
                "curl -i (только показывает ответ)",
                "Ни один инструмент не найдёт",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Kim haqiqiy API bilan hujjatni solishtiradi?",
            "hint_ru": "Кто сравнивает настоящий API с документом?",
            "explanation": "Lint faqat hujjat faylini tekshiradi, curl faqat javobni ko'rsatadi. Hujjat va javob mosligini shartnoma testi tekshiradi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Shartnoma testi bosqichlari", "title_ru": "Этапы контрактного теста",
            "description": "Shartnoma testi bitta so'rovni qanday tekshirishini tartibga soling.",
            "description_ru": "Расположите порядок, в котором контрактный тест проверяет один запрос.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Haqiqiy API'ga so'rov yuboriladi", "Javob status kodi hujjatda borligi tekshiriladi", "Shu status kodining sxemasi hujjatdan olinadi ($ref ochiladi)", "Javob tanasi sxemaga mosligi tekshiriladi"],
            "drag_items_ru": ["Отправляется запрос к настоящему API", "Проверяется, что код статуса ответа есть в описании", "Из описания берётся схема этого кода статуса (раскрывается $ref)", "Проверяется, что тело ответа соответствует схеме"],
            "correct_order": ["Haqiqiy API'ga so'rov yuboriladi", "Javob status kodi hujjatda borligi tekshiriladi", "Shu status kodining sxemasi hujjatdan olinadi ($ref ochiladi)", "Javob tanasi sxemaga mosligi tekshiriladi"],
            "hint": "Avval javob olinadi, keyin hujjat bilan solishtiriladi.",
            "hint_ru": "Сначала получают ответ, потом сравнивают с документом.",
            "explanation": "Test javobni oladi, status kodi hujjatda borligini tekshiradi, shu kodning sxemasini ($ref ni ochib) topadi va tanani unga solishtiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Konvertatsiyadan keyin", "title_ru": "После конвертации",
            "description": "OpenAPI'dan avtomatik yaratilgan Postman kolleksiyasi bilan nima qilish kerak? (Bir nechta javob)",
            "description_ru": "Что нужно сделать с коллекцией Postman, автоматически созданной из OpenAPI? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Tana o'rinbosarlarini (<string>) haqiqiy qiymat bilan almashtirish",
                "pm.test testlarini o'zingiz qo'shish",
                "Ochiq yo'llarda token noto'g'ri qo'llanmaganini tekshirish",
                "Hech narsa qilmasdan tayyor deb hisoblash",
            ],
            "options_ru": [
                "Заменить заглушки тела (<string>) настоящими значениями",
                "Добавить тесты pm.test самостоятельно",
                "Проверить, что токен не применён к открытым путям",
                "Ничего не делать и считать готовой",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Konvertor faqat so'rovlarni yaratadi.",
            "hint_ru": "Конвертер создаёт только запросы.",
            "explanation": "Konvertor so'rovlar skeletini beradi: qiymatlar o'rinbosar, testlar yo'q va autentifikatsiya sozlamasini tekshirish kerak.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "newman va shartnoma", "title_ru": "newman и контракт",
            "description": "newman kolleksiyasi va shartnoma testi nimasi bilan farq qiladi va nega ikkalasi ham kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Чем отличаются коллекция newman и контрактный тест и почему нужны оба? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "newman kolleksiyasi xatti-harakatni tekshiradi (login'dan keyin token keladimi, qayta o'chirish 404 beradimi, zanjirli stsenariylar). Shartnoma testi shaklni tekshiradi: har javob hujjatdagi status kodi va sxemaga mosmi. Birinchisi API to'g'ri ishlashini, ikkinchisi hujjat yolg'on gapirmasligini kafolatlaydi.",
            "hint": "Biri xatti-harakat, biri shakl haqida.",
            "hint_ru": "Один про поведение, другой про форму.",
            "explanation": "newman biznes mantiq va stsenariylarni, shartnoma testi esa hujjat va javob shakli mosligini tekshiradi. Ikkalasi bir-birini to'ldiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: takrorlash + loyiha ──────────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nimalarni o'rgandingiz</h3>
<ul>
  <li><strong>HTTP va REST:</strong> so'rov va javob tarkibi, metodlar, status kodlari (401 va 403 farqi), curl.</li>
  <li><strong>Postman:</strong> kolleksiya, muhit, <code>{{base_url}}</code> va <code>{{token}}</code> o'zgaruvchilari, kolleksiya fayli.</li>
  <li><strong>Testlar:</strong> <code>pm.test</code>, <code>pm.expect</code>, zanjir, <code>jsonSchema</code>, salbiy testlar, <code>newman</code> va chiqish kodlari.</li>
  <li><strong>OpenAPI:</strong> <code>paths</code>, <code>components</code>, <code>$ref</code>, <code>securitySchemes</code>, <code>operationId</code>, <code>redocly lint</code>.</li>
  <li><strong>Moslik:</strong> hujjatdan kolleksiya, FastAPI avtomatik hujjati, shartnoma testi.</li>
</ul>

<h3>Hammasini CI'da birga yurgizish</h3>
<p>Uchala tekshiruv (lint, kolleksiya, shartnoma testi) bitta zanjirga yig'iladi: API ishga tushadi va kod yoki hujjat o'zgarganda har push'da hammasi qayta tekshiriladi. Mahalliy bajariladigan buyruqlar:</p>
<pre><code>__PIPELINE__</code></pre>
<p><code>.github/workflows/api-checks.yml</code> faylida shu zanjir GitHub Actions bo'ladi. Serverni <code>&amp;</code> bilan orqa fonda ishga tushiramiz va qadamdan oldin tayyor bo'lguncha kutamiz (<code>curl</code> har qanday HTTP javobini, hatto 401 ni ham «server ishlayapti» deb hisoblaydi). <code>newman</code> JUnit hisobotini, <code>if: always()</code> qadami esa uni xato bo'lganda ham artefakt sifatida saqlaydi:</p>
<pre><code>__WORKFLOW__</code></pre>

<h3>Tez-tez uchraydigan xatolar</h3>
<ul>
  <li>Kolleksiyada serverni qayta yurgizganda «nom band» (409) bilan yiqilish: pre-request skriptida yangi <code>username</code> yasang.</li>
  <li>Hujjatga yangi status kodi yoki maydon qo'shilganini unutish: shartnoma testi buni ushlaydi, shuning uchun uni CI'dan olib tashlamang.</li>
  <li>Tokenni yoki parolni kolleksiya/muhit faylida haqiqiy qiymat bilan git'ga qo'shish: faylda faqat bo'sh yoki <code>secret</code> turidagi qiymat bo'lsin.</li>
  <li>Faqat «hammasi yaxshi» so'rovlarni test qilish: 401, 403, 404 va 400 holatlarini ham yozing.</li>
</ul>

<h3>Tayyor yechim</h3>
<p>Namunada butun to'plam: server, hujjat, kolleksiya, muhit, shartnoma testi va workflow. Ishga tushirish tartibi: <code>app.py</code> ni ishga tushiring, <code>openapi.yaml</code> ni lint qiling, <code>newman</code> va <code>contract_test.py</code> ni yurgizing. Loyihaning <code>README</code> faylida bu buyruqlar yozilgan bo'lishi kerak.</p>
<p>Keyingi bosqich: vazifani o'zingiz bajarish: yuqoridagini ko'chirmasdan, <strong>o'z API'ngiz</strong> uchun hujjat, kolleksiya va tekshiruvlar yozing.</p>"""

_L6_TEXT_RU = """<h3>Что вы изучили</h3>
<ul>
  <li><strong>HTTP и REST:</strong> состав запроса и ответа, методы, коды статуса (разница 401 и 403), curl.</li>
  <li><strong>Postman:</strong> коллекция, окружение, переменные <code>{{base_url}}</code> и <code>{{token}}</code>, файл коллекции.</li>
  <li><strong>Тесты:</strong> <code>pm.test</code>, <code>pm.expect</code>, цепочка, <code>jsonSchema</code>, негативные тесты, <code>newman</code> и коды завершения.</li>
  <li><strong>OpenAPI:</strong> <code>paths</code>, <code>components</code>, <code>$ref</code>, <code>securitySchemes</code>, <code>operationId</code>, <code>redocly lint</code>.</li>
  <li><strong>Соответствие:</strong> коллекция из описания, автоматическое описание FastAPI, контрактный тест.</li>
</ul>

<h3>Запускаем всё вместе в CI</h3>
<p>Три проверки (lint, коллекция, контрактный тест) собираются в одну цепочку: запускается API, и при каждом push всё проверяется заново, когда меняются код или описание. Команды, которые можно выполнить локально:</p>
<pre><code>__PIPELINE__</code></pre>
<p>В файле <code>.github/workflows/api-checks.yml</code> эта цепочка становится GitHub Actions. Сервер запускается в фоне через <code>&amp;</code>, а перед следующим шагом мы ждём его готовности (<code>curl</code> считает любой HTTP-ответ, даже 401, признаком «сервер работает»). <code>newman</code> формирует отчёт JUnit, а шаг с <code>if: always()</code> сохраняет его как артефакт даже при ошибке:</p>
<pre><code>__WORKFLOW__</code></pre>

<h3>Частые ошибки</h3>
<ul>
  <li>Падение при повторном запуске коллекции с «имя занято» (409): создавайте новый <code>username</code> в pre-request скрипте.</li>
  <li>Забыть, что в описание добавлен новый код статуса или поле: контрактный тест это поймает, поэтому не убирайте его из CI.</li>
  <li>Закоммитить настоящий токен или пароль в файл коллекции или окружения: в файле должны быть только пустые значения или тип <code>secret</code>.</li>
  <li>Тестировать только запросы «всё хорошо»: пишите и случаи 401, 403, 404 и 400.</li>
</ul>

<h3>Готовое решение</h3>
<p>В примере весь набор: сервер, описание, коллекция, окружение, контрактный тест и workflow. Порядок запуска: запустите <code>app.py</code>, проверьте <code>openapi.yaml</code> через lint, затем выполните <code>newman</code> и <code>contract_test.py</code>. В файле <code>README</code> проекта эти команды должны быть записаны.</p>
<p>Следующий этап — выполнить задание самостоятельно: не копируя код выше, напишите описание, коллекцию и проверки для <strong>собственного API</strong>.</p>"""

_L6_BLOCKS = dict(PIPELINE=CMD_PIPELINE, WORKFLOW=WORKFLOW_YML)

LESSON_6 = {
    "order": 5,
    "title": "6-Takrorlash: o'z API'ngiz uchun hujjat, kolleksiya va CI",
    "title_ru": "6-Повторение: описание, коллекция и CI для собственного API",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, **_L6_BLOCKS),
    "text_content_ru": _fill(_L6_TEXT_RU, **_L6_BLOCKS),
    "code_content": WORKFLOW_YML,
    "code_content_ru": WORKFLOW_YML,
    "code_language": "yaml",
    "sample": {
        "title": "Namuna: hujjat, kolleksiya va CI bilan to'liq to'plam",
        "title_ru": "Пример: полный набор с описанием, коллекцией и CI",
        "description": "Notes API, openapi.yaml, Postman kolleksiyasi va muhiti, shartnoma testi va GitHub Actions workflow'i.",
        "description_ru": "Notes API, openapi.yaml, коллекция и окружение Postman, контрактный тест и workflow GitHub Actions.",
        "sample_type": "code",
        "code_files": [
            {"filename": "app.py", "language": "python", "code": API_APP_PY},
            {"filename": "openapi.yaml", "language": "yaml", "code": OPENAPI_YAML},
            {"filename": "collection.json", "language": "json", "code": COLLECTION_JSON},
            {"filename": "environment.json", "language": "json", "code": ENVIRONMENT_JSON},
            {"filename": "contract_test.py", "language": "python", "code": CONTRACT_TEST_PY},
            {"filename": ".github/workflows/api-checks.yml", "language": "yaml", "code": WORKFLOW_YML},
            {"filename": "commands.sh", "language": "bash", "code": CMD_PIPELINE},
        ],
    },
    "task": {
        "task_title": "Loyiha: o'z API'ngiz uchun OpenAPI hujjati, Postman testlari va CI",
        "task_title_ru": "Проект: описание OpenAPI, тесты Postman и CI для собственного API",
        "task_description": "O'zingizning API'ngiz (masalan, Flask, Express yoki FastAPI loyihasi) uchun OpenAPI hujjati, avtomatik testli Postman kolleksiyasi va ularni har push'da tekshiradigan GitHub Actions workflow'ini yozing.",
        "task_description_ru": "Для собственного API (например, проекта на Flask, Express или FastAPI) напишите описание OpenAPI, коллекцию Postman с автоматическими тестами и workflow GitHub Actions, который проверяет их при каждом push.",
        "task_requirements": (
            "1) openapi.yaml (OpenAPI 3.0+): barcha yo'llar, metodlar, operationId, requestBody, javoblar (muvaffaqiyat va kamida 400, 401, 404), sxemalar $ref bilan va securitySchemes (bearerAuth). "
            "2) redocly lint openapi.yaml xatosiz o'tadi. "
            "3) Postman kolleksiyasi va muhiti (collection.json, environment.json): {{base_url}} va {{token}} o'zgaruvchilari, login javobidan tokenni saqlash. "
            "4) pm.test testlari (kamida 8 ta): status kodi, JSON maydonlari, jsonSchema, kamida bitta salbiy test (401 yoki 403 yoki 404). "
            "5) npx newman run collection.json -e environment.json chiqish kodi 0 bilan tugaydi. "
            "6) contract_test.py: kamida 6 ta so'rovni hujjat sxemalariga solishtiradi. "
            "7) .github/workflows: API'ni ishga tushirib, lint, newman va shartnoma testini yurgizadi; README da buyruqlar yozilgan."
        ),
        "task_requirements_ru": (
            "1) openapi.yaml (OpenAPI 3.0+): все пути, методы, operationId, requestBody, ответы (успех и как минимум 400, 401, 404), схемы через $ref и securitySchemes (bearerAuth). "
            "2) redocly lint openapi.yaml проходит без ошибок. "
            "3) Коллекция и окружение Postman (collection.json, environment.json): переменные {{base_url}} и {{token}}, сохранение токена из ответа на вход. "
            "4) Не менее 8 pm.test: код статуса, поля JSON, jsonSchema и хотя бы один негативный тест (401, 403 или 404). "
            "5) npx newman run collection.json -e environment.json завершается с кодом 0. "
            "6) contract_test.py: сравнивает не менее 6 запросов со схемами из описания. "
            "7) .github/workflows: запускает API, затем lint, newman и контрактный тест; в README записаны команды."
        ),
        "task_technologies": "Postman, newman, OpenAPI, GitHub Actions",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "CI zanjiri tartibi", "title_ru": "Порядок цепочки CI",
            "description": "API tekshiruvlarining to'g'ri tartibi qaysi?",
            "description_ru": "Каков правильный порядок проверок API?",
            "exercise_type": "multiple_choice",
            "options": [
                "lint openapi.yaml → API'ni ishga tushirish → newman → shartnoma testi",
                "newman → API'ni ishga tushirish → lint",
                "Shartnoma testi → lint → API'ni ishga tushirish",
                "API'ni ishga tushirmasdan newman'ni yurgizish",
            ],
            "options_ru": [
                "lint openapi.yaml → запуск API → newman → контрактный тест",
                "newman → запуск API → lint",
                "Контрактный тест → lint → запуск API",
                "Запускать newman, не запуская API",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "newman va shartnoma testi ishlayotgan serverni talab qiladi.",
            "hint_ru": "newman и контрактный тест требуют работающего сервера.",
            "explanation": "Lint serverni talab qilmaydi, shuning uchun u birinchi. newman va shartnoma testi esa ishga tushgan API'ga so'rov yuboradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Lint buyrug'i", "title_ru": "Команда lint",
            "description": "OpenAPI faylini Redocly bilan tekshiradigan buyruq: npx @redocly/cli ___ openapi.yaml",
            "description_ru": "Команда проверки файла OpenAPI через Redocly: npx @redocly/cli ___ openapi.yaml",
            "exercise_type": "fill_in_blank",
            "correct_answers": "lint",
            "hint": "Kodni «tozalab» tekshiradigan vosita nomi.",
            "hint_ru": "Название проверки, которая «вычищает» ошибки.",
            "explanation": "redocly lint fayl tuzilishi va uslub qoidalarini tekshiradi; xato bo'lsa chiqish kodi 1 bo'ladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Loyihani rejalashtirish", "title_ru": "План проекта",
            "description": "O'z API'ngiz uchun hujjat, kolleksiya va tekshiruvlarni qaysi tartibda yozasiz? O'z so'zingiz bilan yozing.",
            "description_ru": "В каком порядке вы напишете описание, коллекцию и проверки для своего API? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Avval API'ning yo'llari va javoblarini yozib openapi.yaml ni tuzaman va redocly lint bilan tekshiraman. So'ng Postman kolleksiyasi va muhitini ({{base_url}}, {{token}}) yarataman, testlar (status, sxema, salbiy holatlar) yozaman va newman bilan yurgizaman. Keyin hujjatga mosligini tekshiruvchi shartnoma testini qo'shaman va hammasini GitHub Actions'da avtomatlashtiraman.",
            "hint": "Avval hujjat, keyin kolleksiya va testlar, oxirida avtomatlashtirish.",
            "hint_ru": "Сначала описание, затем коллекция и тесты, в конце автоматизация.",
            "explanation": "Hujjat haqiqat manbasi bo'lgani uchun u birinchi; kolleksiya va shartnoma testi unga tayanadi, CI esa hammasini har o'zgarishda qayta tekshiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
