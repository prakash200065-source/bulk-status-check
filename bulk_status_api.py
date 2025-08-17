from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
import httpx
from urllib.parse import urlparse
import uvicorn
import nest_asyncio

nest_asyncio.apply()
app = FastAPI()

# Helper: extract domain
def extract_domain(u: str):
    try:
        if "://" not in u:
            u = "http://" + u
        parsed = urlparse(u)
        return parsed.hostname.replace("www.", "")
    except Exception:
        return None

# Helper: check status (HEAD → fallback GET)
async def check_status(url: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
            r = await client.head(url)
            return r.status_code
    except Exception:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
                r = await client.get(url)
                return r.status_code
        except Exception:
            return "ERROR"

@app.post("/check")
async def check(request: Request, url: str = Form(None)):
    input_raw = []

    # ✅ JSON input: { "urls": ["google.com", "example.com"] }
    try:
        body = await request.json()
        if "urls" in body and isinstance(body["urls"], list):
            input_raw = body["urls"]
    except Exception:
        pass

    # ✅ Form input: url="google.com\ngithub.com" OR "google.com, github.com"
    if url and not input_raw:
        # split by newline or comma
        parts = []
        for line in url.splitlines():
            parts.extend([p.strip() for p in line.split(",") if p.strip()])
        input_raw = parts

    output = []

    for inp in input_raw:
        domain = extract_domain(inp.strip())
        if not domain:
            continue

        variants = [
            f"http://{domain}",
            f"https://{domain}",
            f"http://www.{domain}",
            f"https://www.{domain}",
        ]

        chosen, chosen_status = None, None

        for v in variants:
            status = await check_status(v)
            if status == 200:
                chosen, chosen_status = v, status
                break

        # fallback to https://domain
        if not chosen:
            chosen = f"https://{domain}"
            chosen_status = await check_status(chosen)

        output.append({"url": chosen, "status": chosen_status})

    return JSONResponse(content={"results": output})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
