from flask import Flask, request, jsonify
import socket
import datetime
import json
import os

app = Flask(__name__)

def get_client_ip():
    """
    Try multiple ways to determine real client IP.
    Useful when testing reverse proxies.
    """
    return {
        "remote_addr": request.remote_addr,
        "x_forwarded_for": request.headers.get("X-Forwarded-For"),
        "x_real_ip": request.headers.get("X-Real-IP"),
        "forwarded": request.headers.get("Forwarded"),
    }

def get_server_info():
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "unknown"

    return {
        "hostname": hostname,
        "server_ip": ip,
        "server_port": request.environ.get("SERVER_PORT"),
    }

def get_request_body():
    raw_data = request.get_data(as_text=True)

    parsed = None
    if request.is_json:
        try:
            parsed = request.get_json()
        except Exception as e:
            parsed = {"error": str(e)}

    elif request.form:
        parsed = request.form.to_dict(flat=False)

    return {
        "raw": raw_data,
        "parsed": parsed
    }

def get_proxy_headers():
    """
    Extract headers that matter for reverse proxy debugging.
    """
    important = [
        "Host",
        "X-Forwarded-For",
        "X-Forwarded-Proto",
        "X-Forwarded-Host",
        "X-Forwarded-Port",
        "X-Real-IP",
        "Forwarded",
        "Via",
        "CF-Connecting-IP",
        "True-Client-IP",
    ]

    return {h: request.headers.get(h) for h in important if h in request.headers}

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def catch_all(path):
    now = datetime.datetime.utcnow().isoformat() + "Z"

    response = {
        "timestamp_utc": now,

        "request": {
            "method": request.method,
            "path": request.path,
            "full_url": request.url,
            "base_url": request.base_url,
            "url_root": request.url_root,
            "scheme": request.scheme,
            "http_version": request.environ.get("SERVER_PROTOCOL"),

            "query_params": request.args.to_dict(flat=False),
            "headers": dict(request.headers),
            "cookies": request.cookies,

            "body": get_request_body(),
        },

        "client": get_client_ip(),

        "server": get_server_info(),

        "proxy_debug": {
            "proxy_headers": get_proxy_headers(),
            "wsgi_env": {
                k: str(v)
                for k, v in request.environ.items()
                if k.startswith("HTTP_") or k in [
                    "REMOTE_ADDR",
                    "REMOTE_PORT",
                    "SERVER_NAME",
                    "SERVER_PORT",
                    "REQUEST_METHOD",
                    "PATH_INFO",
                    "QUERY_STRING",
                    "wsgi.url_scheme",
                ]
            }
        }
    }

    return jsonify(response), 200


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    print(f"Starting debug server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)