"""Motor de atribuição e tokens assinados do Elo.

Regra de ouro do projeto: tudo que envolve dinheiro (quem ganha a comissão,
quanto, quando libera) é calculado aqui, em código determinístico e testado.
O modelo de linguagem só explica o resultado; nunca decide.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import dados

# ---------------------------------------------------------------------------
# Tokens de atribuição (o "link rastreável" da era dos agentes)
# ---------------------------------------------------------------------------
# Hoje o creator é identificado por um clique num link. Numa conversa com um
# agente não existe esse clique. O Elo emite, no momento em que o agente gera
# o link de checkout, um token assinado com o creator dono da sessão. O
# token não é parâmetro de ferramenta: o modelo não consegue forjá-lo nem
# trocar o creator.

VALIDADE_TOKEN_HORAS = 72


class TokenInvalido(Exception):
    pass


def _b64(dados_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(dados_bytes).rstrip(b"=").decode()


def _unb64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def emitir_token(*, oferta_id: str, versao_ficha: int, agente_id: str,
                 creator_id: str | None, agora: datetime, segredo: bytes) -> str:
    carga = {
        "o": oferta_id,
        "v": versao_ficha,
        "a": agente_id,
        "c": creator_id,
        "iat": int(agora.timestamp()),
        "exp": int((agora + timedelta(hours=VALIDADE_TOKEN_HORAS)).timestamp()),
    }
    corpo = _b64(json.dumps(carga, separators=(",", ":")).encode())
    assinatura = _b64(hmac.new(segredo, corpo.encode(), hashlib.sha256).digest())
    return f"{corpo}.{assinatura}"


def validar_token(token: str, *, agora: datetime, segredo: bytes) -> dict:
    try:
        corpo, assinatura = token.split(".")
    except ValueError as erro:
        raise TokenInvalido("formato inválido") from erro
    esperada = _b64(hmac.new(segredo, corpo.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(esperada, assinatura):
        raise TokenInvalido("assinatura não confere")
    carga = json.loads(_unb64(corpo))
    if agora.timestamp() > carga["exp"]:
        raise TokenInvalido("token expirado")
    return carga


# ---------------------------------------------------------------------------
# Atribuição de uma venda
# ---------------------------------------------------------------------------

@dataclass
class ToqueAvaliado:
    tipo: str
    creator_id: str | None
    quando: datetime
    canal: str
    contou: bool = False
    motivo: str = ""


@dataclass
class Decisao:
    creator_vencedor: str | None
    regra: str
    toques: list[ToqueAvaliado] = field(default_factory=list)


def _descricao_regra(oferta: dict) -> str:
    janela = oferta["janela_atribuicao_dias"]
    if oferta["modelo_atribuicao"] == "ultimo_toque":
        return (f"Último toque válido de creator até {janela} dias antes do pagamento "
                "(regra escolhida pelo produtor).")
    return (f"Primeiro toque válido de creator até {janela} dias antes do pagamento "
            "(regra escolhida pelo produtor).")


def resolver(venda: dict) -> Decisao:
    """Decide qual creator (se algum) ganha a comissão de uma venda."""
    oferta = dados.OFERTAS[venda["oferta_id"]]
    pago_em = dados.dt(venda["pago_em"])
    inicio_janela = pago_em - timedelta(days=oferta["janela_atribuicao_dias"])

    avaliados: list[ToqueAvaliado] = []
    elegiveis: list[ToqueAvaliado] = []
    for bruto in venda["toques"]:
        toque = ToqueAvaliado(
            tipo=bruto["tipo"],
            creator_id=bruto["creator_id"],
            quando=dados.dt(bruto["quando"]),
            canal=bruto["canal"],
        )
        if toque.creator_id is None:
            toque.motivo = "agente_sem_creator"
        elif toque.quando < inicio_janela:
            toque.motivo = "fora_da_janela"
        elif toque.quando > pago_em:
            toque.motivo = "depois_do_pagamento"
        elif (toque.creator_id, venda["oferta_id"]) not in dados.AFILIACOES:
            toque.motivo = "nao_elegivel"
        else:
            elegiveis.append(toque)
        avaliados.append(toque)

    vencedor = None
    if elegiveis:
        if oferta["modelo_atribuicao"] == "ultimo_toque":
            escolhido = max(elegiveis, key=lambda t: t.quando)
        else:
            escolhido = min(elegiveis, key=lambda t: t.quando)
        escolhido.contou = True
        escolhido.motivo = "toque_vencedor"
        vencedor = escolhido.creator_id
        for toque in elegiveis:
            if toque is not escolhido:
                toque.motivo = ("houve_toque_posterior" if toque.quando < escolhido.quando
                                else "houve_toque_anterior")

    return Decisao(creator_vencedor=vencedor, regra=_descricao_regra(oferta), toques=avaliados)


# ---------------------------------------------------------------------------
# Status da comissão para um creator
# ---------------------------------------------------------------------------

def status_para_creator(venda: dict, creator_id: str, agora: datetime) -> dict:
    oferta = dados.OFERTAS[venda["oferta_id"]]
    decisao = resolver(venda)
    pago_em = dados.dt(venda["pago_em"])
    fim_garantia = pago_em + timedelta(days=oferta["garantia_dias"])
    valor_comissao = round(oferta["preco"] * oferta["comissao_pct"] / 100, 2)

    if decisao.creator_vencedor != creator_id:
        meus = [t for t in decisao.toques if t.creator_id == creator_id]
        if any(t.motivo == "fora_da_janela" for t in meus) and not any(
                t.motivo in ("houve_toque_posterior", "houve_toque_anterior") for t in meus):
            codigo = "seu_toque_fora_da_janela"
        elif any(t.motivo in ("houve_toque_posterior", "houve_toque_anterior") for t in meus):
            codigo = "toque_de_outro_creator_venceu"
        else:
            codigo = "nao_elegivel"
        return {"status": "nao_comissionada", "codigo": codigo, "valor": 0.0,
                "decisao": decisao, "fim_garantia": fim_garantia}

    if venda.get("reembolsado_em"):
        return {"status": "estornada", "codigo": "reembolso_dentro_da_garantia",
                "valor": 0.0, "valor_original": valor_comissao, "decisao": decisao,
                "fim_garantia": fim_garantia,
                "reembolsado_em": dados.dt(venda["reembolsado_em"])}

    if agora < fim_garantia:
        return {"status": "em_garantia", "codigo": "aguardando_fim_da_garantia",
                "valor": valor_comissao, "decisao": decisao, "fim_garantia": fim_garantia,
                "libera_em": fim_garantia}

    return {"status": "liberada", "codigo": "liberada", "valor": valor_comissao,
            "decisao": decisao, "fim_garantia": fim_garantia, "libera_em": fim_garantia}
