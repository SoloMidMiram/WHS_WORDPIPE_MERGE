# Manual AI scripts (moved to scripts/ai/)

These commands previously referenced `wordpipe/ai/`. Use `scripts/ai/` instead.

```powershell
# Canary test (checks key, connectivity)
python scripts/ai/one_openai_api.py canary

# Simple text
python scripts/ai/one_openai_api.py text --prompt "Summarize attention in transformers"

# Streaming (will print token deltas)
python scripts/ai/one_openai_api.py stream --prompt "Write two haiku about debugging"

# Structured JSON
python scripts/ai/one_openai_api.py structured --prompt "Recommend one 1990s sci-fi movie with 2 reasons"

# Tools demo
python scripts/ai/one_openai_api.py tools --prompt "Compute the hypotenuse for legs 5 and 12"
```

For runtime library usage, see `wordpipe.interfaces.ai` and `wordpipe.adapters.ai`.
