# Questioning mode: chat

The default mode (`questioning: chat` in the manifest profile): the conversation
runs in the session, one question per round, two only when tightly coupled.
Entries with a proposed answer are presented for confirmation, not re-derived.

## The question template

Every question appears in chat exactly in this shape — the runtime's interactive
ask-tools may be used *in addition*, but never replace or compress it:

```markdown
### Question <n> of <total> — [<tier>] [<track>] <short name>

**Context:** <1–2 sentences, with the story quote or path:line from the entry>

**Question:** <the one sentence, bold>

**Options:**
- **A (recommended):** <option> — <why / trade-off>
- **B:** <option> — <trade-off>

Answer A/B or in your own words.
```

The counter gives the human progress; the recommendation gives them a default;
the context spares them reconstructing why this matters. All three come from the
inventory entry — presentation quality must not depend on live improvisation.

## Round discipline

- Critical first, then Important, then Clarification.
- Record each answer in the inventory before the next round: answer, rationale,
  who/when.
- Directional answers are mirrored back and confirmed before moving on.
- A new gap surfaced by an answer is appended to the inventory in the same
  format and announced.
