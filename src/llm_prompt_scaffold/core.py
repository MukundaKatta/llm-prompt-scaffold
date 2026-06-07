"""Build structured multi-section LLM prompts from typed components.

:class:`PromptScaffold` assembles a prompt from named sections
(:class:`PromptSection`).  Sections are rendered in a canonical order
separated by blank lines, or exported as an Anthropic/OpenAI-compatible
``messages`` list.

Example::

    from llm_prompt_scaffold import PromptScaffold, PromptSection

    scaffold = PromptScaffold()
    scaffold.set(PromptSection.SYSTEM, "You are a helpful assistant.")
    scaffold.set(PromptSection.CONTEXT, "The user is onboarding.")
    scaffold.set(PromptSection.INSTRUCTION, "Greet the user warmly.")
    scaffold.set(PromptSection.OUTPUT_FORMAT, "One sentence only.")

    print(scaffold.render())
    # You are a helpful assistant.
    #
    # The user is onboarding.
    #
    # Greet the user warmly.
    #
    # One sentence only.

    msgs = scaffold.render_messages()
    # [{"role": "system", "content": "..."},
    #  {"role": "user", "content": "..."}]
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class PromptSection(str, Enum):
    """Typed sections of a structured LLM prompt.

    Rendering order (canonical): SYSTEM, PERSONA, CONTEXT, EXAMPLES,
    CONSTRAINTS, INSTRUCTION, OUTPUT_FORMAT.
    """

    SYSTEM = "system"
    PERSONA = "persona"
    CONTEXT = "context"
    EXAMPLES = "examples"
    CONSTRAINTS = "constraints"
    INSTRUCTION = "instruction"
    OUTPUT_FORMAT = "output_format"


# Canonical display order for rendering
_RENDER_ORDER: list[PromptSection] = [
    PromptSection.SYSTEM,
    PromptSection.PERSONA,
    PromptSection.CONTEXT,
    PromptSection.EXAMPLES,
    PromptSection.CONSTRAINTS,
    PromptSection.INSTRUCTION,
    PromptSection.OUTPUT_FORMAT,
]

# Sections that go into the system message when rendering as messages
_SYSTEM_SECTIONS: set[PromptSection] = {
    PromptSection.SYSTEM,
    PromptSection.PERSONA,
}


class PromptScaffold:
    """Compose an LLM prompt from typed sections.

    Sections are stored as ordered text blocks.  Call :meth:`render` to
    produce a plain-text prompt, or :meth:`render_messages` for a
    ``[{"role": ..., "content": ...}]`` list compatible with the
    Anthropic and OpenAI APIs.
    """

    def __init__(self) -> None:
        # Each section maps to a list of text blocks (append order preserved)
        self._blocks: dict[PromptSection, list[str]] = {
            sec: [] for sec in PromptSection
        }

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def set(self, section: PromptSection, content: str) -> PromptScaffold:
        """Replace *section* with *content*, discarding prior blocks.

        Returns self for chaining.
        """
        self._blocks[section] = [content]
        return self

    def append(self, section: PromptSection, content: str) -> PromptScaffold:
        """Append *content* to *section*.

        Returns self for chaining.
        """
        self._blocks[section].append(content)
        return self

    def clear(self, section: PromptSection) -> PromptScaffold:
        """Remove all content from *section*.

        Returns self for chaining.
        """
        self._blocks[section] = []
        return self

    def clear_all(self) -> PromptScaffold:
        """Remove all content from every section.

        Returns self for chaining.
        """
        for sec in PromptSection:
            self._blocks[sec] = []
        return self

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, section: PromptSection) -> str:
        """Return the joined content for *section*, or an empty string."""
        blocks = self._blocks[section]
        return "\n\n".join(blocks) if blocks else ""

    def sections_used(self) -> list[PromptSection]:
        """Return sections that have at least one content block, in render order."""
        return [sec for sec in _RENDER_ORDER if self._blocks[sec]]

    def word_count(self) -> int:
        """Approximate word count across all sections."""
        text = self.render()
        return len(text.split()) if text.strip() else 0

    def char_count(self) -> int:
        """Total character count across all sections."""
        return len(self.render())

    def is_empty(self) -> bool:
        """``True`` when no section has any content."""
        return not any(self._blocks[sec] for sec in PromptSection)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, *, separator: str = "\n\n") -> str:
        """Render all populated sections into a single string.

        Sections are emitted in canonical order, joined by *separator*.
        """
        parts: list[str] = []
        for sec in _RENDER_ORDER:
            text = self.get(sec)
            if text:
                parts.append(text)
        return separator.join(parts)

    def render_section(self, section: PromptSection) -> str:
        """Render a single section, or return an empty string."""
        return self.get(section)

    def render_messages(self) -> list[dict[str, str]]:
        """Render as a list of chat messages.

        System-role sections (SYSTEM, PERSONA) become a single
        ``{"role": "system", ...}`` message.  All remaining sections
        become a single ``{"role": "user", ...}`` message.  If either
        would be empty it is omitted.
        """
        system_parts: list[str] = []
        user_parts: list[str] = []

        for sec in _RENDER_ORDER:
            text = self.get(sec)
            if not text:
                continue
            if sec in _SYSTEM_SECTIONS:
                system_parts.append(text)
            else:
                user_parts.append(text)

        messages: list[dict[str, str]] = []
        if system_parts:
            messages.append({"role": "system", "content": "\n\n".join(system_parts)})
        if user_parts:
            messages.append({"role": "user", "content": "\n\n".join(user_parts)})
        return messages

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {sec.value: self.get(sec) for sec in _RENDER_ORDER if self._blocks[sec]}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> PromptScaffold:
        """Reconstruct a scaffold from a :meth:`to_dict` payload."""
        scaffold = cls()
        for key, value in data.items():
            try:
                sec = PromptSection(key)
            except ValueError:
                continue  # silently ignore unknown sections
            if value:
                scaffold.set(sec, value)
        return scaffold

    def __repr__(self) -> str:
        used = [s.value for s in self.sections_used()]
        return f"PromptScaffold(sections={used})"
