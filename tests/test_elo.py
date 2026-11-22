import asyncio
import json
from datetime import timedelta

import pytest

from elo import atribuicao, checkout, dados
from elo.servidor import criar_servidor

SEGREDO = b"teste"
AGORA = dados.AGORA_PADRAO


def chamar(sessao, ferramenta, args=None):
    servidor = criar_servidor(sessao, agora=AGORA, segredo=SEGREDO)
    resultado = asyncio.run(servidor.call_tool(ferramenta, args or {}))
    return json.loads(resultado.content[0].text)


def nomes_ferramentas(sessao):
    servidor = criar_servidor(sessao, agora=AGORA, segredo=SEGREDO)
    return {t.name for t in asyncio.run(servidor.list_tools())}


def venda(id_):
    return next(v for v in dados.VENDAS if v["id"] == id_)


# --- Atribuição -----------------------------------------------------------

def test_agente_do_creator_gera_comissao_em_garantia():
    st = atribuicao.status_para_creator(venda("V-1042"), "cr-ana", AGORA)
    assert st["status"] == "em_garantia"
    assert st["valor"] == pytest.approx(78.80)


def test_cupom_posterior_de_outro_creator_vence_ultimo_toque():
    decisao = atribuicao.resolver(venda("V-1031"))
    assert decisao.creator_vencedor == "cr-bruno"
    st = atribuicao.status_para_creator(venda("V-1031"), "cr-ana", AGORA)
    assert st["codigo"] == "toque_de_outro_creator_venceu"


def test_clique_fora_da_janela_nao_conta():
    st = atribuicao.status_para_creator(venda("V-1019"), "cr-ana", AGORA)
    assert st["codigo"] == "seu_toque_fora_da_janela"


def test_reembolso_estorna_comissao():
    st = atribuicao.status_para_creator(venda("V-1008"), "cr-ana", AGORA)
    assert st["status"] == "estornada" and st["valor"] == 0


def test_comissao_libera_apos_garantia():
    st = atribuicao.status_para_creator(venda("V-0987"), "cr-ana", AGORA)
    assert st["status"] == "liberada"


def test_agente_sem_creator_nao_rouba_comissao():
    decisao = atribuicao.resolver(venda("V-0975"))
    assert decisao.creator_vencedor == "cr-ana"


# --- Tokens e checkout ----------------------------------------------------

def test_token_adulterado_e_ignorado_no_checkout():
    link = chamar("agente:ag-ana-planilhas", "gerar_link_checkout",
                  {"oferta_id": "of-excel-dashboard", "versao_ficha": 3})["link_checkout"]
    ok = checkout.abrir_checkout(link, agora=AGORA, segredo=SEGREDO)
    assert ok["toque"]["creator_id"] == "cr-ana"
    adulterado = link[:-3] + ("abc" if not link.endswith("abc") else "xyz")
    ruim = checkout.abrir_checkout(adulterado, agora=AGORA, segredo=SEGREDO)
    assert ruim["toque"] is None


def test_token_expira():
    token = atribuicao.emitir_token(oferta_id="of-excel-dashboard", versao_ficha=3,
                                    agente_id="ag-ana-planilhas", creator_id="cr-ana",
                                    agora=AGORA, segredo=SEGREDO)
    with pytest.raises(atribuicao.TokenInvalido):
        atribuicao.validar_token(token, agora=AGORA + timedelta(hours=73), segredo=SEGREDO)


# --- Servidor MCP ---------------------------------------------------------

def test_agente_da_audiencia_nao_enxerga_ferramentas_de_vendas():
    assert "minhas_vendas" not in nomes_ferramentas("agente:ag-ana-planilhas")
    assert "rastro_da_comissao" not in nomes_ferramentas("agente:ag-ana-planilhas")
    assert {"minhas_vendas", "rastro_da_comissao"} <= nomes_ferramentas("creator:cr-ana")


def test_atribuicao_nao_e_parametro_de_ferramenta():
    servidor = criar_servidor("agente:ag-ana-planilhas", agora=AGORA, segredo=SEGREDO)
    for ferramenta in asyncio.run(servidor.list_tools()):
        propriedades = ferramenta.input_schema.get("properties", {})
        assert not any("creator" in p for p in propriedades), ferramenta.name


def test_ficha_desatualizada_recusa_link():
    r = chamar("agente:ag-ana-planilhas", "gerar_link_checkout",
               {"oferta_id": "of-excel-dashboard", "versao_ficha": 2})
    assert r["erro"] == "ficha_desatualizada" and r["preco_atual"] == 197.0


def test_rascunho_de_ia_nunca_chega_ao_agente():
    ficha = chamar("agente:neutro", "detalhar_oferta", {"oferta_id": "of-excel-dashboard"})
    assert "Domine o Excel em 7 dias" not in json.dumps(ficha, ensure_ascii=False)
    assert ficha["garantia_dias"] == 15


def test_divulgacao_obrigatoria_no_agente_de_creator():
    r = chamar("agente:ag-ana-planilhas", "gerar_link_checkout",
               {"oferta_id": "of-excel-dashboard", "versao_ficha": 3})
    assert "Ana Ribeiro" in r["divulgacao_obrigatoria"]
    neutro = chamar("agente:neutro", "gerar_link_checkout",
                    {"oferta_id": "of-excel-dashboard", "versao_ficha": 3})
    assert neutro["divulgacao_obrigatoria"] is None


def test_busca_respeita_preco_e_nao_ordena_por_comissao():
    r = chamar("agente:neutro", "buscar_ofertas",
               {"consulta": "excel dashboard", "preco_max": 200})
    ids = [o["oferta_id"] for o in r["ofertas"]]
    assert "of-powerbi-essencial" not in ids
    assert ids[0] == "of-excel-dashboard"


def test_rastro_nao_revela_outro_creator():
    r = chamar("creator:cr-ana", "rastro_da_comissao", {"venda_id": "V-1031"})
    texto = json.dumps(r, ensure_ascii=False)
    assert "Bruno" not in texto and "cr-bruno" not in texto


def test_creator_nao_ve_venda_alheia():
    r = chamar("creator:cr-carla", "rastro_da_comissao", {"venda_id": "V-1042"})
    assert r["erro"] == "venda_nao_encontrada"
