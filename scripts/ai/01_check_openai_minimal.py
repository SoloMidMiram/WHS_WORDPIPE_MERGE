# 01_check_openai_minimal.py
import os
from openai import OpenAI

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def main():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("Set OPENAI_API_KEY in your env.")
        return
    client = OpenAI(api_key=key)
    # one sentence, coherent prompt
    prompt = "In one short sentence, explain why clean code matters."
    r = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), input=prompt, temperature=0.2
    )
    print("OK:", r.output_text.strip())
    u = getattr(r, "usage", None)
    if u:
        print(
            f"usage: in={getattr(u, 'input_tokens', 0)} out={getattr(u, 'output_tokens', 0)}"
        )


if __name__ == "__main__":
    main()
