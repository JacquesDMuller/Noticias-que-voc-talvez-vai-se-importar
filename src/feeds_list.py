# -*- coding: utf-8 -*-
"""
RSS Feed Lists by Category
Notícias que você talvez vai se importar
"""

FEEDS = {
    "capa": {
        "name": "Capa",
        "description": "Principais manchetes do dia",
        "feeds": [
            "https://www.bbc.com/portuguese/index.xml",
            "https://g1.globo.com/rss/g1/",
            "https://www.cnnbrasil.com.br/rss/",
            "https://rss.uol.com.br/feed/noticias.xml",
        ]
    },
    "tech": {
        "name": "Tech & Futuro",
        "description": "Tecnologia, inovação e o mundo digital",
        "feeds": [
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.theverge.com/rss/index.xml",
            "https://techcrunch.com/feed/",
            "https://www.wired.com/feed/rss",
            "https://feeds.feedburner.com/TechCrunch/",
        ]
    },
    "ciencia": {
        "name": "Ciência & Espaço",
        "description": "Descobertas científicas e exploração espacial",
        "feeds": [
            "https://www.nasa.gov/rss/dyn/breaking_news.rss",
            "https://www.sciencedaily.com/rss/all.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
            "https://www.nature.com/nature.rss",
            "https://phys.org/rss-feed/",
        ]
    },
    "brasil": {
        "name": "Brasil & Sociedade",
        "description": "Política, economia e sociedade brasileira",
        "feeds": [
            "https://www.bbc.com/portuguese/brasil/index.xml",
            "https://www.cnnbrasil.com.br/politica/rss/",
            "https://rss.uol.com.br/feed/economia.xml",
        ]
    },
    "retro": {
        "name": "Retrô & Narrativas",
        "description": "Histórias fascinantes e domínio público",
        "feeds": [
            "https://www.damninteresting.com/feed/",
            "https://publicdomainreview.org/rss.xml",
            "https://longreads.com/feed/",
            "https://daily.jstor.org/feed/",
        ]
    },
    "variedades": {
        "name": "Variedades",
        "description": "Curiosidades, cultura e lugares incríveis",
        "feeds": [
            "https://www.atlasobscura.com/feeds/latest",
            "https://www.smithsonianmag.com/rss/latest_articles/",
            "https://www.mentalfloss.com/feed",
            "https://www.openculture.com/feed",
        ]
    }
}

# Priority order for Capa selection (articles with images first)
CAPA_PRIORITY_DOMAINS = [
    "bbc.com",
    "g1.globo.com",
    "cnnbrasil.com.br",
    "uol.com.br",
]
