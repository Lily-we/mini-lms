from urllib.parse import urlparse, parse_qs

def extract_youtube_id(url: str) -> str | None:
    """
    Supports:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - https://www.youtube.com/shorts/VIDEOID
    - https://www.youtube.com/embed/VIDEOID
    """
    if not url:
        return None

    u = url.strip()
    try:
        parsed = urlparse(u)
    except Exception:
        return None

    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").strip("/")

    # youtu.be/VIDEOID
    if "youtu.be" in host:
        vid = path.split("/")[0] if path else None
        return vid or None

    # youtube.com/watch?v=VIDEOID
    if "youtube.com" in host:
        if path == "watch":
            qs = parse_qs(parsed.query or "")
            return (qs.get("v", [None])[0]) or None

        # /shorts/VIDEOID or /embed/VIDEOID
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
            return parts[1] or None

    return None