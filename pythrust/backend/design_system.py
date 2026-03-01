import json
import os
from functools import lru_cache
from typing import Any, Dict, Set


@lru_cache(maxsize=1)
def load_design_tokens() -> Dict[str, Any]:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    token_path = os.path.join(base_dir, "design-system", "design-tokens.json")
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Design token file not found at: {token_path}")
    with open(token_path, "r", encoding="utf-8") as f:
        return json.load(f)


def design_token_version() -> str:
    tokens = load_design_tokens()
    return tokens.get("version", "v1")


def flatten_allowed_values() -> Set[str]:
    tokens = load_design_tokens()
    allowed: Set[str] = set()

    def _walk(node: Any):
        if isinstance(node, dict):
            for value in node.values():
                _walk(value)
        elif isinstance(node, list):
            for value in node:
                _walk(value)
        elif isinstance(node, str):
            allowed.add(node.strip().lower())

    _walk(tokens)
    return allowed


def allowed_colors() -> Set[str]:
    tokens = load_design_tokens()
    colors = tokens.get("colors", {})
    return {str(v).lower() for v in colors.values()}
