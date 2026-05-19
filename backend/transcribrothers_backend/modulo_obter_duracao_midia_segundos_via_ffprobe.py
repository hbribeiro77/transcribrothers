import asyncio
import json
import shutil
import subprocess
from pathlib import Path


def _executar_ffprobe_duracao_json_sync(caminho_video: str) -> subprocess.CompletedProcess[bytes]:
    """Mesma razão do ffmpeg: evitar `create_subprocess_exec` no Windows com loop incompatível."""
    return subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            caminho_video,
        ],
        capture_output=True,
        check=False,
    )


async def obter_duracao_video_segundos_via_ffprobe(caminho_video: Path) -> float:
    if shutil.which("ffprobe") is None:
        return 0.0
    proc = await asyncio.to_thread(_executar_ffprobe_duracao_json_sync, str(caminho_video))
    stdout = proc.stdout or b""
    if proc.returncode != 0:
        return 0.0
    data = json.loads(stdout.decode() or "{}")
    dur = float(data.get("format", {}).get("duration") or 0.0)
    return max(0.0, dur)
