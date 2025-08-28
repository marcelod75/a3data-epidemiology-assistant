import argparse, os, json, re
from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader # type: ignore

def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for i, page in enumerate(reader.pages):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        if t:
            texts.append(t)
    return "\n".join(texts)

def clean_text(t: str) -> str:
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def chunk_text(text: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> List[str]:
    tokens = list(text)
    chunks = []
    start = 0
    n = len(tokens)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = "".join(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - chunk_overlap
        if start < 0:
            start = 0
    return chunks

def main(data_dir: str, out_path: str, chunk_size: int, chunk_overlap: int):
    data_dir = Path(data_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc_id = 0
    with out_path.open("w", encoding="utf-8") as f:
        for pdf in sorted(data_dir.glob("**/*.pdf")):
            full_text = clean_text(read_pdf(str(pdf)))
            if not full_text:
                continue
            chunks = chunk_text(full_text, chunk_size, chunk_overlap)
            for i, ch in enumerate(chunks):
                rec = {
                    "id": f"{pdf.stem}-{i}",
                    "source": str(pdf),
                    "page_hint": i,  # chunk-id: apenas uma dica
                    "text": ch,
                    "metadata": {"filename": pdf.name}
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                doc_id += 1
    print(f"Escrito {doc_id} chunks em {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True)
    parser.add_argument("--out_path", required=True)
    parser.add_argument("--chunk_size", type=int, default=1200)
    parser.add_argument("--chunk_overlap", type=int, default=200)
    args = parser.parse_args()
    main(args.data_dir, args.out_path, args.chunk_size, args.chunk_overlap)
