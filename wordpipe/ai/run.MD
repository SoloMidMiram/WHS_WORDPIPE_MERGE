# Canary test (checks key, connectivity)
python wordpipe/ai/one_openai_api.py canary

# Simple text
python wordpipe/ai/one_openai_api.py text --prompt "Summarize attention in transformers"

# Streaming (will print token deltas)
python wordpipe/ai/one_openai_api.py stream --prompt "Write two haiku about debugging"

# Structured JSON
python wordpipe/ai/one_openai_api.py structured --prompt "Recommend one 1990s sci-fi movie with 2 reasons"

# Tools demo
python wordpipe/ai/one_openai_api.py tools --prompt "Compute the hypotenuse for legs 5 and 12"
    