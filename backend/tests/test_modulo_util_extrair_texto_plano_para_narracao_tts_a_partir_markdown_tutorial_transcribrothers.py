"""Texto plano para narração TTS a partir do Markdown do tutorial."""

from transcribrothers_backend.modulo_util_extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers import (
    extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers,
)


def test_remove_imagens_links_codigo_e_mantem_texto_util() -> None:
    md = """# Título do tutorial

Introdução com [link](https://exemplo.com) e imagem:

![captura](assets/frame_001.png)

## Passo 1

Clique em **Salvar** no menu.

```python
print("ignore")
```

Veja em [00:12](?t=12).
"""
    texto = extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(md)
    assert "Título do tutorial" in texto
    assert "Introdução com link" in texto or "Introdução com" in texto
    assert "assets/" not in texto
    assert "frame_001" not in texto
    assert "print" not in texto
    assert "https://" not in texto
    assert "Salvar" in texto
    assert "?t=" not in texto


def test_markdown_vazio_retorna_string_vazia() -> None:
    assert extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers("   ") == ""
    assert extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(None) == ""  # type: ignore[arg-type]
