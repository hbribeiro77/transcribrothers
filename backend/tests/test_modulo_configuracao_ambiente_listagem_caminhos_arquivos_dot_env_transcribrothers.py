from pathlib import Path

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    listar_caminhos_arquivos_dot_env_ordem_carregamento_para_settings_transcribrothers,
)


def test_listar_caminhos_dot_env_retorna_raiz_e_backend_com_backend_por_ultimo(
    tmp_path: Path,
) -> None:
    raiz = tmp_path / "repo"
    backend = raiz / "backend"
    pkg = backend / "transcribrothers_backend"
    pkg.mkdir(parents=True)
    (raiz / ".env").write_text("A=1\n", encoding="utf-8")
    (backend / ".env").write_text("A=2\n", encoding="utf-8")
    out = listar_caminhos_arquivos_dot_env_ordem_carregamento_para_settings_transcribrothers(pkg)
    assert out == (str((raiz / ".env").resolve()), str((backend / ".env").resolve()))


def test_listar_caminhos_dot_env_so_backend_quando_so_backend_existe(tmp_path: Path) -> None:
    raiz = tmp_path / "repo"
    backend = raiz / "backend"
    pkg = backend / "transcribrothers_backend"
    pkg.mkdir(parents=True)
    (backend / ".env").write_text("X=1\n", encoding="utf-8")
    out = listar_caminhos_arquivos_dot_env_ordem_carregamento_para_settings_transcribrothers(pkg)
    assert out == (str((backend / ".env").resolve()),)


def test_listar_caminhos_dot_env_fallback_cwd_quando_nenhum_arquivo_existe(
    tmp_path: Path,
) -> None:
    raiz = tmp_path / "repo"
    backend = raiz / "backend"
    pkg = backend / "transcribrothers_backend"
    pkg.mkdir(parents=True)
    out = listar_caminhos_arquivos_dot_env_ordem_carregamento_para_settings_transcribrothers(pkg)
    assert out == (".env",)
