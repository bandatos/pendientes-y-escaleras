---
name: create-skill
description: Create a new Claude Code skill (<skill-name>/SKILL.md). Use this whenever the user wants to document a reusable pattern, add a slash command, or standardize how to implement a recurring project feature. Triggers when the user mentions "create skill", "new skill", "add command", or wants to capture a workflow as a skill.
---

# Create a Claude Code Skill

## Skill Anatomy

A skill lives in its own directory with a required `SKILL.md` file and optional bundled resources:

```
skill-name/
├── SKILL.md          (required — main instructions)
├── scripts/          (optional — executable code for deterministic tasks)
├── references/       (optional — docs loaded into context as needed)
└── assets/           (optional — templates, icons, fonts used in output)
```

Target path: `.claude/skills/<skill-name>/SKILL.md`

## Required Structure

```markdown
---
name: <slug-kebab-case>
description: <what it does + when to trigger, 1-2 sentences with natural keywords the user would say>
---

# <Skill Title>

<body content>
```

## Content Rules

- **Keep SKILL.md under 500 lines** — if it grows beyond that, move details into bundled resource files (`references/`, `scripts/`) and add clear pointers from SKILL.md about when to read them
- Read the project's actual files before writing — use real snippets, not abstract placeholders
- Document which store, composable, or plugin to use, with exact paths
- Include minimal working examples; avoid unnecessary boilerplate
- Use tables for mappings (action → message, field → validation, etc.)
- Write the `description` with keywords the user would naturally say — be slightly "pushy" so Claude triggers the skill even when the user doesn't ask for it by name
- Prefer imperative form in instructions; explain *why* things matter instead of piling on rigid MUSTs

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — loaded when the skill triggers (<500 lines ideal)
3. **Bundled resources** — loaded as needed (unlimited size; scripts can execute without being read into context)

For large reference files (>300 lines), include a table of contents so Claude can jump to the relevant section.

## Optional YAML Fields

| Field | When to use |
|-------|-------------|
| `user-invocable: false` | Claude-only; won't appear in the `/` menu |
| `disable-model-invocation: true` | Manual invocation only; Claude won't auto-trigger it |
| `allowed-tools: Read, Grep` | Restrict available tools (useful for read-only skills) |
| `argument-hint: [name]` | Autocomplete hint when typing `/skill-name` |

## Skills vs. Commands

| `.claude/skills/` | `.claude/commands/` |
|-------------------|---------------------|
| Implementation pattern (how to code something) | API reference / external documentation |
| Claude auto-triggers by context | Manually invoked via `/command` |
| Includes code snippets from the project | Can be pure documentation |

## Process

1. Identify the topic; pick a `name` in kebab-case
2. Read the relevant project files to extract real patterns
3. Write a `description` with keywords the user would naturally use — lean toward over-triggering rather than under-triggering
4. Structure the content: context → main pattern → minimal example → notes
5. Check total lines — if approaching 500, extract sections into `references/` or `scripts/`
6. If a related skill already exists, update it instead of creating a new one

## Minimal Example

```markdown
---
name: api-calls
description: Make API calls using the project's $api plugin. Use whenever the user
  needs GET, POST, or DELETE requests to the Django REST backend, or mentions fetching
  data from the API.
---

# api-calls

Use the `$api` plugin (axios) injected by `plugins/api.ts`.

\`\`\`js
const { $api } = useNuxtApp()
const { data } = await $api.get('/api/resource/')
const created = await $api.post('/api/resource/', payload)
await $api.delete(`/api/resource/${id}/`)
\`\`\`

The plugin attaches `Authorization: Token <value>` from the `auth_onigies` cookie.
```