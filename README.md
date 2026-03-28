# Reverse Proxy Debug Web Application (Python / Flask)

This is a minimal but highly verbose HTTP debug server designed specifically for testing and troubleshooting reverse proxy setups.

It exposes everything a proxy might modify, including headers, client IP handling, protocol details, and request body.

---

## 1. Requirements

- Python 3.x
- pip

---

## 2. Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
```

## 3. Running the application

```bash
python app.py
```

## 4. Basic requests

### Get request

```bash
curl http://localhost:8080/test?foo=bar
```

### Post request

```bash
curl -X POST http://localhost:8080/api \
  -H "Content-Type: application/json" \
  -d '{"test": "value"}'
```

### Simulate reverse proxy headers

```bash
curl http://localhost:8080 \
  -H "X-Forwarded-For: 1.2.3.4" \
  -H "X-Forwarded-Proto: https" \
  -H "X-Forwarded-Host: example.com"
```

## 5 Optional: run with gunicorn

```bash
pip install gunicorn
gunicorn -b 0.0.0.0:8080 app:app
```

## 6. Health check

`GET /health`
