"""Allowlist LiteLLM: modelos extras (runtime) entram nas opções permitidas."""

import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_modelos_litellm_extras_sqlite_transcribrothers import (
    definir_cache_modelos_litellm_extras_runtime_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    listar_modelos_litellm_permitidos_efetivos_transcribrothers,
    validar_e_resolver_modelo_litellm_solicitado_pelo_cliente,
)


def test_whitelist_aceita_modelo_extra_presente_no_cache_runtime_transcribrothers() -> None:
    definir_cache_modelos_litellm_extras_runtime_transcribrothers(["azure_ai/claude-opus-4-8"])
    try:
        cfg = ConfiguracaoAmbienteTranscribrothers(
            litellm_model="azure_ai/claude-opus-4-6",
            litellm_modelos_provisionados="azure_ai/claude-opus-4-6,azure_ai/claude-sonnet-4-6",
        )
        assert (
            validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(
                cfg, "azure_ai/claude-opus-4-8"
            )
            == "azure_ai/claude-opus-4-8"
        )
        efetivos = listar_modelos_litellm_permitidos_efetivos_transcribrothers(cfg)
        assert "azure_ai/claude-opus-4-6" in efetivos
        assert "azure_ai/claude-opus-4-8" in efetivos
    finally:
        definir_cache_modelos_litellm_extras_runtime_transcribrothers([])


def test_whitelist_ainda_rejeita_modelo_fora_do_env_e_dos_extras_transcribrothers() -> None:
    definir_cache_modelos_litellm_extras_runtime_transcribrothers(["azure_ai/claude-opus-4-8"])
    try:
        cfg = ConfiguracaoAmbienteTranscribrothers(
            litellm_model="azure_ai/claude-opus-4-6",
            litellm_modelos_provisionados="azure_ai/claude-opus-4-6",
        )
        with pytest.raises(ValueError, match="lista permitida"):
            validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(cfg, "outro/modelo-x")
    finally:
        definir_cache_modelos_litellm_extras_runtime_transcribrothers([])
