# Shared skill rules

These rules apply to `create`, `connect`, and `update-index-and-crosslinks`.
Each skill defines its own questions and Result block.

## Output discipline

The user sees exactly two kinds of messages from this skill: questions and the final Result block. Nothing else.

- Work silently. No step-by-step narration, no file-by-file progress, no restating these instructions, no explaining the registry format.
- Each question is one short message: one line of context, the options, nothing more.
- The final message is the Result block, preceded by at most one sentence. Anything that does not fit the block does not belong in the final message.
- Every run ends with the block, success or failure: Status says what happened, the body says what changed or why nothing did, Next steps give the user concrete actions or state `none`.
