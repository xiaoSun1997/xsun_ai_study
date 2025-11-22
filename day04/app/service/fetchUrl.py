import httpx


class fecthUrl:
    async def fetch_one(client: httpx.AsyncClient, url: str) -> dict:
        try:
            resp = await client.get(url,timeout=10.0)

            text = resp.text[0:10]
            return {
                "url": url,
                "status_code": resp.status_code,
                "ok": resp.is_success,
                "snippet": text,
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
            }
