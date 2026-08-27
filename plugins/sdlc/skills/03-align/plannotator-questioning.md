# Questioning mode: annotation rounds

The asynchronous mode (`questioning: annotation` in the manifest profile): the
human reviews the whole inventory in an annotation tool (Plannotator is the
example this mode was built with; any tool that returns per-passage comments
works) and answers many questions per pass. Best when the human prefers reading
over dialogue, or wants to work through a large inventory in one sitting.

## The round loop

1. **Hand over the inventory.** Point the annotation tool at
   `02-questions.inventory.md` (the view page serves as the pre-read). Say
   clearly what a useful annotation looks like: pick an option, answer in free
   text, or push back on the question itself.
2. **Open a feedback batch before ingestion.** Add an `OPEN` entry to the
   decision manifest's `feedbackBatches`: stable batch ID, annotation source,
   and the exact number of returned annotations as `expectedItems`. Do not fill
   answers in speculatively while waiting.
3. **Ingest every annotation exactly once:** record it in the inventory under
   the entry it belongs to — answer, rationale, and who/when (for example
   "User via annotation, <date>")—and update the corresponding decision state.
   Increment `processedItems` only after both writes succeed. An annotation that
   pushes back on a question rewrites nothing; the response is appended under
   the entry.
4. **Reconcile the batch before interpreting the result.** `processedItems`
   must equal `expectedItems`. Then mark it `COMPLETE` with no unresolved items,
   or `DEFERRED` with every intentionally deferred annotation named. An `OPEN`
   batch blocks gate 04. If the session stops midway, the next session resumes
   the same batch instead of starting a replacement.
5. **Keep hunting between rounds.** Answers create new gaps: append them as new
   entries in the same format, and include them in the next round.
6. **Iterate** until every Critical and Important entry is answered or
   explicitly deferred. Mirror directional decisions back in one short summary
   before writing the artifacts, so the human confirms the total picture once.

## What does not change with the mode

The recording rules are mode-independent: every answer lands in the inventory
with rationale and who/when before the artifacts are written, live findings are
appended rather than lost, and the human's explicit alignment signal is still
required. The mode changes how the conversation travels, never what gets
recorded.

The batch boundary prevents the most dangerous annotation failure: processing
some feedback, losing the rest, and presenting a polished gate as if the pass
were complete.
