# Bulk Status Check API

FastAPI-based microservice to check HTTP status of multiple domains in bulk.
- Accepts **JSON** or **form-urlencoded** input
- Generates variants: `http://d`, `https://d`, `http://www.d`, `https://www.d`
- Picks first variant with **200 OK**
- Else falls back to `https://domain`

## Run locally
```bash
pip install -r requirements.txt
python bulk_status_api.py

JSON request
curl -X POST "http://localhost:3000/check" \
  -H "Content-Type: application/json" \
  -d '{"urls":["google.com","example.com","http://yahoo.com"]}'

Form-URL Encoded request (n8n style)
curl -X POST "http://localhost:3000/check" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "url=google.com
example.com"

Example response
{
  "results": [
    {"url": "https://google.com", "status": 200},
    {"url": "https://example.com", "status": 404},
    {"url": "https://yahoo.com", "status": 200}
  ]
}
