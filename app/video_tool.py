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

"""Video generation tool for Mekong Voyager using gemini-omni-flash-preview model."""

import base64
import uuid
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-03-49140da9fb98"
BUCKET_NAME = "mekong-voyager-assets-qwiklabs-gcp-03-49140da9fb98"


def generate_destination_video(
    prompt: str,
    destination_name: str = "destination",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Generate a scenic travel video clip for a destination in Vietnam or Southeast Asia using gemini-omni-flash-preview.

    Args:
        prompt: Detailed video prompt describing the scene (e.g. 'A scenic 5-second video clip of Ha Long Bay karsts at sunset').
        destination_name: Optional destination name or title (e.g. 'ha-long-bay', 'hoi-an', 'mekong-delta').
        tool_context: ADK ToolContext passed automatically by the framework to record artifacts in Playground.

    Returns:
        A dictionary containing the public Cloud Storage video URL, video filename, and prompt details.
    """
    try:
        # Step 1: Initialize Vertex AI client with global region for gemini-omni-flash-preview
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        # Step 2: Generate video using gemini-omni-flash-preview via Interactions API
        response = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        if not response.output_video or not response.output_video.data:
            return {"error": "Failed to extract generated video bytes from response."}

        raw_data = response.output_video.data
        if isinstance(raw_data, bytes):
            video_bytes = raw_data
        elif isinstance(raw_data, str):
            try:
                video_bytes = base64.b64decode(raw_data)
            except Exception:
                video_bytes = raw_data.encode("utf-8")
        else:
            return {"error": "Unexpected video data format."}

        clean_dest = destination_name.lower().replace(" ", "-").strip() or "video"
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{clean_dest}_{unique_id}.mp4"

        # Action 1: Save video with tool_context.save_artifact for ADK Playground Artifacts panel
        if tool_context is not None:
            video_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
            tool_context.save_artifact(
                filename=filename,
                artifact=video_part,
                custom_metadata={"prompt": prompt, "destination": destination_name},
            )

        # Action 2: Upload video bytes directly to Cloud Storage bucket and return public URL
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "video_url": public_url,
            "filename": filename,
            "prompt": prompt,
            "formatted_result": f"Generated video for '{destination_name}' successfully. Public URL: {public_url}",
        }
    except Exception as exc:
        return {"error": f"Failed to generate destination video: {str(exc)}"}
