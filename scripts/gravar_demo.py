"""Grava as chamadas reais ao servidor MCP do Elo (via protocolo MCP, transporte stdio)
e salva as respostas em demo/gravacao.json, usadas pela demo web.

A fala do agente na demo é um roteiro ilustrativo; as respostas das ferramentas
são exatamente as que o servidor devolveu nesta gravação.

Uso: python scripts/gravar_demo.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp.client.client import Client
from mcp.client.stdio import StdioServerParameters

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from elo import checkout, dados  # noqa: E402

SEGREDO = "segredo-de-demonstracao"


def parametros(sessao: str) -> StdioServerParameters:
    env = dict(os.environ, ELO_SESSAO=sessao, ELO_SEGREDO=SEGREDO, PYTHONPATH=str(RAIZ))
    return StdioServerParameters(command=sys.executable, args=["-m", "elo"], env=env, cwd=str(RAIZ))


async def sessao_gravada(sessao: str, chamadas: list[tuple[str, dict]]) -> dict:
    registro = {"sessao": sessao, "ferramentas": [], "chamadas": []}
    async with Client(parametros(sessao)) as cliente:
        ferramentas = await cliente.list_tools()
        registro["ferramentas"] = [t.name for t in ferramentas.tools]
        for nome, argumentos in chamadas:
            resultado = await cliente.call_tool(nome, argumentos)
            texto = resultado.content[0].text
            registro["chamadas"].append({"ferramenta": nome, "argumentos": argumentos,
                                         "resposta": json.loads(texto)})
    return registro


async def main() -> None:
    compra = await sessao_gravada("agente:ag-ana-planilhas", [
        ("buscar_ofertas", {"consulta": "excel para montar dashboards no trabalho", "preco_max": 200}),
        ("detalhar_oferta", {"oferta_id": "of-excel-dashboard"}),
        ("gerar_link_checkout", {"oferta_id": "of-excel-dashboard", "versao_ficha": 2}),
        ("gerar_link_checkout", {"oferta_id": "of-excel-dashboard", "versao_ficha": 3}),
    ])
    link = compra["chamadas"][-1]["resposta"]["link_checkout"]
    no_checkout = checkout.abrir_checkout(link, agora=dados.AGORA_PADRAO, segredo=SEGREDO.encode())
    no_checkout["toque"]["quando"] = no_checkout["toque"]["quando"].strftime("%d/%m/%Y %H:%M")
    adulterado = checkout.abrir_checkout(link.replace("cr-ana", "x")[:-4] + "AAAA",
                                         agora=dados.AGORA_PADRAO, segredo=SEGREDO.encode())

    painel = await sessao_gravada("creator:cr-ana", [
        ("minhas_vendas", {}),
        *[("rastro_da_comissao", {"venda_id": v["id"]}) for v in dados.VENDAS],
    ])

    saida = {
        "gerado_por": "scripts/gravar_demo.py (cliente MCP real, transporte stdio)",
        "agora_simulado": dados.AGORA_PADRAO.strftime("%d/%m/%Y %H:%M"),
        "compra": compra,
        "checkout": {"link_valido": no_checkout, "link_adulterado": adulterado},
        "painel_creator": painel,
    }
    destino = RAIZ / "demo" / "gravacao.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gravado em {destino}")

    # Monta a demo web: injeta a gravação no modelo e gera um único HTML autocontido.
    modelo = (RAIZ / "demo" / "modelo.html").read_text(encoding="utf-8")
    html = modelo.replace("/*__GRAVACAO__*/null", json.dumps(saida, ensure_ascii=False))
    (RAIZ / "demo" / "index.html").write_text(html, encoding="utf-8")
    print("Demo montada em demo/index.html")
    print("Ferramentas no agente da audiência:", compra["ferramentas"])
    print("Ferramentas no painel da creator:", painel["ferramentas"])


if __name__ == "__main__":
    asyncio.run(main())
