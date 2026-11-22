"""Dados fictícios do protótipo Elo.

Nada aqui é dado real da YouShop: produtores, ofertas, creators e vendas
foram inventados para demonstrar o fluxo. Datas fixas tornam a demo
reprodutível (o "agora" padrão é 22/11/2026, 10h, horário de Brasília).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))


def dt(texto: str) -> datetime:
    """'2026-11-20 14:02' -> datetime com fuso de Brasília."""
    return datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=BRT)


AGORA_PADRAO = dt("2026-11-22 10:00")

# ---------------------------------------------------------------------------
# Produtores e ofertas
# ---------------------------------------------------------------------------
# Cada oferta guarda as regras comerciais que o produtor configurou na
# plataforma (preço, garantia, comissão, janela de atribuição). Essas regras
# são a fonte da verdade: o agente de IA nunca as calcula, só as consulta.

PRODUTORES = {
    "pr-planilha-viva": "Planilha Viva (Prof. Marina Lopes)",
    "pr-dados-pra-ja": "Dados Pra Já",
    "pr-bolso-em-dia": "Bolso em Dia",
    "pr-pele-serena": "Pele Serena Cosméticos",
    "pr-forca-pura": "Força Pura Nutrição",
}

OFERTAS = {
    "of-excel-dashboard": {
        "nome": "Excel do Zero ao Dashboard",
        "produtor_id": "pr-planilha-viva",
        "tipo": "digital",
        "preco": 197.00,
        "parcelas_max": 12,
        "garantia_dias": 15,
        "comissao_pct": 40,
        "janela_atribuicao_dias": 7,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "excel planilha dashboard graficos tabela dinamica trabalho iniciante",
    },
    "of-excel-concursos": {
        "nome": "Excel para Concursos",
        "produtor_id": "pr-planilha-viva",
        "tipo": "digital",
        "preco": 147.00,
        "parcelas_max": 10,
        "garantia_dias": 7,
        "comissao_pct": 35,
        "janela_atribuicao_dias": 7,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "excel planilha concurso prova formulas",
    },
    "of-powerbi-essencial": {
        "nome": "Power BI Essencial",
        "produtor_id": "pr-dados-pra-ja",
        "tipo": "digital",
        "preco": 297.00,
        "parcelas_max": 12,
        "garantia_dias": 30,
        "comissao_pct": 40,
        "janela_atribuicao_dias": 14,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "power bi dashboard dados relatorio graficos excel",
    },
    "of-financas-pratica": {
        "nome": "Finanças Pessoais na Prática",
        "produtor_id": "pr-bolso-em-dia",
        "tipo": "digital",
        "preco": 97.00,
        "parcelas_max": 6,
        "garantia_dias": 7,
        "comissao_pct": 50,
        "janela_atribuicao_dias": 7,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "financas pessoais orcamento dividas planilha investimento iniciante",
    },
    "of-planilha-controle": {
        "nome": "Planilha de Controle Financeiro (modelo pronto)",
        "produtor_id": "pr-bolso-em-dia",
        "tipo": "digital",
        "preco": 37.00,
        "parcelas_max": 1,
        "garantia_dias": 7,
        "comissao_pct": 50,
        "janela_atribuicao_dias": 7,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "planilha excel financas controle orcamento modelo",
    },
    "of-kit-noite": {
        "nome": "Kit Skincare Noite Calmante",
        "produtor_id": "pr-pele-serena",
        "tipo": "fisico",
        "preco": 129.90,
        "parcelas_max": 3,
        "garantia_dias": 7,
        "comissao_pct": 20,
        "janela_atribuicao_dias": 7,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "skincare cosmetico pele noite hidratante kit",
    },
    "of-whey-isolado": {
        "nome": "Whey Isolado 900 g (baunilha)",
        "produtor_id": "pr-forca-pura",
        "tipo": "fisico",
        "preco": 159.90,
        "parcelas_max": 3,
        "garantia_dias": 7,
        "comissao_pct": 15,
        "janela_atribuicao_dias": 7,
        "modelo_atribuicao": "ultimo_toque",
        "tags": "whey proteina suplemento treino academia",
    },
}

# ---------------------------------------------------------------------------
# Fichas de fatos
# ---------------------------------------------------------------------------
# A ficha é o que um agente de IA pode afirmar sobre a oferta. Uma IA da
# YouShop gera o rascunho a partir da página de vendas e cruza com a
# configuração do checkout; o produtor revisa e aprova. Só ficha
# "aprovada" chega aos agentes. Campos curtos e estruturados: texto livre
# longo é onde mora a "promessa de marketing" e o risco de prompt injection.

FICHAS = {
    "of-excel-dashboard": {
        "versao": 3,
        "status": "aprovada",
        "aprovada_em": "2026-11-18",
        "resumo": "Curso em vídeo para sair do zero e montar dashboards no Excel.",
        "conteudo": [
            "8 módulos, 42 aulas, cerca de 14 h de vídeo",
            "Fórmulas essenciais, tabela dinâmica, gráficos e dashboard final",
            "3 planilhas de exercício para baixar",
        ],
        "para_quem": "Iniciantes que usam Excel no trabalho.",
        "nao_e_para": "Quem já domina tabela dinâmica e Power Query.",
        "acesso": "12 meses",
        "suporte": "Dúvidas por comentário na aula, resposta em até 2 dias úteis",
        "certificado": True,
        "nao_promete": ["Não garante emprego ou promoção."],
    },
    "of-excel-concursos": {
        "versao": 2,
        "status": "aprovada",
        "aprovada_em": "2026-10-30",
        "resumo": "Excel focado no que cai em provas de concursos.",
        "conteudo": [
            "6 módulos, 30 aulas, cerca de 8 h",
            "Questões comentadas de bancas",
        ],
        "para_quem": "Quem estuda para concursos com conteúdo de informática.",
        "nao_e_para": "Quem quer usar Excel para relatórios no trabalho.",
        "acesso": "6 meses",
        "suporte": "Fórum da turma",
        "certificado": True,
        "nao_promete": ["Não garante aprovação em concurso."],
    },
    "of-powerbi-essencial": {
        "versao": 1,
        "status": "aprovada",
        "aprovada_em": "2026-11-02",
        "resumo": "Introdução prática ao Power BI, do dado ao relatório publicado.",
        "conteudo": [
            "7 módulos, 35 aulas, cerca de 12 h",
            "Conexão a planilhas, modelagem simples, DAX básico",
        ],
        "para_quem": "Quem já usa Excel e quer relatórios interativos.",
        "nao_e_para": "Quem nunca abriu uma planilha.",
        "acesso": "12 meses",
        "suporte": "Comunidade no Discord",
        "certificado": True,
        "nao_promete": ["Não inclui licença do Power BI Pro."],
    },
    "of-financas-pratica": {
        "versao": 4,
        "status": "aprovada",
        "aprovada_em": "2026-11-10",
        "resumo": "Organizar orçamento, sair das dívidas e começar a investir.",
        "conteudo": ["5 módulos, 20 aulas, cerca de 5 h", "Planilha de orçamento inclusa"],
        "para_quem": "Quem quer organizar o dinheiro do mês.",
        "nao_e_para": "Quem busca recomendação de ativos específicos.",
        "acesso": "Vitalício",
        "suporte": "Grupo de alunos",
        "certificado": False,
        "nao_promete": ["Não promete renda extra nem rentabilidade."],
    },
    "of-planilha-controle": {
        "versao": 1,
        "status": "aprovada",
        "aprovada_em": "2026-09-14",
        "resumo": "Modelo de planilha pronto para controlar gastos mensais.",
        "conteudo": ["Arquivo .xlsx e versão Google Sheets", "Vídeo de 15 min explicando o uso"],
        "para_quem": "Quem quer só a planilha pronta, sem curso.",
        "nao_e_para": "Quem quer aprender a montar a própria planilha.",
        "acesso": "Download imediato",
        "suporte": "E-mail",
        "certificado": False,
        "nao_promete": [],
    },
    "of-kit-noite": {
        "versao": 2,
        "status": "aprovada",
        "aprovada_em": "2026-11-05",
        "resumo": "Kit com sérum e hidratante para rotina noturna.",
        "conteudo": ["Sérum 30 ml", "Hidratante 50 g"],
        "para_quem": "Rotina de cuidados diários com a pele.",
        "nao_e_para": "Tratamento de acne, rosácea ou outra condição de pele.",
        "entrega": "Correios, 3 a 9 dias úteis",
        "suporte": "WhatsApp da marca",
        "certificado": False,
        "nao_promete": ["Não é medicamento e não trata doenças de pele."],
    },
    "of-whey-isolado": {
        "versao": 1,
        "status": "aprovada",
        "aprovada_em": "2026-10-21",
        "resumo": "Proteína isolada do soro do leite, 30 doses.",
        "conteudo": ["Pote 900 g, sabor baunilha", "Tabela nutricional no rótulo"],
        "para_quem": "Complementar a ingestão de proteína na dieta.",
        "nao_e_para": "Substituir refeições ou orientação de nutricionista.",
        "entrega": "Correios, 3 a 9 dias úteis",
        "suporte": "E-mail da marca",
        "certificado": False,
        "nao_promete": ["Não promete emagrecimento nem ganho de massa garantido."],
    },
}

# Rascunho gerado por IA a partir da página de vendas, ainda NÃO aprovado.
# Serve para mostrar que rascunho nunca chega ao agente de compra.
RASCUNHOS = {
    "of-excel-dashboard": {
        "versao": 4,
        "status": "rascunho",
        "gerado_por": "IA (extração da página de vendas)",
        "divergencias_detectadas": [
            "Página de vendas diz 'garantia de 30 dias'; checkout está configurado com 15 dias.",
        ],
        "resumo": "Domine o Excel em 7 dias e seja promovido!",
    },
}

# ---------------------------------------------------------------------------
# Creators e agentes de creator
# ---------------------------------------------------------------------------
# Um "agente de creator" é um assistente de recomendação (no ChatGPT, Claude,
# Gemini...) que o creator publica para a audiência dele, conectado ao Elo
# com uma credencial própria. A credencial identifica o creator; o modelo de
# linguagem nunca recebe nem escolhe esse dado.

CREATORS = {
    "cr-ana": {"nome": "Ana Ribeiro", "nicho": "Finanças e planilhas"},
    "cr-bruno": {"nome": "Bruno Tech", "nicho": "Dados e tecnologia"},
    "cr-carla": {"nome": "Carla Concursos", "nicho": "Concursos públicos"},
}

AGENTES = {
    "ag-ana-planilhas": {
        "nome": "Agente da Ana, Finanças & Planilhas",
        "creator_id": "cr-ana",
        "ofertas_curadas": [
            "of-excel-dashboard",
            "of-financas-pratica",
            "of-planilha-controle",
            "of-powerbi-essencial",
        ],
    },
    "neutro": {
        "nome": "Agente sem creator (ex.: assistente pessoal do comprador)",
        "creator_id": None,
        "ofertas_curadas": None,  # vê o catálogo inteiro
    },
}

# Afiliações ativas: quais creators podem receber comissão de qual oferta.
AFILIACOES = {
    ("cr-ana", "of-excel-dashboard"),
    ("cr-ana", "of-financas-pratica"),
    ("cr-ana", "of-planilha-controle"),
    ("cr-ana", "of-powerbi-essencial"),
    ("cr-bruno", "of-excel-dashboard"),
    ("cr-bruno", "of-powerbi-essencial"),
    ("cr-carla", "of-excel-concursos"),
    ("cr-carla", "of-excel-dashboard"),
}

# ---------------------------------------------------------------------------
# Vendas (para o Rastro)
# ---------------------------------------------------------------------------
# Cada venda guarda os "toques" que aconteceram antes do pagamento.
# tipo: link (clique em link rastreável), agente (link de checkout gerado na
# sessão de um agente de creator, com token assinado), cupom (cupom ligado a
# um creator), agente_neutro (agente sem creator: não gera comissão e não
# "rouba" a comissão de ninguém).

VENDAS = [
    {
        "id": "V-1042",
        "oferta_id": "of-excel-dashboard",
        "pago_em": "2026-11-20 21:47",
        "meio": "Pix",
        "toques": [
            {"tipo": "agente", "creator_id": "cr-ana", "quando": "2026-11-20 21:31",
             "canal": "Agente da Ana (conversa no ChatGPT)"},
        ],
    },
    {
        "id": "V-1031",
        "oferta_id": "of-excel-dashboard",
        "pago_em": "2026-11-18 19:05",
        "meio": "Cartão 12x",
        "toques": [
            {"tipo": "link", "creator_id": "cr-ana", "quando": "2026-11-16 12:40",
             "canal": "Seu link no Instagram (stories)"},
            {"tipo": "cupom", "creator_id": "cr-bruno", "quando": "2026-11-18 19:03",
             "canal": "Cupom de outro creator aplicado no checkout"},
        ],
    },
    {
        "id": "V-1019",
        "oferta_id": "of-financas-pratica",
        "pago_em": "2026-11-15 08:20",
        "meio": "Cartão 6x",
        "toques": [
            {"tipo": "link", "creator_id": "cr-ana", "quando": "2026-11-05 22:10",
             "canal": "Seu link no YouTube (descrição do vídeo)"},
        ],
    },
    {
        "id": "V-1008",
        "oferta_id": "of-powerbi-essencial",
        "pago_em": "2026-11-09 15:12",
        "meio": "Cartão 3x",
        "reembolsado_em": "2026-11-13 10:00",
        "toques": [
            {"tipo": "agente", "creator_id": "cr-ana", "quando": "2026-11-09 14:58",
             "canal": "Agente da Ana (conversa no Claude)"},
        ],
    },
    {
        "id": "V-0987",
        "oferta_id": "of-planilha-controle",
        "pago_em": "2026-10-28 12:30",
        "meio": "Pix",
        "toques": [
            {"tipo": "link", "creator_id": "cr-ana", "quando": "2026-10-28 12:22",
             "canal": "Seu link no Instagram (bio)"},
        ],
    },
    {
        "id": "V-0975",
        "oferta_id": "of-excel-dashboard",
        "pago_em": "2026-11-12 20:15",
        "meio": "Pix",
        "toques": [
            {"tipo": "link", "creator_id": "cr-ana", "quando": "2026-11-11 18:30",
             "canal": "Seu link no TikTok"},
            {"tipo": "agente_neutro", "creator_id": None, "quando": "2026-11-12 20:09",
             "canal": "Assistente pessoal do comprador (agente sem creator)"},
        ],
    },
]
