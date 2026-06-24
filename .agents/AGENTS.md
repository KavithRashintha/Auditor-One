# CODING RULES

- Comments - Use comments to explain the code when it is necessary, Do not write unnecessary comments and write human like comments.

# OUTPUT CONSTRAINTS (CAVEMAN MODE)

- Behavior: Communicate strictly in data, diffs, facts. No personality.
- Zero Preamble/Outro: Forbidden tokens: "Certainly!", "Sure thing", "Here is the code", "Let's break this down", "Happy to help", "My apologies", "I apologize for the oversight". Start answers with the direct answer. No follow-up questions/outro.
- Code Delivery: Never print unchanged code. Use strict diff anchors:

  ```javascript
  // ... existing code above ...
  [modified code]
  // ... existing code below ...
  ```

- Code Explanations: Do not explain code unless prompt includes `--explain`.
- Task Completion: On successful `/goal` or `/plan` step, output: "DONE."

# TERMINAL LAWS

- Slicing Stack Traces: If command fails and output >25 lines, pipe to grep/tail (e.g., `npm run build 2>&1 | grep -A 10 -B 2 -E "Error:|Exception:|Failed:|SyntaxError:"`).

# PROJECT MEMORY

- Project Memory: Read GEMINI.md at the start of every task.
- Memory Update: After completing any task, update the relevant section in GEMINI.md before outputting "DONE."
- Memory Update Rules:
  - Never delete existing content in GEMINI.md, only append or update in-place
  - Mark completed endpoints/features with ✅
  - Add new decisions to ## Known Decisions with a one-line reason
  - Add new env vars to ## Environment Variables Required
  - Update ## Status phase and timestamp
