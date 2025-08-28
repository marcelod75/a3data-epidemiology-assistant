# == A3Data Epidemiology Assistant: bootstrap de repo ==
# Execute na raiz do repositório. Requer git já inicializado e remoto configurado.

$ErrorActionPreference = "Stop"

# 1) .gitignore (sobrescreve com entradas recomendadas)
$gitignore = @'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.sqlite3

# Virtual env
.venv/

# VSCode
.vscode/

# Env / Secrets
.env
.env.*
!.env.example

# Artifacts / Vector DB
artifacts/chroma/
artifacts/*.jsonl

# OS / misc
.DS_Store
Thumbs.db
'@
Set-Content -Path ".gitignore" -Value $gitignore -Encoding UTF8
Write-Host "✓ .gitignore escrito/atualizado" -ForegroundColor Green

# 2) .env.example (NÃO commitar a chave real)
$envExample = @'
# Preencha e salve como .env (NÃO comitar .env)
OPENAI_API_KEY=coloque_sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
PERSIST_DIR=artifacts/chroma
COLLECTION_NAME=eu_epi_2021
'@
Set-Content -Path ".env.example" -Value $envExample -Encoding UTF8
Write-Host "✓ .env.example criado" -ForegroundColor Green

# 3) README.md (guia completo)
$readme = @'
# A3Data Epidemiology Assistant

Assistente RAG (Retrieval-Augmented Generation) para responder perguntas sobre os **Relatórios Epidemiológicos 2021 (UE/EEA)**.

Pipeline:
- **Ingestão** de PDFs → **ChromaDB** (embeddings)
- **API** em **FastAPI** (endpoint `/ask`)
- **LLM** via OpenAI (opcional – sem chave, retorna apenas trechos)

---

## ✨ Funcionalidades
- Busca semântica (ChromaDB)
- Respostas com fontes (arquivo + chunk)
- Swagger UI: `http://127.0.0.1:8000/docs`

---

## 🧱 Requisitos
- Python 3.11+
- Windows PowerShell com execução de scripts habilitada (ver *Troubleshooting*)

---

## 🚀 Setup

```powershell
git clone https://github.com/marcelod75/a3data-epidemiology-assistant.git
cd a3data-epidemiology-assistant

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
