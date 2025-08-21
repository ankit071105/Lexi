def chunk_text(text, chunk_size=500):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
