from pathlib import Path

import httpx

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


class ErroDownloadGoogleDrive(Exception):
    pass


async def baixar_arquivo_google_drive_publico_por_id_para_caminho(
    *,
    file_id: str,
    api_key: str,
    destino: Path,
    max_bytes: int,
) -> None:
    if not api_key:
        raise ErroDownloadGoogleDrive(
            "GOOGLE_DRIVE_API_KEY não configurada. Defina no .env ou variáveis de ambiente."
        )
    destino.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    params = {"alt": "media", "key": api_key}
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
        async with client.stream("GET", url, params=params) as resp:
            if resp.status_code == 404:
                raise ErroDownloadGoogleDrive(
                    "Arquivo não encontrado (404). Verifique o link e se o arquivo está "
                    "compartilhado como 'qualquer pessoa com o link'."
                )
            if resp.status_code == 403:
                raise ErroDownloadGoogleDrive(
                    "Acesso negado (403). API key inválida, quota excedida ou o arquivo não "
                    "está público o suficiente para a API."
                )
            if resp.status_code != 200:
                body = (await resp.aread())[:2000]
                raise ErroDownloadGoogleDrive(
                    f"Falha no download ({resp.status_code}): {body.decode(errors='replace')}"
                )
            total = 0
            with destino.open("wb") as f:
                async for chunk in resp.aiter_bytes():
                    total += len(chunk)
                    if total > max_bytes:
                        destino.unlink(missing_ok=True)
                        raise ErroDownloadGoogleDrive(
                            f"Vídeo excede o limite configurado de {max_bytes} bytes."
                        )
                    f.write(chunk)


def max_bytes_da_config(cfg: ConfiguracaoAmbienteTranscribrothers) -> int:
    return int(cfg.max_video_bytes)
