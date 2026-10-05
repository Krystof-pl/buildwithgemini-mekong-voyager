# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.genai import types

from .a2ui_utils import a2ui_callback
from .currency_tool import convert_currency
from .firestore_tools import (
    add_destination,
    get_destination_details,
    search_destinations,
)
from .image_tool import generate_destination_image
from .video_tool import generate_destination_video
from .weather_tool import get_live_weather

# Load deployment metadata for Agent Engine sandbox code execution and memory bank
deployment_metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
remote_agent_runtime_id = "projects/1016024720907/locations/us-east1/reasoningEngines/6932676999336951808"
sandbox_resource_name = None

if deployment_metadata_path.exists():
    try:
        with open(deployment_metadata_path) as f:
            meta = json.load(f)
            remote_agent_runtime_id = meta.get("remote_agent_runtime_id", remote_agent_runtime_id)
            sandbox_resource_name = meta.get("sandbox_resource_name")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=sandbox_resource_name,
    agent_engine_resource_name=remote_agent_runtime_id if not sandbox_resource_name else None,
)

# Configure Vertex AI Memory Bank Service for Agent Engine redeployments
agent_engine_id = remote_agent_runtime_id.split("/")[-1]
memory_service = VertexAiMemoryBankService(
    project="qwiklabs-gcp-03-49140da9fb98",
    location="us-east1",
    agent_engine_id=agent_engine_id,
)

# Build A2UI system prompt using A2uiSchemaManager v0.8
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Mekong Voyager, an expert travel concierge specializing in Vietnam and Southeast Asia. "
        "You help travelers discover unforgettable destinations, check live weather (get_live_weather), calculate currency "
        "conversions (convert_currency), generate scenic travel postcards and images (generate_destination_image), generate "
        "short travel video clips (generate_destination_video), and query "
        "or add destinations using your Firestore database tools (search_destinations, get_destination_details, add_destination)."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


def get_current_time(query: str) -> str:
    """Gets the current local time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        Current time string.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    elif any(city in query.lower() for city in ["hanoi", "ho chi minh", "hoi an", "bangkok", "phnom penh"]):
        tz_identifier = "Asia/Bangkok"
    else:
        tz_identifier = "UTC"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time in {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    after_model_callback=a2ui_callback,
    tools=[
        get_live_weather,
        get_current_time,
        convert_currency,
        generate_destination_image,
        generate_destination_video,
        search_destinations,
        get_destination_details,
        add_destination,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
