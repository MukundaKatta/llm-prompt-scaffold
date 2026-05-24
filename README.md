# llm-prompt-scaffold

Build structured multi-section LLM prompts from typed components. Zero dependencies.

## Install

```bash
pip install llm-prompt-scaffold
```

## Quick start

```python
from llm_prompt_scaffold import PromptScaffold, PromptSection

scaffold = PromptScaffold()
scaffold.set(PromptSection.SYSTEM,       "You are a code reviewer.")
scaffold.set(PromptSection.CONTEXT,      "The PR touches auth logic.")
scaffold.set(PromptSection.INSTRUCTION,  "Identify security issues.")
scaffold.set(PromptSection.OUTPUT_FORMAT,"Bullet list, one issue per line.")

# Plain-text prompt
print(scaffold.render())

# Chat messages list (Anthropic / OpenAI compatible)
messages = scaffold.render_messages()
# [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
```

## Sections

| Section | Chat role | Description |
|---|---|---|
| `SYSTEM` | system | Core system instructions |
| `PERSONA` | system | Persona / role definition |
| `CONTEXT` | user | Background information |
| `EXAMPLES` | user | Few-shot examples |
| `CONSTRAINTS` | user | Rules and guardrails |
| `INSTRUCTION` | user | Main task instruction |
| `OUTPUT_FORMAT` | user | Desired output structure |

Sections render in the order shown above.

## API

### `PromptScaffold`

| Method | Description |
|---|---|
| `set(section, content)` | Replace section content (chainable) |
| `append(section, content)` | Append a block to a section (chainable) |
| `clear(section)` | Remove all content from a section (chainable) |
| `clear_all()` | Remove all content (chainable) |
| `get(section)` | Return section text, or `""` |
| `render(separator)` | All sections as a single string |
| `render_section(section)` | Single section as a string |
| `render_messages()` | `[{"role": ..., "content": ...}]` list |
| `sections_used()` | Populated sections in render order |
| `word_count()` | Approximate word count |
| `char_count()` | Total character count |
| `is_empty()` | `True` when no section has content |
| `to_dict()` | JSON-serialisable dict |
| `from_dict(data)` | Reconstruct from `to_dict()` output |

## License

MIT
