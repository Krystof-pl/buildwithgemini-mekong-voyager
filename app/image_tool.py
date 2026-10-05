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

"""Image generation tool for Mekong Voyager using gemini-3.1-flash-lite-image model."""

import uuid
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-03-49140da9fb98"
BUCKET_NAME = "mekong-voyager-assets-qwiklabs-gcp-03-49140da9fb98"


def generate_destination_image(
    prompt: str,
    destination_name: str = "destination",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Generate a scenic travel postcard image for a destination in Vietnam or Southeast Asia using gemini-3.1-flash-lite-image.

    Args:
        prompt: Detailed image prompt describing the scene (e.g. 'A scenic travel postcard of Ha Long Bay limestone karsts at sunset').
        destination_name: Optional destination name or title (e.g. 'ha-long-bay', 'hoi-an', 'sapa').
        tool_context: ADK ToolContext passed automatically by the framework to record artifacts in Playground.

    Returns:
        A dictionary containing the public Cloud Storage image URL, image filename, and prompt details.
    """
    try:
        # Step 1: Initialize Vertex AI client with global region for gemini-3.1-flash-lite-image
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        # Step 2: Generate image using gemini-3.1-flash-lite-image model
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return {"error": "Failed to extract generated image bytes from response."}

        clean_dest = destination_name.lower().replace(" ", "-").strip() or "postcard"
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{clean_dest}_{unique_id}.jpg"

        # Action 1: Save image with tool_context.save_artifact for ADK Playground Artifacts panel
        if tool_context is not None:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            tool_context.save_artifact(
                filename=filename,
                artifact=image_part,
                custom_metadata={"prompt": prompt, "destination": destination_name},
            )

        # Action 2: Upload image bytes directly to Cloud Storage bucket and return public URL
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/jpeg")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "image_url": public_url,
            "filename": filename,
            "prompt": prompt,
            "formatted_result": f"Generated image for '{destination_name}' successfully. Public URL: {public_url}",
        }
    except Exception as exc:
        return {"error": f"Failed to generate destination image: {str(exc)}"}
