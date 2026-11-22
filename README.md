# Elo: a vitrine da YouShop para agentes de IA

Protótipo do Desafio de Inovação do Programa de Estágio YouShop 2027.
Vaga: **Desenvolvimento, Integrações com Agentes de IA (MCP)**.
Autor: Alexandre Vital Demolinari Pereira ([LinkedIn](https://www.linkedin.com/in/alexandrevital)).

**Demo navegável (sem instalar nada):** https://claude.ai/artifact/Qk7pEXQH1Z89DTeQ4HysFR

> **Quando a compra acontece dentro de uma IA, quem paga o creator?**

## O problema

Na YouShop, a venda de um creator depende de um clique: o creator recebe um link
rastreável, divulga, e a plataforma identifica quem trouxe o comprador. Só que o
comprador está começando a pedir recomendações e a comprar dentro de agentes de IA
(ChatGPT, Claude, Gemini). Nessa conversa não existe o clique no link. Daí vêm três perdas:

* **Creator:** a venda que ele influenciou chega sem rastro e a comissão some.
* **Produtor:** o agente não tem fatos confiáveis da oferta (preço, garantia, conteúdo).
  Ou não recomenda o produto, ou recomenda com informação inventada.
* **Comprador:** decide com base no que o modelo "acha" e não no que a oferta realmente diz.

Somado a isso, mesmo quando a venda é rastreada, o creator não entende por que uma
comissão não caiu. A regra existe, mas ninguém explica.

## A solução: Elo + Rastro

Um servidor **MCP** que torna a YouShop legível e comprável por agentes de IA,
preservando a comissão de quem trouxe o comprador:

| Peça | O que faz |
|---|---|
| **Ficha de fatos** | O que um agente pode afirmar sobre uma oferta. Uma IA rascunha a partir da página de vendas e cruza com o checkout; o produtor aprova. Só ficha aprovada chega ao agente. |
| **Agente do creator** | O creator publica um assistente de recomendação com a curadoria dele. Cada link de checkout gerado ali carrega um token assinado com a identidade do creator: atribuição sem depender de cookie. |
| **Rastro** | No assistente do próprio creator: "por que essa venda não me pagou?". A plataforma calcula a trilha (clique → janela → checkout → garantia → liberação) e a IA só explica. |

## Ferramentas MCP

| Ferramenta | Sessão | Tipo |
|---|---|---|
| `buscar_ofertas(consulta, preco_max?, tipo?)` | agente e creator | leitura |
| `detalhar_oferta(oferta_id)` | agente e creator | leitura |
| `gerar_link_checkout(oferta_id, versao_ficha)` | agente e creator | gera link (não cobra) |
| `minhas_vendas()` | **só creator** | leitura |
| `rastro_da_comissao(venda_id)` | **só creator** | leitura |
| recurso `elo://politica-para-agentes` | todas | leitura |

## Decisões técnicas

1. **O código decide, a IA explica.** Atribuição, comissão, garantia e liberação são
   calculadas em `elo/atribuicao.py`, de forma determinística e testada. O modelo
   nunca faz conta de dinheiro.
2. **A atribuição está fora do alcance do modelo.** A identidade do creator vem da
   credencial da sessão (no protótipo, `ELO_SESSAO`; em produção, OAuth). Não é
   parâmetro de nenhuma ferramenta, então o modelo não consegue forjá-la. O teste
   `test_atribuicao_nao_e_parametro_de_ferramenta` garante isso.
3. **Token assinado (HMAC) no link de checkout.** O checkout confere assinatura,
   validade (72 h) e oferta. Link adulterado continua vendendo, só perde a atribuição.
4. **Ficha versionada.** `gerar_link_checkout` exige a versão lida. Se o produtor
   mudou preço ou garantia, o link é recusado e os valores atuais são devolvidos.
5. **Menor privilégio.** O agente que a audiência usa nem enxerga as ferramentas de
   vendas. Elas só existem na sessão do próprio creator.
6. **Agente sem creator não "rouba" comissão.** Se o comprador veio pelo link da Ana
   e terminou a compra no assistente pessoal dele, a comissão continua com a Ana.
7. **Privacidade no Rastro.** O creator nunca vê quem é o outro creator nem dados do
   comprador. Regras de elegibilidade e antifraude não são detalhadas, porque
   explicar demais ensina a burlar.
8. **Conteúdo de oferta é dado, não instrução.** Campos curtos e estruturados,
   rascunho de IA nunca publicado sem aprovação, e instruções do servidor contra
   prompt injection.

## Como rodar

Requer Python 3.10+.

```bash
pip install -r requirements.txt
python -m pytest -q          # 16 testes
python scripts/gravar_demo.py   # grava chamadas reais via MCP em demo/gravacao.json
```

### No Claude Desktop

Em *Configurações → Desenvolvedor → Editar configuração*, adicione (ajuste o caminho):

```json
{
  "mcpServers": {
    "elo-agente-da-ana": {
      "command": "python",
      "args": ["-m", "elo"],
      "env": {
        "ELO_SESSAO": "agente:ag-ana-planilhas",
        "PYTHONPATH": "C:\\caminho\\para\\elo"
      }
    },
    "elo-painel-da-ana": {
      "command": "python",
      "args": ["-m", "elo"],
      "env": {
        "ELO_SESSAO": "creator:cr-ana",
        "PYTHONPATH": "C:\\caminho\\para\\elo"
      }
    }
  }
}
```

Reinicie o Claude Desktop e teste:

* **Como comprador** (ative só `elo-agente-da-ana`): *"Quero aprender Excel para montar
  dashboards no trabalho, até R$ 200 e com garantia. O que você recomenda?"*
* **Como creator** (ative só `elo-painel-da-ana`): *"Por que a venda V-1031 não me
  pagou comissão?"*

Sessões disponíveis: `agente:neutro`, `agente:ag-ana-planilhas`, `creator:cr-ana`,
`creator:cr-bruno`, `creator:cr-carla`.

## Estrutura

```
elo/
  dados.py        dados fictícios (ofertas, fichas, creators, vendas)
  atribuicao.py   motor de atribuição + tokens assinados
  checkout.py     o que o checkout faz ao receber o link
  servidor.py     servidor MCP (SDK oficial em Python, v2)
scripts/gravar_demo.py
tests/test_elo.py
demo/index.html   demo navegável (abre no navegador, sem instalar nada)
```

## Limites do protótipo

* Todos os dados são fictícios. Nada aqui usa dados ou sistemas reais da YouShop.
* Não há pagamento: o link aponta para um domínio de exemplo (`.example`).
* A busca é textual simples. Em produção, busca semântica com o mesmo critério:
  relevância, nunca comissão.
* A geração do rascunho da ficha por IA está simulada (há um exemplo de rascunho com
  divergência detectada em `dados.RASCUNHOS`).
* Credencial por variável de ambiente. Em produção: OAuth por agente e por creator,
  limite de requisições e trilha de auditoria.
