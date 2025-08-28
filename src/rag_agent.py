import os
from pathlib import Path
from typing import Dict, List, Any

import chromadb  # type: ignore
from chromadb.utils import embedding_functions  # type: ignore

# Carrega variáveis do .env a partir da RAIZ do projeto (…\a3data-epidemiology-assistant\.env)
from dotenv import load_dotenv  # type: ignore
ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
load_dotenv(dotenv_path=str(ENV_PATH), override=True)

try:
    # SDK OpenAI v1.x
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

SYSTEM_PROMPT = (
    "Você é um assistente para relatórios epidemiológicos da União Europeia (2021). "
    "Responda APENAS com base nos trechos fornecidos. "
    "Cite as fontes (arquivo e chunk) no final. Se não souber, diga que não sabe."
)


class RagAgent:
    def __init__(self, persist_dir: str | None = None, collection_name: str | None = None):
        persist_dir = persist_dir or os.getenv("PERSIST_DIR", "artifacts/chroma")
        collection_name = collection_name or os.getenv("COLLECTION_NAME", "eu_epi_2021")

        # Vector store (Chroma)
        self.client = chromadb.PersistentClient(path=persist_dir)
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        self.coll = self.client.get_or_create_collection(name=collection_name, embedding_function=self.emb_fn)

        # OpenAI (opcional). Só ativa se houver chave E o SDK estiver instalado.
        self.use_openai = bool(os.getenv("OPENAI_API_KEY"))
        if self.use_openai and OpenAI:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            self.openai_client = None
            self.openai_model = None

        # Filtro de arquivos respiratórios (ajuste termos conforme os PDFs da pasta data/)
        self.respiratory_where = {
            "$or": [
                {"filename": {"$contains": "tuberculosis"}},
                {"filename": {"$contains": "influenza"}},
                {"filename": {"$contains": "pertussis"}},      # coqueluche
                {"filename": {"$contains": "legion"}},         # legionelose
                {"filename": {"$contains": "covid"}},
                {"filename": {"$contains": "respir"}},         # respirat/respiratórias
            ]
        }

    def retrieve(self, question: str, k: int = 5, only_respiratory: bool = False):
        kwargs = {"query_texts": [question], "n_results": k}
        # por enquanto NÃO use where com $contains
        # if only_respiratory:
        #     kwargs["where"] = {"respiratory": True}
        return self.coll.query(**kwargs)


    def generate(self, question: str, contexts: List[str], metadatas: List[Dict]) -> str:
        context_block = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(contexts)])
        sources_block = "; ".join([f"{m.get('filename','?')}#chunk{idx+1}" for idx, m in enumerate(metadatas)])

        if self.openai_client:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Pergunta: {question}\n\n"
                        f"Contexto:\n{context_block}\n\n"
                        "Responda em no máximo 200-250 palavras, objetivo e com referências."
                    ),
                },
            ]
            resp = self.openai_client.chat.completions.create(
                model=self.openai_model or "gpt-4o-mini",
                messages=messages,
                temperature=0.2,
            )
            answer = resp.choices[0].message.content.strip()
            return f"{answer}\n\n**Fontes:** {sources_block}"

        # Fallback sem LLM
        return f"Sem LLM configurado. Trechos relevantes:\n\n{context_block}\n\n**Fontes:** {sources_block}"

    def ask(self, question: str, k: int = 5, only_respiratory = False) -> Dict[str, Any]:
        res = self.retrieve(question, k=k, only_respiratory=only_respiratory)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        answer = self.generate(question, docs, metas)
        return {"answer": answer, "sources": metas}


if __name__ == "__main__":
    agent = RagAgent()
    print(agent.ask("Quais foram as principais doenças respiratórias monitoradas em 2021?", k=8)["answer"])
