# 🌴 Mekong Voyager — Southeast Asia AI Travel Concierge

![Mekong Voyager Demo](mekong_voyager_demo.gif)

**Mekong Voyager** is an intelligent AI travel concierge designed for travelers exploring Vietnam and Southeast Asia. Powered by Google Cloud's Agent Development Kit (ADK) and Gemini models, Mekong Voyager delivers personalized destination recommendations, rich interactive UI cards, live weather updates, currency conversion, AI postcard image generation, and short AI travel video clips.

---

## 🌟 Core Features & Capabilities

- **🧠 Vertex AI Memory Bank Integration**: Preserves long-term user travel preferences, budget levels, and dietary needs across chat sessions.
- **🏛️ Firestore Destination Knowledge Base**:
  - `search_destinations`: Queries curated destination profiles across Vietnam, Thailand, Cambodia, and Laos in Google Cloud Firestore.
  - `get_destination_details`: Retrieves comprehensive attraction lists, best times to visit, local cuisine, and culture tips.
  - `add_destination`: Enables adding new Southeast Asian destinations to the Firestore registry.
- **🎨 AI Postcard Image Generation**:
  - `generate_destination_image`: Uses Google's `gemini-3.1-flash-lite-image` model to generate custom travel postcard imagery.
- **🎥 AI Short Video Clip Generation**:
  - `generate_destination_video`: Uses Google's `gemini-omni-flash-preview` model in the `global` region via Vertex AI Interactions API to generate 3-second motion travel clips.
- **☁️ Public Google Cloud Storage (GCS) Integration**:
  - Direct in-memory upload of generated images (`.jpg`) and videos (`.mp4`) to public GCS buckets, serving direct public HTTPS URLs.
- **🌦️ Live Utilities**:
  - `get_live_weather`: Fetches live weather conditions for cities across Southeast Asia.
  - `convert_currency`: Real-time exchange rate calculations (e.g. USD to VND, THB, KHR).
  - `get_current_time`: Local time lookup for Southeast Asian timezones.
- **📱 A2UI Rich Surface Renderer**:
  - Powered by `a2ui_callback` with `A2uiSchemaManager` (v0.8) and `BasicCatalog`.
  - Generates interactive, structured UI cards with image carousels, action buttons, and destination details.

---

## 🏗️ Architecture & Technology Stack

- **Agent Framework**: Google ADK (Agent Development Kit) with `LlmAgent` and `AgentEngineSandboxCodeExecutor`.
- **Primary LLM**: `gemini-2.5-flash`
- **Image & Video Models**: `gemini-3.1-flash-lite-image` and `gemini-omni-flash-preview` (global Vertex AI endpoint).
- **Backend Storage & Services**: Google Cloud Firestore, Google Cloud Storage, Vertex AI Memory Bank.
- **Frontend**: Custom FastAPI server with vanilla HTML5/CSS3/JavaScript chat UI, custom branding, and responsive dialogue layout.

---

## 📁 Repository Structure

```
mekong-voyager/
├── app/
│   ├── agent.py               # Main ADK root agent configuration & system prompt
│   ├── destination_tools.py   # Firestore search, details, and add destination tools
│   ├── image_tool.py          # Gemini image generation & GCS upload tool
│   ├── video_tool.py          # Gemini Omni video generation & GCS upload tool
│   ├── weather_tool.py        # Live weather lookup tool
│   ├── utility_tools.py       # Currency conversion & local time tools
│   └── a2ui_utils.py          # A2UI callback and schema manager setup
├── frontend/
│   ├── main.py                # FastAPI proxy server for Cloud Run / local execution
│   ├── requirements.txt       # Frontend dependencies
│   └── static/
│       └── index.html         # Custom branded chat UI layout & interactive prompt chips
├── mekong_voyager_demo.gif    # Animated demo recording of the agent in action
├── agents-cli-manifest.yaml   # AGY deployment manifest
├── deployment_metadata.json   # Deployment resource metadata
└── pyproject.toml             # Python project dependencies & environment
```

---

## 🛠️ Local Setup & Development

### Prerequisites
- Python 3.11+
- `uv` package manager (`pip install uv`)
- Google Cloud SDK (`gcloud`) authenticated to your GCP project

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run ADK Development Playground
Start the local ADK developer UI with Memory Bank support:
```bash
uv run adk web . --port 8000 --reload_agents
```

### 3. Run Custom Web Frontend Locally
Navigate to the `frontend/` directory and launch the FastAPI server:
```bash
cd frontend
uv run python main.py
```
Open a browser and navigate to the local port displayed in the console output to interact with Mekong Voyager.
