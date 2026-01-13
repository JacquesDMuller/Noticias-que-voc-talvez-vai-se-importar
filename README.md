# Notícias que você talvez vai se importar

Um agregador de notícias automatizado com estética de jornal dos anos 1920.

![Demo](https://img.shields.io/badge/demo-GitHub%20Pages-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-yellow)

## 🗞️ Sobre

Um jornal digital auto-atualizado que coleta notícias de diversas fontes RSS e as apresenta com uma estética vintage inspirada nos jornais dos anos 1920.

**Características:**
- ✅ 100% automatizado (GitHub Actions)
- ✅ Zero dependências de IA
- ✅ Hospedagem gratuita (GitHub Pages)
- ✅ Design responsivo vintage
- ✅ 6 categorias de conteúdo

## 📂 Estrutura

```
├── .github/workflows/
│   └── update_news.yml    # Automação (cron a cada 2h)
├── src/
│   ├── crawler.py         # Motor de crawling
│   ├── feeds_list.py      # Lista de RSS feeds
│   └── main.py            # Entry point
├── public/
│   ├── index.html         # Frontend completo
│   └── data/
│       └── latest.json    # Dados gerados
└── requirements.txt       # Dependências Python
```

## 🚀 Uso Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar crawler
cd src
python main.py

# Abrir frontend
start public/index.html  # Windows
open public/index.html   # macOS
```

## 📰 Categorias

1. **Capa** - Principais manchetes
2. **Tech & Futuro** - Tecnologia e inovação
3. **Ciência & Espaço** - Descobertas científicas
4. **Brasil & Sociedade** - Notícias nacionais
5. **Retrô & Narrativas** - Histórias fascinantes
6. **Variedades** - Curiosidades e cultura

## 🔧 Configuração GitHub Pages

1. Vá em **Settings** > **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / Folder: `/public`
4. Save

## 📜 Licença

MIT License - Uso livre.
