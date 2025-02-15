# Zippy's Archon

This is a fork of Cole Medin's Archon, branded and maintained by **Zippy**.

It supports:
- **Multi-agent workflow** with Pydantic AI and LangGraph
- **Diagnostic Agent** for error handling
- **Tool Generator Sub-Agent** for plugin creation
- **Concurrency** via session IDs (multiple orchestrators in memory)
- **Streamlit** UI for chat
- **FastAPI** endpoints for external integrations (n8n, etc.)

## Setup

1. **Clone** this repository.
2. **Install** dependencies:
   ```bash
   cd zippy-archon
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
3. **Copy** .env.example to .env and fill in your API keys and model preferences

### Running the System
- FastAPI server for concurrency and external calls:

```bash

uvicorn archon_server:app --host 0.0.0.0 --port 8080
```

This exposes ```/start_flow``` and ```/resume_flow```.

- Streamlit UI for local chat:

```bash
streamlit run streamlit_ui.py
```

### Using the Plugins
- The system writes newly generated plugins to plugins/.
- The plugin_manager.py automatically loads them on load_plugins("plugins").
  
### License
See LICENSE for details. We keep the original license from Archon and include any modifications under the same terms.

vbnet

---

## 11. `zippy-archon/LICENSE`

```text
MIT License

Copyright (c) [2025] [Eric Henderson, aka "Zippy" of Zippy Technologies LLC]

Original Archon code by Cole Medin, licensed under MIT as well.

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge, 
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons 
to whom the Software is furnished to do so, subject to the following conditions:

[Full MIT text goes here, unmodified from original Archon license plus your disclaimers...]
