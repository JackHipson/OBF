---
name: ddc-writeup
description: Generate weekly DDC (Done/Doing/Considering) writeup from Notion tasks. Use when Jack asks for DDC, weekly update, or status summary.
allowed-tools: mcp__notionPersonal__*
---

# DDC Writeup Generator

Generate Jack's weekly DDC (Done/Doing/Considering) writeup for manager updates.

## Process

1. **Query Work To-Do's database** (`249e175d-4f61-81cd-9b74-d1b15465485b`):
   - Get tasks with Status = "Done" (completed this week)
   - Get tasks with Status = "Doing" (current focus)
   - Get tasks with Status = "To Do" and high priority (considering)

2. **Group by Category** where relevant:
   - Budget Model, FB BB, MBR, FP&A
   - AI, Transformation, Development
   - Learning, CIMA

3. **Format Output**:

```markdown
## Done
- [Completed task 1] - brief context if needed
- [Completed task 2]

## Doing
- [Current task 1] - progress/blockers if relevant
- [Current task 2]

## Considering
- [Upcoming priority 1] - why it's on the radar
- [Decision or question if applicable]
```

## Guidelines

- Keep it **concise** - bullet points, not paragraphs
- Focus on **business impact** - what matters to Will and leadership
- Highlight **blockers** or decisions needed
- Include **metrics** where available (e.g., "Budget model v2.3 complete - coverage ratios smoothed")
- Group related items if multiple tasks under same project
