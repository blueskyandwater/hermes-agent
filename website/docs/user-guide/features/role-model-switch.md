---
title: Verified role model switching
sidebar_label: Role model switching
---

# Verified role model switching (Codex)

`hermes role-model --role normal --model MODEL_ID` changes **one existing** `routing.roles` entry for an `openai-codex` profile. The command reads the live Codex model catalog using your existing Hermes OAuth credentials (no offline catalog fallback), then sends a tool-free, non-stored streaming completion probe. It writes only after the selected model returns text and a completed response. Failures leave `config.yaml` unchanged; successful writes create a private `config.yaml.bak` containing the previous config. Use `hermes --profile NAME role-model ...` to target a named profile. This command does not sign in, migrate your config, or restart running agents; restart the CLI/gateway separately to apply the change.

Example of an **existing** role mapping (model IDs below are placeholders, not claims of current catalog availability):

```yaml
model:
  provider: openai-codex
routing:
  enabled: true
  roles:
    normal: CURRENT_NORMAL_MODEL
    design: CURRENT_DESIGN_MODEL
  normal_chat:
    role: normal
  code_design:
    role: design
  long_context:
    model: EXISTING_LONG_CONTEXT_MODEL
  vision:
    model: EXISTING_VISION_MODEL
```

For example, `hermes role-model --role normal --model NEW_MODEL_ID` changes `routing.roles.normal` only, leaving the `normal_chat.role` mapping, `design`, direct `long_context.model` and `vision.model`, and fallback configuration unchanged. Use `--role design` to change the `design` role separately. It cannot create roles or convert an existing direct route to a role. A model listed in the live catalog is not sufficient by itself: a failed/empty completion prevents the update. The probe makes a real network request and may incur provider usage. Do not paste OAuth tokens into the command.
