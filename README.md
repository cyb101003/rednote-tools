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
  Includes a modern web UI for quick testing and visualisation.

  ## 🌍 Global Potential

RealSkill currently targets Chinese platforms, but its architecture is **language-agnostic**:

- **Multi-language ready**: Replace prompt templates with any language — English, Japanese, Korean — and the same multi-agent pipeline works immediately.
- **Standard Skill interface**: Any AI agent worldwide can discover and call RealSkill via `/.well-known/skill.json`.
- **Platform-extensible**: Add support for Twitter, Instagram, LinkedIn by adding new prompt templates and seed data — no core code changes needed.

## 🧠 How it works


User provides a topic and target platform.

The system retrieves similar viral posts from the vector DB (and live Xiaohongshu if applicable).

Three agents generate distinct versions simultaneously.

A judge agent scores them on "human-like", "platform fit", and "viral potential".

The winning copy is polished with LLM humanization and rule-based perturbations.

The final text is returned along with scores and the raw outputs of all agents.

## 🌐 Live Demo

RealSkill is deployed and accessible online:

👉 **[https://realskill.asia](https://realskill.asia)**

You can generate copy directly in your browser — no installation needed.

API endpoint: `https://realskill.asia/generate`  
Skill discovery: `https://realskill.asia/.well-known/skill.json`  
Swagger docs: `https://realskill.asia/docs`

## 📦 Use as an Agent Skill (ZIP)

RealSkill can also run locally inside any agent that supports Python functions.  
No server, no API calls — just drop the ZIP into your agent's skill folder.

1. Download `RealSkill_agent.zip` from the [Releases](https://github.com/cyb101003/rednote-tools/releases) page (or generate it with `python build_skill_zip.py`).
2. Extract the ZIP into your agent's `skills/` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements_skill.txt
   playwright install chromium
Create a .env file with your DeepSeek API key:

text
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
Build the vector index:

bash
python build_index.py
Your agent can now call from skill_entry import generate and use the Skill locally.

🗂 Project Structure
text
rednote-tools/
├── main.py                # FastAPI server & Skill endpoints
├── app.py                 # Streamlit demo UI
├── skill_manifest.py      # Skill definition (OpenAI function format)
├── build_skill_zip.py     # Script to create the Agent Skill ZIP
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
🚀 Quick Start (Local)
1. Clone & set up environment
bash
git clone https://github.com/cyb101003/rednote-tools.git
cd rednote-tools
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
2. Configure API keys
Create .env from the example:

bash
cp .env.example .env
Edit .env with your DeepSeek credentials:

text
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
3. Build the vector index
bash
python build_index.py
4. Start the backend
bash
uvicorn main:app --reload
The API is now running at http://localhost:8000.
Swagger UI: http://localhost:8000/docs

5. (Optional) Launch the demo UI
Open a new terminal:

bash
streamlit run app.py
Then visit http://localhost:8501.

🔌 API Usage
Generate copy
bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"weekend trip ideas","platform":"xiaohongshu"}'
Response includes the final text, winner agent, scores, and all variants.

Skill discovery (for AI agents)
bash
curl http://localhost:8000/.well-known/skill.json
🐳 Docker Deployment
bash
docker build -t realskill .
docker run -d -p 8000:8000 -e OPENAI_API_KEY=your_key -e OPENAI_BASE_URL=... realskill
📄 License
MIT – feel free to use, extend, or integrate into your own agents.

## 💼 Monetization Roadmap

RealSkill addresses a real pain point for millions of content creators. Potential monetization paths:

| Stage | Model | Description |
|-------|-------|-------------|
| **Phase 1** | Freemium API | Free tier (10 generations/day), paid tier ($9.99/month for unlimited) |
| **Phase 2** | Enterprise SaaS | Customized copywriting engine for MCN agencies and brands |
| **Phase 3** | Platform Integration | One-click publish to Xiaohongshu/Zhihu via platform APIs |


Built for the UCWS Hackathon — Skill Track.
