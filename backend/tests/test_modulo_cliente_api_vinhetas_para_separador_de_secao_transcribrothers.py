import httpx
import pytest

from transcribrothers_backend.modulo_cliente_api_vinhetas_para_separador_de_secao_transcribrothers import (
    baixar_mp4_renderizado_da_vinheta,
    baixar_mp4_renderizado_da_vinheta_com_debug,
    interpretar_cabecalho_debug_da_vinheta,
    listar_vinhetas_para_o_separador,
)


@pytest.mark.asyncio
async def test_lista_os_modelos_e_as_vinhetas_salvas(monkeypatch):
    class Resposta:
        status_code = 200

        def json(self):
            return [{"id": "abc", "titulo": "Abertura"}]

    class Cliente:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url):
            assert url == "http://vinhetas.test/api/vinhetas"
            return Resposta()

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Cliente())
    corpo = await listar_vinhetas_para_o_separador("http://vinhetas.test")

    assert corpo["projetos"] == [{"id": "abc", "titulo": "Abertura"}]
    assert corpo["modelos"][0]["id"] == "planos-que-abrem-espaco"


@pytest.mark.asyncio
async def test_manda_duracao_cores_e_presenca_no_render(monkeypatch):
    visto = {}

    class Resposta:
        status_code = 200
        content = b"mp4"

    class Cliente:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, json):
            visto["url"] = url
            visto["json"] = json
            return Resposta()

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Cliente())
    conteudo = await baixar_mp4_renderizado_da_vinheta(
        titulo="Consulta",
        efeito="linhas-que-desenham-o-lugar",
        duracao_segundos=4.5,
        presenca_da_imagem=60,
        cores={
            "fundo": "#0e1c2f",
            "plano_principal": "#1b4f72",
            "plano_destaque": "#c4a35a",
            "texto": "#ffffff",
        },
        url_base="http://vinhetas.test",
    )

    assert conteudo == b"mp4"
    assert visto["url"] == "http://vinhetas.test/api/vinhetas/renderizar-mp4"
    assert visto["json"]["duracao_segundos"] == 4.5
    assert visto["json"]["presenca_da_imagem"] == 60
    assert visto["json"]["cores"]["texto"] == "#ffffff"


@pytest.mark.asyncio
async def test_manda_largura_e_altura_do_video_no_render(monkeypatch):
    visto = {}

    class Resposta:
        status_code = 200
        content = b"mp4"

    class Cliente:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, json):
            visto["json"] = json
            return Resposta()

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Cliente())
    await baixar_mp4_renderizado_da_vinheta(
        titulo="Consulta",
        efeito="planos-que-abrem-espaco",
        largura=1366,
        altura=768,
        url_base="http://vinhetas.test",
    )

    assert visto["json"]["largura"] == 1366
    assert visto["json"]["altura"] == 768


@pytest.mark.asyncio
async def test_manda_o_quadro_anterior_para_a_dissolucao_sair_no_proprio_mp4(monkeypatch):
    visto = {}

    class Resposta:
        status_code = 200
        content = b"mp4"

    class Cliente:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, json):
            visto["json"] = json
            return Resposta()

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Cliente())
    await baixar_mp4_renderizado_da_vinheta(
        titulo="Consulta",
        efeito="planos-que-abrem-espaco",
        imagem_quadro_anterior_base64="QU5URVJJT1I=",
        url_base="http://vinhetas.test",
    )

    assert visto["json"]["imagem_quadro_anterior_base64"] == "QU5URVJJT1I="


def test_interpreta_o_cabecalho_debug_da_vinheta():
    debug = interpretar_cabecalho_debug_da_vinheta(
        {"x-vinheta-debug": '{"amostragem_ms": 2100, "desenho_ms": 9800, "encode_ms": 4900, "quantidade_quadros": 150}'}
    )
    assert debug["amostragem_ms"] == 2100
    assert debug["desenho_ms"] == 9800
    assert debug["quantidade_quadros"] == 150


@pytest.mark.asyncio
async def test_baixa_o_mp4_e_os_tempos_do_cabecalho_debug(monkeypatch):
    class Resposta:
        status_code = 200
        content = b"mp4"
        headers = {
            "X-Vinheta-Debug": '{"amostragem_ms": 1800, "desenho_ms": 9000, "encode_ms": 4000}',
        }

    class Cliente:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, json):
            return Resposta()

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Cliente())
    conteudo, debug = await baixar_mp4_renderizado_da_vinheta_com_debug(
        titulo="Consulta",
        efeito="planos-que-abrem-espaco",
        url_base="http://vinhetas.test",
    )

    assert conteudo == b"mp4"
    assert debug["amostragem_ms"] == 1800
    assert debug["encode_ms"] == 4000
