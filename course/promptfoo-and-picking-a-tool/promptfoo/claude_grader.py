"""Claude as promptfoo's grading provider for llm-rubric, through `claude -p` with the lean flags."""
import subprocess

FLAGS = ["--system-prompt", "You grade customer-support conversations. Follow the instructions exactly.",
         "--tools", "", "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"]


def call_api(prompt, options, context):
    out = subprocess.run(["claude", "-p", "--model", "claude-sonnet-5-5", *FLAGS], input=prompt,
                         capture_output=True, text=True, timeout=300)
    return {"output": out.stdout.strip()}
