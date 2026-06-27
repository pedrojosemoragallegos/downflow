from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## INLINE-LEAF HANDLER
class LeafInline(Handler): ...


## Code Span Handler
@final
class CodeSpan(LeafInline):
    def handle(self, cursor: Cursor, engine: Engine) -> Self:
        if cursor.current_char() == "`":
            cursor.advance()
            code_content = ""
            while cursor.current_char() != "`" and not cursor.is_at_end():
                code_content += cursor.current_char()
                cursor.advance()
            if cursor.current_char() == "`":
                cursor.advance()
                engine.add_action(Action("code_span", code_content))
        return self


## Autolink Handler
@final
class AutoLink(LeafInline):
    def handle(self, cursor: Cursor, engine: Engine) -> Self:
        if cursor.current_char() == "<":
            cursor.advance()
            link_content = ""
            while cursor.current_char() != ">" and not cursor.is_at_end():
                link_content += cursor.current_char()
                cursor.advance()
            if cursor.current_char() == ">":
                cursor.advance()
                engine.add_action(Action("autolink", link_content))
        return self


## Raw HTML Handler
@final
class RawHTML(LeafInline):
    def handle(self, cursor: Cursor, engine: Engine) -> Self:
        if cursor.current_char() == "<":
            cursor.advance()
            html_content = ""
            while cursor.current_char() != ">" and not cursor.is_at_end():
                html_content += cursor.current_char()
                cursor.advance()
            if cursor.current_char() == ">":
                cursor.advance()
                engine.add_action(Action("raw_html", html_content))
        return self


## Hardline Break Handler
@final
class HardlineBreak(LeafInline):
    def handle(self, cursor: Cursor, engine: Engine) -> Self:
        if cursor.current_char() == "\\":
            cursor.advance()
            if cursor.current_char() == "\n":
                cursor.advance()
                engine.add_action(Action("hardline_break"))
        return self


## Softline Break Handler
@final
class SoftlineBreak(LeafInline):
    def handle(self, cursor: Cursor, engine: Engine) -> Self:
        if cursor.current_char() == "\n":
            cursor.advance()
            engine.add_action(Action("softline_break"))
        return self


## Textual Content Handler
@final
class Text(LeafInline):
    def handle(self, cursor: Cursor, engine: Engine) -> Self:
        text_content = ""
        while not cursor.is_at_end() and cursor.current_char() not in [
            "`",
            "<",
            "\\",
            "\n",
        ]:
            text_content += cursor.current_char()
            cursor.advance()
        if text_content:
            engine.add_action(Action("text", text_content))
        return self
