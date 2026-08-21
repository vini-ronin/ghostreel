# GhostReel Explorer 🎬👻

O **GhostReel Explorer** é uma ferramenta web de raspagem, análise e download em lote de Reels e posts do Instagram. Construído em Python com **FastAPI**, ele permite explorar perfis, visualizar métricas de engajamento e baixar conteúdos de forma rápida e prática.

---

## ✨ Funcionalidades Principais

- ⚡ **Scraping em Tempo Real (SSE)**: Streaming ultra-rápido de Reels, Carrosséis e Fotos de qualquer perfil público.
- 🎯 **Radar de Nichos & Correntes Virais**: Varredura recursiva de perfis do mesmo nicho com identificação da **Taxa Outlier** (proporção views/seguidores).
- 🏆 **Isolamento de Top 3 Virais**: Identifica automaticamente os 3 melhores conteúdos de cada perfil da corrente com opção de download direto.
- 📁 **Presets de Nichos Open Source**: Presets pré-configurados (`niches.json`) para Fitness, Finanças, Tech/AI, Culinária, Podcasts e Negócios.
- 📊 **Métricas de Engajamento**: Exibe contagem de visualizações, curtidas, comentários e taxa média de engajamento.
- 🔑 **Sessão Autenticada (Cookie `sessionid`)**: Suporte a sessão do Instagram para evitar bloqueios e acessar perfis restritos.
- 📥 **Download Individual e em Lote (.ZIP)**: Faça download direto de Reels/vídeos individualmente ou empacotados em arquivo `.zip`.
- 📁 **Integração com Sistema Operacional**: Botão para abrir a pasta de downloads diretamente no Windows Explorer.

---

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.10+** instalado no sistema.

### Passo a Passo

1. **Clonar o Repositório ou Acessar a Pasta**:
   ```bash
   cd ghostreel
   ```

2. **Instalar as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar o Servidor FastAPI**:
   ```bash
   python app.py
   ```
   *Ou utilizando o Uvicorn diretamente:*
   ```bash
   uvicorn app:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Acessar a Aplicação**:
   Abra seu navegador e acesse: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📁 Estrutura do Projeto

```text
ghostreel/
├── app.py              # Servidor principal (FastAPI + Endpoints & Scraping)
├── requirements.txt    # Dependências do projeto (FastAPI, Requests, Uvicorn, etc.)
├── session.json        # Arquivo local de armazenamento da sessão autenticada
├── templates/
│   └── index.html      # Interface web principal (HTML + CSS/JS)
├── static/             # Arquivos estáticos (Estilos e Scripts adicionais)
└── downloads/          # Pasta local para armazenamento de vídeos baixados
```

---

## 💡 Dica de Uso (Sessão do Instagram)

Para extrair mais mídias e evitar que o Instagram limite as requisições:
1. Abra o Instagram no seu navegador e faça login.
2. Abra as Ferramentas do Desenvolvedor (`F12`), vá na aba **Application / Aplicativo** > **Cookies**.
3. Copie o valor do cookie `sessionid`.
4. Cole o `sessionid` no campo de autenticação na interface do **GhostReel**.

---

## ⚠️ Aviso Legal

Esta ferramenta destina-se exclusivamente a fins educacionais e de pesquisa de mercado. O download e uso de conteúdos de terceiros deve respeitar os termos de serviço e direitos autorais da plataforma.
