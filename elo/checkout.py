"""O lado do checkout: o que a YouShop faz quando o comprador abre o link.

O checkout confere a assinatura do token, a validade e a versão da ficha.
Se tudo bate, registra um toque do tipo "agente" para o creator do token.
Preço e garantia exibidos vêm sempre da configuração da oferta, nunca do agente.
"""

from __future__ import annotations

from datetime import datetime
from urllib.parse import parse_qs, urlparse

from . import atribuicao, dados


def abrir_checkout(link: str, *, agora: datetime, segredo: bytes) -> dict:
    url = urlparse(link)
    oferta_id = url.path.rsplit("/", 1)[-1]
    token = parse_qs(url.query).get("elo", [""])[0]
    oferta = dados.OFERTAS[oferta_id]
    try:
        carga = atribuicao.validar_token(token, agora=agora, segredo=segredo)
    except atribuicao.TokenInvalido as erro:
        # Link adulterado ou vencido: o comprador ainda pode comprar, só não há atribuição.
        return {"oferta_id": oferta_id, "preco": oferta["preco"], "toque": None,
                "aviso": f"Atribuição ignorada ({erro})."}
    if carga["o"] != oferta_id:
        return {"oferta_id": oferta_id, "preco": oferta["preco"], "toque": None,
                "aviso": "Atribuição ignorada (token de outra oferta)."}
    toque = None
    if carga["c"]:
        toque = {"tipo": "agente", "creator_id": carga["c"], "agente_id": carga["a"],
                 "quando": agora}
    return {"oferta_id": oferta_id, "preco": oferta["preco"],
            "garantia_dias": oferta["garantia_dias"], "toque": toque}
