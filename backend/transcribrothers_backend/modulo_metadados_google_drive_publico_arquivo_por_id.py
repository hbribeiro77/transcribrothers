import httpx


async def obter_metadados_google_drive_publico_por_id(
    *,
    file_id: str,
    api_key: str,
) -> dict:
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    params = {"fields": "name,mimeType,size", "key": api_key}
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


def extensao_sugerida_para_video_a_partir_do_mime(mime: str | None) -> str:
    if not mime:
        return "mp4"
    m = mime.lower()
    if m == "video/mp4":
        return "mp4"
    if m == "video/webm":
        return "webm"
    if m == "video/quicktime":
        return "mov"
    return "mp4"


def media_type_para_video_por_extensao(ext: str) -> str:
    e = ext.lower().lstrip(".")
    if e == "webm":
        return "video/webm"
    if e == "mov":
        return "video/quicktime"
    return "video/mp4"
