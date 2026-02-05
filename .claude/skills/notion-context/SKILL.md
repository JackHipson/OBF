---
name: notion-context
description: Provides Notion database IDs and query patterns for Jack's workspace. Auto-invoked when working with Notion data.
user-invocable: false
---

# Notion Context for Jack's Workspace

## Key Databases

| Database | ID | Purpose |
|----------|-----|---------|
| Work To-Do's | `249e175d-4f61-81cd-9b74-d1b15465485b` | Current work tasks, priorities, status |
| Personal To-Do's | `2bce175d-4f61-8022-ba86-fc3c167aa59f` | Personal tasks and reminders |

## Key Pages

| Page | ID | Content |
|------|-----|---------|
| DDC's | `1d8e175d-4f61-80aa-a773-ebb42681776d` | Weekly Done/Doing/Considering logs |
| Career & Development | `1d1e175d-4f61-8003-85f1-caf33b54b3e0` | Career planning and development |
| Work/Life Mindset | `2b7e175d-4f61-80e9-93b3-f9e036bfdb82` | Work-life balance principles |
| Goals | `1d9e175d-4f61-80fe-a9d2-f259bb6840d6` | Short and long-term goals |
| Daily | `2bce175d-4f61-80bf-ae2b-d4b60e3528e9` | Daily kickoff and routines |
| FB-BB Model | `249e175d-4f61-8069-ba95-e4d4e23e338a` | Budget model documentation |
| Manager 1:1's | `1f4e175d-4f61-80ad-8b95-f4186f732b23` | Meeting notes with Will |

## Common Query Patterns

### Get Active Tasks
```
filter: {"property": "Status", "status": {"equals": "Doing"}}
```

### Get Tasks by Category
```
filter: {"property": "Category", "select": {"equals": "Budget Model"}}
```

### Get Completed Tasks (for DDC)
```
filter: {"property": "Status", "status": {"equals": "Done"}}
```

### Get High Priority To-Do's
```
filter: {
  "and": [
    {"property": "Status", "status": {"equals": "To Do"}},
    {"property": "Priority", "select": {"equals": "High"}}
  ]
}
```

## Task Categories
- FP&A, Budget Model, FB BB, MBR
- AI, Transformation, Development
- Learning, CIMA, Other

## Status Values
- To Do, Doing, Done, Blocked, On Hold
