# RealSkill — Humanized Social Copy Engine

RealSkill is a multi-agent AI Skill that generates authentic, platform-native copy for Xiaohongshu, Zhihu, and Weibo.  
It reduces AI detection scores and mimics genuine user-generated content, helping creators avoid shadowbanning and traffic loss.

> ⚡ Built as a standard Agent Skill – any agent (OpenClaw, Codex, LangChain) can discover and call it via OpenAPI/Function Calling conventions.

## ✨ Features

- **Multi-Agent Collaboration**  
  Three writing agents (viral curator / real-life sharer / rational author) compete on the same topic, then a judge agent picks the best one.
- **Platform-Specific Styles**  
  Emulates native tone for Xiaohongshu (emoji-heavy, short sentences), Zhihu (structured, logical), and Weibo (casual, emotional).
- **AI Trace Reduction**  
  Combines LLM humanization with rule-based post-processing (typos, pauses, grammar imperfections) to lower detection scores.
- **Live Data Enrichment (RAG)**  
  Fetches real Xiaohongshu trending content in real time and searches a local vector database of proven viral posts to guide generation.
- **Standard Skill Interface**  
  Exposes `POST /generate` and `GET /.well-known/skill.json`, making it directly callable by any agent supporting OpenAI function calling.
- **Beautiful Streamlit Demo**  
  Includes a modern UI for quick testing and visualisation.

## 🧠 How it works

1. User provides a topic and target platform.
2. The system retrieves similar viral posts from the vector DB (and live Xiaohongshu if applicable).
3. Three agents generate distinct versions simultaneously.
4. A judge agent scores them on "human-like", "platform fit", and "viral potential".
5. The winning copy is polished with LLM humanization and rule-based perturbations.
6. The final text is returned along with scores and the raw outputs of all agents.

## 🗂 Project Structure

rednote-tools/
├── main.py                # FastAPI server & Skill endpoints
├── app.py                 # Streamlit demo UI
├── skill_manifest.py      # Skill definition (OpenAI function format)
├── build_index.py         # ChromaDB vector index builder
├── core/                  # Core logic
│   ├── generator.py       # RAG + multi-agent generation
│   ├── judge.py           # Scoring & AI detection
│   └── humanize.py        # LLM + rule-based post-processing
├── agents/
│   └── prompts.py         # Prompt templates for all agents
├── collectors/
│   └── xiaohongshu.py     # Playwright-based live scraper
├── data/
│   └── seed_data.py       # Built-in viral samples
├── requirements.txt
├── Dockerfile
└── .env.example

## 🚀 Quick Start

### 1. Clone & set up environment

```bash
git clone https://github.com/cyb101003/rednote-tools.git
cd rednote-tools
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

2. Configure API keys

Create .env from the example:

```bash
cp .env.example .env
```

Edit .env with your DeepSeek credentials:

```
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

3. Build the vector index

```bash
python build_index.py
```

4. Start the backend

```bash
uvicorn main:app --reload
```

The API is now running at http://localhost:8000.
Swagger UI: http://localhost:8000/docs

5. (Optional) Launch the demo UI

Open a new terminal:

```bash
streamlit run app.py
```

Then visit http://localhost:8501.

🔌 API Usage

Generate copy

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"weekend trip ideas","platform":"xiaohongshu"}'
```

Response includes the final text, winner agent, scores, and all variants.

Skill discovery (for AI agents)

```bash
curl http://localhost:8000/.well-known/skill.json
```

🐳 Docker Deployment

```bash
docker build -t realskill .
docker run -d -p 8000:8000 -e OPENAI_API_KEY=your_key -e OPENAI_BASE_URL=... realskill
```

📄 License

MIT – feel free to use, extend, or integrate into your own agents.

---

Built for the UCWS Hackathon
