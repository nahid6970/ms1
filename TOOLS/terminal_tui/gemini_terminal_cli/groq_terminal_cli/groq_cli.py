#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import html
import json
import os
import platform
import re
import time
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

# (Import AES logic and core file/system utility functions from gemini_cli.py here...)
# To keep the response clean, I am focusing on the Groq-specific Client logic.

DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_SYSTEM = (
    "You are a terminal coding assistant using Groq. "
    "Be concise, practical, and ask before making destructive changes. "
    "For code work, inspect with run_powershell first. "
    "Prefer fuzzy_apply_patch for edits."
)

class GroqClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        messages: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Groq expects a system message at the start for instructions
        formatted_messages = []
        if system_instruction:
            formatted_messages.append({"role": "system", "content": system_instruction})
        formatted_messages.extend(messages)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Groq API Error: {raw}") from exc

    def list_models(self) -> List[str]:
        url = "https://api.groq.com/openai/v1/models"
        request = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            method="GET"
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return [m["id"] for m in data.get("data", []) if "llama" in m["id"] or "mixtral" in m["id"]]

# Note: The Tool Loop in main() needs to handle the OpenAI 'tool_calls' structure:
# 1. response['choices'][0]['message'].get('tool_calls')
# 2. Results must be returned as messages with role: 'tool' and tool_call_id matching.

# (Rest of main loop logic adapted for the OpenAI/Groq message list format...)
