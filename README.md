A3Data Epidemiology Assistant

Assistente RAG (Retrieval-Augmented Generation) para responder perguntas sobre os Relatórios Epidemiológicos 2021 (UE/EEA).
Pipeline: ingestão de PDFs → ChromaDB (embeddings) → FastAPI (/ask) → LLM OpenAI (opcional).

✨ O que ele faz

Faz busca semântica em chunks dos relatórios (ChromaDB).

Gera respostas baseadas nos trechos recuperados (RAG).

Cita fontes (arquivo + chunk) no final da resposta.

Possui Swagger UI em http://127.0.0.1:8000/docs.

🧱 Pré-requisitos

Windows + PowerShell

Python 3.11+

(Opcional) Chave da OpenAI para respostas com LLM
Sem chave, a API retorna “Sem LLM configurado” + trechos relevantes (útil para demo).

🚀 Setup rápido (5 min)
# 1) clonar e entrar
git clone https://github.com/marcelod75/a3data-epidemiology-assistant.git
cd a3data-epidemiology-assistant

# 2) criar venv e instalar deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Criar .env

Crie um arquivo .env na raiz (ou duplique o .env.example):

OPENAI_API_KEY=sua_chave_aqui   # opcional (sem isso, vem resposta "Sem LLM configurado")
OPENAI_MODEL=gpt-4o-mini
PERSIST_DIR=artifacts/chroma
COLLECTION_NAME=eu_epi_2021


Importante: .env não deve ir para o git (já está ignorado no .gitignore).

📥 Ingestão (se for indexar PDFs)

Coloque os PDFs em data/.

Gere o arquivo documents.jsonl (chunks) e depois embeddings no Chroma:

# Gera o JSONL com chunks (ajuste tamanhos se quiser)
python src/ingestion.py `
  --data_dir data `
  --out_path artifacts/documents.jsonl `
  --chunk_size 1200 `
  --chunk_overlap 200

# Cria embeddings no ChromaDB
python src/embedding_pipeline.py `
  --jsonl_path artifacts/documents.jsonl `
  --persist_dir artifacts/chroma


Se você já tem artifacts/chroma pronto, não precisa rodar a ingestão.

▶️ Subir a API
uvicorn src.api:app --reload --port 8000
# Abra: http://127.0.0.1:8000/docs

🧪 Testes (prontos para colar)
1) Swagger UI (POST /ask)

Exemplo 1 — panorama TB:

{
  "question": "Qual foi o panorama da tuberculose em 2021 na UE/EEA? Resuma dados e tendências.",
  "k": 5
}


Exemplo 2 — doenças respiratórias monitoradas:

{
  "question": "Quais doenças respiratórias foram monitoradas em 2021?",
  "k": 5
}


Exemplo 3 — populações vulneráveis:

{
  "question": "Quais populações foram destacadas como mais vulneráveis às doenças respiratórias em 2021 e por quê?",
  "k": 6
}


Exemplo 4 — recomendações de vigilância:

{
  "question": "Quais foram as recomendações de vigilância para Zika em 2021?",
  "k": 5
}

2) PowerShell (sem Postman)
$payload = @{ question = "Qual foi o panorama da tuberculose em 2021 na UE/EEA?"; k = 5 } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/ask `
  -ContentType 'application/json; charset=utf-8' `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))

📌 Expectativa de resposta

Com chave OpenAI válida, a resposta vem sintetizada + “Fontes: arquivo#chunk…”

Sem chave, volta: “Sem LLM configurado. Trechos relevantes: …” + fontes
(útil para provar a recuperação de contexto mesmo sem LLM).

🗂️ Estrutura do projeto
a3data-epidemiology-assistant/
├─ data/                      # PDFs (local; não versionar)
├─ artifacts/
│  ├─ chroma/                 # banco vetorial (gerado)
│  └─ documents.jsonl         # saída de ingestão (gerado)
├─ src/
│  ├─ api.py                  # FastAPI (endpoint /ask)
│  ├─ rag_agent.py            # retrieve + generate (OpenAI opcional)
│  ├─ ingestion.py            # lê PDFs, limpa, chunca
│  └─ embedding_pipeline.py   # grava embeddings no Chroma
├─ .env                       # suas variáveis (NÃO commit)
├─ .env.example               # modelo seguro
├─ requirements.txt
├─ .gitignore
└─ README.md

🧰 Troubleshooting

PowerShell bloqueia Activate.ps1
Abra um novo terminal e rode:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1


Porta 8000 ocupada

netstat -aon | findstr :8000
taskkill /PID <PID> /F


ModuleNotFoundError: No module named 'rag_agent'
Execute a partir da raiz do projeto:

uvicorn src.api:app --reload --port 8000


Ou use esse launch.json no VS Code:

{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Uvicorn API",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.api:app", "--reload", "--port", "8000"],
      "justMyCode": true
    }
  ]
}


Chroma com erro em filtros
Use apenas query_texts + n_results (operadores permitidos: $gt, $gte, $lt, $lte, $ne, $eq, $in, $nin).

📣 Roteiro de demo (sugestões para o cliente)

Mostrar http://127.0.0.1:8000/docs e o endpoint /ask.

Enviar 2–3 perguntas de negócio (exemplos acima).

Mostrar as Fontes citadas (arquivo + chunk) — foco em auditoria e rastreabilidade.

Explicar que sem a chave OpenAI ainda é possível ver os trechos (validando o corpus).

Com a chave, a resposta vem sintetizada e pronta para executivo.

✅ Status

✅ Ingestão/embeddings funcionando (ChromaDB).

✅ API FastAPI operando (Swagger).

✅ Geração com OpenAI quando OPENAI_API_KEY está no .env.
