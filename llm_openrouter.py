import requests

OPENROUTER_API_KEY = "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"
MODEL = "deepseek/deepseek-r1:free"  

def generate_answer(question, chunks):
    messages = [
        {"role": "system", "content": "You are an expert insurance claims evaluator. Provide structured JSON answers."},
        {"role": "user", "content": f"""
Given this context and user question, answer strictly in JSON:

{{ 
  "decision": "Approved"|"Rejected"|"Insufficient Information",
  "amount": "INR value or N/A",
  "justification": "Short explanation referencing clauses",
  "referenced_clauses": ["clause excerpt 1", "clause excerpt 2"]
}}

Context:
{chr(10).join(chunks)}

Question:
{question}
"""}
    ]

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024
        }
    )

    try:
        result = response.json()
        if "choices" not in result:
            return {"error": result.get("error", "No 'choices' returned"), "full_response": result}

        return {"context_used": chunks, "answer": result['choices'][0]['message']['content'].strip(), "model": MODEL}
    except Exception as e:
        return {"error": str(e), "raw_response": response.text}
