"""Simple Template Engine (clean version)

This is a minimal, safe implementation that supports:
- Registering templates with variables
- Rendering with {{var}} replacements
- Basic helpers: upper, lower, title
It intentionally avoids advanced parsing to keep it robust.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TemplateType(Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"


class ContentFormat(Enum):
    HTML = "html"
    TEXT = "text"
    MARKDOWN = "markdown"


@dataclass
class TemplateVariable:
    name: str
    type: str
    required: bool = True
    default_value: Any = None
    description: str = ""


@dataclass
class MessageTemplate:
    id: str
    name: str
    type: TemplateType
    format: ContentFormat
    content: str
    subject: Optional[str] = None
    variables: List[TemplateVariable] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TemplateEngine:
    def __init__(self) -> None:
        self.templates: Dict[str, MessageTemplate] = {}
        self.helpers = {
            "upper": lambda x: str(x).upper(),
            "lower": lambda x: str(x).lower(),
            "title": lambda x: str(x).title(),
            "escape_html": html.escape,
        }

    def register_template(self, template: MessageTemplate) -> None:
        self.templates[template.id] = template

    def render_template(self, template_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        tpl = self.templates.get(template_id)
        if not tpl:
            return {"success": False, "error": f"Template {template_id} not found"}

        # Validate required vars
        missing = [v.name for v in tpl.variables if v.required and v.name not in variables]
        if missing:
            return {"success": False, "error": f"Missing variables: {missing}"}

        # Merge defaults
        ctx = {v.name: v.default_value for v in tpl.variables if v.default_value is not None}
        ctx.update(variables)
        ctx.update(self.helpers)

        # Subject
        subject = self._render_content(tpl.subject, ctx) if tpl.subject else None
        content = self._render_content(tpl.content, ctx)
        return {
            "success": True,
            "template_id": tpl.id,
            "template_name": tpl.name,
            "type": tpl.type.value,
            "format": tpl.format.value,
            "subject": subject,
            "content": content,
            "rendered_at": datetime.now().isoformat(),
        }

    def _render_content(self, content: Optional[str], ctx: Dict[str, Any]) -> Optional[str]:
        if content is None:
            return None

        def replace_var(match: re.Match) -> str:
            expr = match.group(1).strip()
            # Helper call: {{ upper name }}
            parts = expr.split(" ", 1)
            if len(parts) == 2 and parts[0] in self.helpers:
                func = self.helpers[parts[0]]
                arg = parts[1]
                val = ctx.get(arg, arg)
                try:
                    return str(func(val))
                except Exception:
                    return str(val)
            # Plain variable
            return str(ctx.get(expr, f"{{{{{expr}}}}}"))

        return re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace_var, content)


def create_template_engine() -> TemplateEngine:
    return TemplateEngine()
