"""Tests for llm-prompt-scaffold."""

from __future__ import annotations

from llm_prompt_scaffold import PromptScaffold, PromptSection

# ---------------------------------------------------------------------------
# PromptSection
# ---------------------------------------------------------------------------


def test_section_values():
    assert PromptSection.SYSTEM.value == "system"
    assert PromptSection.PERSONA.value == "persona"
    assert PromptSection.CONTEXT.value == "context"
    assert PromptSection.EXAMPLES.value == "examples"
    assert PromptSection.CONSTRAINTS.value == "constraints"
    assert PromptSection.INSTRUCTION.value == "instruction"
    assert PromptSection.OUTPUT_FORMAT.value == "output_format"


def test_section_is_str():
    assert isinstance(PromptSection.SYSTEM, str)


# ---------------------------------------------------------------------------
# PromptScaffold — construction
# ---------------------------------------------------------------------------


def test_new_scaffold_is_empty():
    s = PromptScaffold()
    assert s.is_empty()


def test_sections_used_empty():
    s = PromptScaffold()
    assert s.sections_used() == []


def test_word_count_empty():
    s = PromptScaffold()
    assert s.word_count() == 0


def test_char_count_empty():
    s = PromptScaffold()
    assert s.char_count() == 0


# ---------------------------------------------------------------------------
# PromptScaffold — set / get / clear
# ---------------------------------------------------------------------------


def test_set_and_get():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "You are helpful.")
    assert s.get(PromptSection.SYSTEM) == "You are helpful."


def test_set_replaces():
    s = PromptScaffold()
    s.set(PromptSection.INSTRUCTION, "First instruction.")
    s.set(PromptSection.INSTRUCTION, "Second instruction.")
    assert s.get(PromptSection.INSTRUCTION) == "Second instruction."


def test_set_returns_self():
    s = PromptScaffold()
    result = s.set(PromptSection.SYSTEM, "x")
    assert result is s


def test_append_adds_block():
    s = PromptScaffold()
    s.set(PromptSection.CONTEXT, "Block one.")
    s.append(PromptSection.CONTEXT, "Block two.")
    text = s.get(PromptSection.CONTEXT)
    assert "Block one." in text
    assert "Block two." in text


def test_append_separator():
    s = PromptScaffold()
    s.set(PromptSection.CONTEXT, "A")
    s.append(PromptSection.CONTEXT, "B")
    assert s.get(PromptSection.CONTEXT) == "A\n\nB"


def test_append_returns_self():
    s = PromptScaffold()
    result = s.append(PromptSection.SYSTEM, "x")
    assert result is s


def test_clear_section():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "content")
    s.clear(PromptSection.SYSTEM)
    assert s.get(PromptSection.SYSTEM) == ""


def test_clear_returns_self():
    s = PromptScaffold()
    result = s.clear(PromptSection.SYSTEM)
    assert result is s


def test_clear_all():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "a")
    s.set(PromptSection.INSTRUCTION, "b")
    s.clear_all()
    assert s.is_empty()


def test_clear_all_returns_self():
    s = PromptScaffold()
    result = s.clear_all()
    assert result is s


def test_get_missing_returns_empty():
    s = PromptScaffold()
    assert s.get(PromptSection.EXAMPLES) == ""


# ---------------------------------------------------------------------------
# PromptScaffold — sections_used
# ---------------------------------------------------------------------------


def test_sections_used_order():
    s = PromptScaffold()
    s.set(PromptSection.INSTRUCTION, "do it")
    s.set(PromptSection.SYSTEM, "be helpful")
    s.set(PromptSection.CONTEXT, "background")
    used = s.sections_used()
    # Must be in canonical render order: SYSTEM < CONTEXT < INSTRUCTION
    assert used.index(PromptSection.SYSTEM) < used.index(PromptSection.CONTEXT)
    assert used.index(PromptSection.CONTEXT) < used.index(PromptSection.INSTRUCTION)


def test_sections_used_excludes_empty():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "x")
    assert PromptSection.EXAMPLES not in s.sections_used()


# ---------------------------------------------------------------------------
# PromptScaffold — word_count / char_count / is_empty
# ---------------------------------------------------------------------------


def test_word_count():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "You are a helpful assistant.")
    assert s.word_count() == 5


def test_char_count():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "Hello")
    assert s.char_count() == 5


def test_is_empty_false_after_set():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "content")
    assert not s.is_empty()


def test_is_empty_true_after_clear_all():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "content")
    s.clear_all()
    assert s.is_empty()


# ---------------------------------------------------------------------------
# PromptScaffold — render
# ---------------------------------------------------------------------------


def test_render_single_section():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "You are helpful.")
    assert s.render() == "You are helpful."


def test_render_multiple_sections_order():
    s = PromptScaffold()
    s.set(PromptSection.INSTRUCTION, "Do the thing.")
    s.set(PromptSection.SYSTEM, "Be concise.")
    rendered = s.render()
    assert rendered.index("Be concise.") < rendered.index("Do the thing.")


def test_render_separator():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "A")
    s.set(PromptSection.INSTRUCTION, "B")
    assert s.render() == "A\n\nB"


def test_render_custom_separator():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "A")
    s.set(PromptSection.INSTRUCTION, "B")
    assert s.render(separator="\n---\n") == "A\n---\nB"


def test_render_empty():
    s = PromptScaffold()
    assert s.render() == ""


def test_render_section():
    s = PromptScaffold()
    s.set(PromptSection.EXAMPLES, "Example 1\nExample 2")
    assert s.render_section(PromptSection.EXAMPLES) == "Example 1\nExample 2"


def test_render_section_missing():
    s = PromptScaffold()
    assert s.render_section(PromptSection.CONSTRAINTS) == ""


# ---------------------------------------------------------------------------
# PromptScaffold — render_messages
# ---------------------------------------------------------------------------


def test_render_messages_system_only():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "Be helpful.")
    msgs = s.render_messages()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "system"
    assert msgs[0]["content"] == "Be helpful."


def test_render_messages_user_only():
    s = PromptScaffold()
    s.set(PromptSection.INSTRUCTION, "Do this.")
    msgs = s.render_messages()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "user"


def test_render_messages_both():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "system text")
    s.set(PromptSection.INSTRUCTION, "user text")
    msgs = s.render_messages()
    assert len(msgs) == 2
    roles = [m["role"] for m in msgs]
    assert roles == ["system", "user"]


def test_render_messages_empty():
    s = PromptScaffold()
    assert s.render_messages() == []


def test_render_messages_persona_in_system():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "system")
    s.set(PromptSection.PERSONA, "persona")
    msgs = s.render_messages()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "system"
    assert "system" in msgs[0]["content"]
    assert "persona" in msgs[0]["content"]


def test_render_messages_context_in_user():
    s = PromptScaffold()
    s.set(PromptSection.CONTEXT, "background info")
    msgs = s.render_messages()
    assert msgs[0]["role"] == "user"
    assert "background info" in msgs[0]["content"]


# ---------------------------------------------------------------------------
# PromptScaffold — to_dict / from_dict
# ---------------------------------------------------------------------------


def test_to_dict():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "Be helpful.")
    s.set(PromptSection.INSTRUCTION, "Summarize.")
    d = s.to_dict()
    assert d["system"] == "Be helpful."
    assert d["instruction"] == "Summarize."
    assert "context" not in d  # empty sections omitted


def test_from_dict_roundtrip():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "A")
    s.set(PromptSection.CONTEXT, "B")
    s.set(PromptSection.INSTRUCTION, "C")
    s2 = PromptScaffold.from_dict(s.to_dict())
    assert s2.get(PromptSection.SYSTEM) == "A"
    assert s2.get(PromptSection.CONTEXT) == "B"
    assert s2.get(PromptSection.INSTRUCTION) == "C"


def test_from_dict_ignores_unknown_keys():
    s = PromptScaffold.from_dict({"system": "hello", "unknown_key": "ignored"})
    assert s.get(PromptSection.SYSTEM) == "hello"


def test_from_dict_ignores_empty_values():
    s = PromptScaffold.from_dict({"system": "", "instruction": "do it"})
    assert PromptSection.SYSTEM not in s.sections_used()
    assert s.get(PromptSection.INSTRUCTION) == "do it"


def test_to_dict_joins_appended_blocks():
    s = PromptScaffold()
    s.append(PromptSection.EXAMPLES, "one")
    s.append(PromptSection.EXAMPLES, "two")
    assert s.to_dict()["examples"] == "one\n\ntwo"


def test_from_dict_roundtrip_preserves_appended_blocks():
    s = PromptScaffold()
    s.append(PromptSection.EXAMPLES, "one")
    s.append(PromptSection.EXAMPLES, "two")
    s2 = PromptScaffold.from_dict(s.to_dict())
    assert s2.get(PromptSection.EXAMPLES) == s.get(PromptSection.EXAMPLES)


def test_to_dict_keys_in_render_order():
    s = PromptScaffold()
    s.set(PromptSection.INSTRUCTION, "do it")
    s.set(PromptSection.SYSTEM, "be helpful")
    keys = list(s.to_dict().keys())
    assert keys.index("system") < keys.index("instruction")


# ---------------------------------------------------------------------------
# PromptScaffold — chaining
# ---------------------------------------------------------------------------


def test_chaining():
    s = (
        PromptScaffold()
        .set(PromptSection.SYSTEM, "sys")
        .set(PromptSection.INSTRUCTION, "inst")
        .append(PromptSection.INSTRUCTION, "more")
    )
    assert "inst" in s.get(PromptSection.INSTRUCTION)
    assert "more" in s.get(PromptSection.INSTRUCTION)


# ---------------------------------------------------------------------------
# PromptScaffold — repr
# ---------------------------------------------------------------------------


def test_repr_empty():
    s = PromptScaffold()
    assert "PromptScaffold" in repr(s)
    assert "[]" in repr(s)


def test_repr_with_sections():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "x")
    r = repr(s)
    assert "system" in r


# ---------------------------------------------------------------------------
# Integration — full prompt
# ---------------------------------------------------------------------------


def test_full_prompt_render():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "You are a code reviewer.")
    s.set(PromptSection.CONTEXT, "The PR touches auth logic.")
    s.set(PromptSection.INSTRUCTION, "Identify security issues.")
    s.set(PromptSection.OUTPUT_FORMAT, "Bullet list, one issue per line.")

    rendered = s.render()
    assert "code reviewer" in rendered
    assert "auth logic" in rendered
    assert "security issues" in rendered
    assert "Bullet list" in rendered
    # canonical order preserved
    assert rendered.index("code reviewer") < rendered.index("auth logic")
    assert rendered.index("auth logic") < rendered.index("security issues")


def test_full_prompt_messages():
    s = PromptScaffold()
    s.set(PromptSection.SYSTEM, "You are helpful.")
    s.set(PromptSection.INSTRUCTION, "Explain this code.")
    s.set(PromptSection.OUTPUT_FORMAT, "One paragraph.")

    msgs = s.render_messages()
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"
    assert "Explain" in msgs[1]["content"]
    assert "One paragraph" in msgs[1]["content"]


def test_append_examples():
    s = PromptScaffold()
    s.append(PromptSection.EXAMPLES, "Example 1: foo → bar")
    s.append(PromptSection.EXAMPLES, "Example 2: baz → qux")
    text = s.get(PromptSection.EXAMPLES)
    assert "Example 1" in text
    assert "Example 2" in text
    assert s.word_count() > 0
