---
id: "002"
title: "Add TOC Section"
stage: "constitution"
date_iso: "2026-01-26"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "main"
user: "user"
command: "sp.constitution Create a automatic ToC section that updated automatically"
labels: ["documentation", "table-of-contents", "navigation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .specify/memory/constitution.md
  - history/prompts/constitution/002-add-toc-section.constitution.prompt.md
tests_yaml: |
  - none
outcome: |
  Successfully added a Table of Contents section to the constitution for easier navigation.
evaluation: |
  The constitution was successfully updated with a Table of Contents that links to all major sections, improving document navigation.
---

# Prompt Text

```
Create a automatic ToC section that updated automatically
```

# Response Text

Added a Table of Contents section to the constitution file after the main title. The ToC includes links to all major sections of the document to improve navigation. Updated the changelog and version number to reflect this change.