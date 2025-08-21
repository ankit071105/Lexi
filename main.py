from fastapi import FastAPI, UploadFile, File
from utils.parser import extract_text
from utils.chunker import chunk_text
from utils.embedder import embed_and_store, query_top_chunks
from utils.llm_openrouter import generate_answer

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text(file.filename, content)
    chunks = chunk_text(text)
    embed_and_store(chunks, file.filename)
    return {"status": f"Stored {len(chunks)} chunks from {file.filename}"}

@app.post("/query")
async def query(question: str):
    try:
        from utils.embedder import query_top_chunks
        from utils.llm_openrouter import generate_answer

        top_chunks = query_top_chunks(question)
        if not top_chunks:
            return {"error": "No relevant content found in uploaded documents."}

        response = generate_answer(question, top_chunks)
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
