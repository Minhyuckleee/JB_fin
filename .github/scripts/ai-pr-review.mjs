import fs from "node:fs";
import { execFileSync } from "node:child_process";
import OpenAI from "openai";

const diffPath = "pr.diff";
const maxDiffChars = 120_000;
const model = process.env.AI_REVIEW_MODEL || "gpt-5.5";
const prNumber = process.env.PR_NUMBER;
const repo = process.env.REPO;

if (!process.env.OPENAI_API_KEY) {
  throw new Error("OPENAI_API_KEY secret is required.");
}

if (!prNumber || !repo) {
  throw new Error("PR_NUMBER and REPO environment variables are required.");
}

const rawDiff = fs.existsSync(diffPath) ? fs.readFileSync(diffPath, "utf8") : "";
const diff =
  rawDiff.length > maxDiffChars
    ? `${rawDiff.slice(0, maxDiffChars)}\n\n[Diff truncated at ${maxDiffChars} characters.]`
    : rawDiff;

if (!diff.trim()) {
  console.log("No diff found; skipping AI review comment.");
  process.exit(0);
}

const client = new OpenAI();

const response = await client.responses.create({
  model,
  reasoning: { effort: "medium" },
  input: [
    {
      role: "developer",
      content:
        "You are a senior code reviewer. Be concise, specific, and practical. Focus on real risks, not style nits. Do not claim tests were run unless evidence appears in the diff.",
    },
    {
      role: "user",
      content: `Review this pull request diff.

Return Markdown with these sections:

## High-risk findings
## Medium-risk findings
## Missing tests
## Merge recommendation

For each finding, include the affected file or code area when possible. If a section has no items, say "None found."

Diff:
${diff}`,
    },
  ],
});

const body = [
  "## AI PR Review",
  "",
  response.output_text?.trim() || "No review output was generated.",
].join("\n");

execFileSync(
  "gh",
  ["pr", "comment", prNumber, "--repo", repo, "--body", body],
  {
    stdio: "inherit",
    env: {
      ...process.env,
      GH_TOKEN: process.env.GH_TOKEN,
    },
  },
);
