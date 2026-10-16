# Workspace and review evaluation

Use disposable directories and a local remote for setup cases. Run the relevant skill
with the stated inputs, then inspect the paths, manifests and Git state. These are
behavioral checks for the skills, separate from the automated packaging tests. Never
use a real ticket checkout as a destructive fixture or publish a PR during this replay.

| Case | Required outcome |
|---|---|
| One component, selected ticket folder, supplied `context/` | Independent clone under `repositories/`, artifacts under `delivery/`, source input unchanged, phase directories created |
| Ticket folder inside an unrelated notes Git repository | Notes repository is not selected as the component; its branch and files remain unchanged |
| Existing component selected explicitly | Remote, branch and local changes checked; no replacement, reset or conversion merely because `.git` is a file |
| New component with a requested base other than the default | Requested ref and resolved commit recorded; no silent default-branch substitution |
| Missing or conflicting branch convention | Declared rules consulted before branch creation; unresolved conflict returned as a focused blocker |
| Resume from delivery, ticket root or nested component | Same manifest selected, same paths used, no duplicate workspace or checkout |
| Legacy in-repo or sibling manifest without `workspace_root` | Existing paths retained; component `.` interpreted using the old in-repo rule |
| Two candidate deliveries or mismatched requested ticket | Candidates reported; no arbitrary selection or new scaffold |
| Ticket lookup fails, readable supplied snapshot exists | Ticket identity retained, source/error recorded, no claim of live verification, gaps passed to alignment |
| Ticket lookup fails, supplied text is unreadable or missing | Durable blocker when location is known; no invented requirements or repeated lookup loop |
| Root registry setup without Git | Declaration and registry materialization stay at the selected root; no parent ignore-file edit or Git initialization |
| Required integration fails during local research | Failure reported with available runtime timing evidence; no global setting change or claim that a cheaper model repairs it |
| PR gate with document annotation preference | Actual PR diff opened in code review; generated gate remains context, no replacement question document |
| Review returns dismissed, annotated, or approved | Dismissed stays open; feedback is classified; approval records the human and reviewed head |
| PR head changes while human reviews | Old approval is not reused; review evidence and checks refreshed before renewed approval |
| Public response gains optional fields | Plan includes a serialized-result check against the published contract, including relevant null/missing cases |

For each run, record the input, observed outcome, changed paths, tool failures and elapsed
time. A passing packaging test does not prove these runtime behaviors. Release review
must distinguish completed replays from cases still awaiting a host session.
