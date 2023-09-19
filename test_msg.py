"""Send a test message."""
import argparse
import json

import requests

from fastchat.model.model_adapter import get_conversation_template




import argparse
import json

import requests
import os, json, sys, time, re, math, random, datetime, argparse, requests
from typing import List, Dict, Any

from fastchat.model.model_adapter import get_conversation_template


class FastChatAgent:

    def __init__(self, model_name, controller_address, temperature=0, max_new_tokens=32) -> None:
        self.model_name = model_name
        self.controller_address = controller_address
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens

    def inference(self, history: List[dict]) -> str:
        controller_addr = self.controller_address
        conv = get_conversation_template(self.model_name)
        for history_item in history:
            role = history_item["role"]
            content = history_item["content"]
            if role == "user":
                conv.append_message(conv.roles[0], content)
            elif role == "agent":
                conv.append_message(conv.roles[1], content)
            else:
                raise ValueError(f"Unknown role: {role}")
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()
        headers = {"User-Agent": "FastChat Client"}
        gen_params = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_new_tokens": self.max_new_tokens,
            "stop": conv.stop_str,
            "stop_token_ids": conv.stop_token_ids,
            "echo": False,
            "top_p": 0
        }
        response = requests.post(
            controller_addr + "/worker_generate_stream",
            headers=headers,
            json=gen_params,
            stream=True
        )
        text = ""
        for line in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if line:
                text = json.loads(line)["text"]
        return text

def handler(idx):
    response = agent.inference([
        {"role": "user", "content": "What's your name?"},
        {"role": "agent", "content": "Alice. How about you?"},
        {"role": "user", "content": "I'm Bob. Please tell me a story about how to make friends. More detailed."},
    ])
    print("\n\n== %d ==\n\n\n%s\n\n\n==   ==\n\n" % (idx, response))

if __name__ == '__main__':
    agent = FastChatAgent(model_name="openchat", controller_address='http://localhost:10010', temperature=0, max_new_tokens=1024)
    from concurrent.futures import ThreadPoolExecutor
    
    t = ThreadPoolExecutor(max_workers=5)
    for i in range(5):
        t.submit(handler, i)

