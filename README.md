<div align="center">

<img src="static/logo.jpg" alt="GhostReel Logo" width="120" style="border-radius: 12px; margin-bottom: 12px;"/>

# 👻 GhostReel | Dark Viral Explorer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-FF5A36.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg?style=for-the-badge)](LICENSE)

**GhostReel** é um garimpador e explorador de conteúdo viral para Instagram de alta velocidade (< 0.4s), operando via API Privada Mobile com streaming em tempo real (SSE), análise de métricas virais e download direto de Reels e Carrosséis em alta resolução sem compressão.

*GhostReel is an ultra-fast (< 0.4s) viral Instagram content miner and explorer, powered by private Mobile API endpoints with live SSE streaming, engagement analytics, and high-speed direct MP4 CDN downloads without compression.*

---

[🇧🇷 Português](#-português) • [🇺🇸 English](#-english)

</div>

---

## 🇧🇷 Português

### ✨ Funcionalidades Principais

- ⚡ **Mineração Ultra-Rápida (< 0.4s):** Comunicação direta via API Privada Mobile do Instagram, dispensando emuladores lentos ou extensões instáveis.
- 📡 **Streaming em Tempo Real (SSE):** O perfil e os cards de vídeo começam a aparecer na tela em milissegundos enquanto a extração acontece.
- 🛡️ **Zero Rate Limit (401-Proof):** Autenticação local persistente via cookie de sessão (`sessionid`), evitando bloqueios de visitantes anônimos.
- 🎯 **Filtro de Formatos Inteligente:** Alterne facilmente entre *Apenas Reels*, *Apenas Carrosséis* ou *Todos os Formatos*.
- 📊 **Detecção Automática de Virais:** Algoritmo que calcula a média de visualizações do perfil e destaca vídeos com performance acima de 180% da média com a tag `VIRAL`.
- 🔗 **Radar de Nicho (Perfis Semelhantes):** Extrai contas recomendadas e do mesmo nicho com 1 clique para copiar o `@`.
- 📥 **Download Direto em Alta Qualidade:** Baixa vídeos individuais ou lotes inteiros diretamente dos CDNs do Instagram para sua pasta local `downloads/`.
- 🌓 **Modo Escuro / Claro (Dark & Light Mode):** Interface minimalista tech com paleta Obsidian/Coral e tema claro de alta precisão.
- 🌐 **Totalmente Bilíngue (PT-BR / EN):** Alternância instantânea de idioma sem recarregar a página.

---

### 🚀 Instalação e Execução

#### 1. Pré-requisitos
- Python 3.10 ou superior
- Git

#### 2. Clonar o Repositório
```bash
git clone https://github.com/SEU_USUARIO/ghostreel.git
cd ghostreel
```

#### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 4. Iniciar o Servidor
```bash
python app.py
```
Acesse no seu navegador: **`http://127.0.0.1:8000`**

---

### ⚙️ Conectando sua Conta (Opcional, porém recomendado)
1. No painel web do GhostReel, clique em **`CONECTAR CONTA IG`** no canto superior direito.
2. No seu navegador, abra o Instagram logado &rarr; aperte `F12` &rarr; aba **Application / Aplicativo** &rarr; **Cookies** &rarr; `https://www.instagram.com`.
3. Copie o valor do cookie **`sessionid`** e salve no modal. Sua sessão ficará salva localmente e de forma segura no seu computador.

---

<br/>

---

## 🇺🇸 English

### ✨ Key Features

- ⚡ **Ultra-Fast Scraping (< 0.4s):** Direct communication with Instagram's Private Mobile API, eliminating slow browser automation and fragile extensions.
- 📡 **Live Real-Time Streaming (SSE):** Profiles and video cards stream into the UI in milliseconds as data arrives.
- 🛡️ **Rate Limit Resistant (401-Proof):** Persistent session management via local `sessionid` cookie prevents anonymous visitor blocks.
- 🎯 **Smart Format Filtering:** Toggle between *Reels Only*, *Carousels Only*, or *All Media Formats*.
- 📊 **Automated Viral Detection:** Algorithm evaluates profile average views and flags posts performing 180%+ above average with a glowing `VIRAL` badge.
- 🔗 **Niche Discovery (Related Profiles):** Discovers related accounts in the same niche with 1-click copy functionality.
- 📥 **High-Speed Direct Downloads:** Download single videos or bulk batches directly from Instagram CDN endpoints to your local `downloads/` folder.
- 🌓 **Dark & Light Mode:** Minimalist OpenClaw-inspired tech UI with Dark Obsidian / Coral Neon and high-contrast Light themes.
- 🌐 **Bilingual (PT-BR / EN):** Instant language switching without page reloads.

---

### 🚀 Getting Started

#### 1. Prerequisites
- Python 3.10+
- Git

#### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ghostreel.git
cd ghostreel
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
python app.py
```
Open your browser at: **`http://127.0.0.1:8000`**

---

### 📂 Project Structure

```
ghostreel/
├── app.py                  # FastAPI Backend & Private Mobile API Engine
├── requirements.txt        # Python dependencies
├── session.json            # Local authenticated session (gitignored)
├── static/
│   └── logo.jpg            # Pixel art GhostReel logo mascot
├── templates/
│   └── index.html          # Reactive Dark/Light & Bilingual Dashboard UI
├── downloads/              # Downloaded high-resolution MP4 videos
└── README.md               # Documentation (PT-BR / EN)
```

---

### 🗺️ GhostReel Ecosystem Roadmap

- [x] **System 1: GhostReel Explorer** (Viral miner, engagement analytics, fast bulk downloader)
- [ ] **System 2: GhostReel Studio** (Mass video editor, FFmpeg GPU acceleration, Canva PNG overlay & anti-hash alterations)
- [ ] **System 3: GhostReel Cloud Publisher** (VPS scheduler, Google Drive watcher & auto-reposter)

---

### 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
