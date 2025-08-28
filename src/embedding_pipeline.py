import argparse, os, json
from typing import List
import chromadb # type: ignore
from chromadb.utils import embedding_functions # type: ignore

def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def get_embedding_fn():
    # Default: sentence-transformers local
    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

def main(jsonl_path: str, persist_dir: str, collection_name: str = "eu_epi_2021"):
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    emb_fn = get_embedding_fn()
    coll = client.get_or_create_collection(name=collection_name, embedding_function=emb_fn)

    ids, docs, metas = [], [], []
    for rec in load_jsonl(jsonl_path):
        ids.append(rec["id"])
        docs.append(rec["text"])
        metas.append({"source": rec.get("source"), "filename": rec.get("metadata", {}).get("filename"), "page_hint": rec.get("page_hint")})
        if len(ids) >= 512:
            coll.add(ids=ids, documents=docs, metadatas=metas)
            ids, docs, metas = [], [], []
    if ids:
        coll.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Indexação concluída em {persist_dir} / coleção {collection_name}. Itens: {coll.count()}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--jsonl_path", required=True)
    p.add_argument("--persist_dir", required=True)
    p.add_argument("--collection_name", default="eu_epi_2021")
    a = p.parse_args()
    main(a.jsonl_path, a.persist_dir, a.collection_name)
