import requests


OLLAMA_URL = "http://10.0.2.2:11434"
OLLAMA_MODEL = "gemma3:1b"


def generate_response(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]
    
#if __name__ == "__main__":
 #   answer = generate_response(
  #      "What is a government scholarship? Explain in two sentences."
   # )
#
    #print(answer)
