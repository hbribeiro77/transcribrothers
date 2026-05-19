import re
from dataclasses import dataclass

_DRIVE_FILE_ID = re.compile(
    r"(?:https?://)?(?:drive\.google\.com/(?:file/d/|open\?id=)|docs\.google\.com/.*\?id=)([a-zA-Z0-9_-]{10,})",
    re.IGNORECASE,
)
_DRIVE_FILE_D_SLASH = re.compile(r"/file/d/([a-zA-Z0-9_-]{10,})/", re.IGNORECASE)


@dataclass(frozen=True)
class ResultadoParseLinkGoogleDrive:
    file_id: str


class ErroParseLinkGoogleDrive(ValueError):
    pass


def extrair_file_id_google_drive_de_url(url: str) -> ResultadoParseLinkGoogleDrive:
    u = (url or "").strip()
    if not u:
        raise ErroParseLinkGoogleDrive("URL vazia.")
    m = _DRIVE_FILE_D_SLASH.search(u)
    if m:
        return ResultadoParseLinkGoogleDrive(file_id=m.group(1))
    m = _DRIVE_FILE_ID.search(u)
    if m:
        return ResultadoParseLinkGoogleDrive(file_id=m.group(1))
    raise ErroParseLinkGoogleDrive(
        "Não foi possível extrair o ID do arquivo. Use um link do tipo "
        "https://drive.google.com/file/d/<ID>/view"
    )


def formatar_timestamp_segundos_para_mmss(segundos: float) -> str:
    if segundos < 0:
        segundos = 0.0
    total = int(round(segundos))
    m, s = divmod(total, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"
