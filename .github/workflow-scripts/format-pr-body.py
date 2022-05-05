import subprocess
import shutil
import sys
import os


print("------- here -------")
print(os.environ.get("INPUT_RAW_BODY"))


def run(cmd, **kwargs):
    """Execute the given command and return the stdout as a decoded string."""

    cmd, *args = cmd.split(" ")

    resolved_cmd = shutil.which(cmd)
    if not resolved_cmd:
        raise Exception(f"Couldn't resolve command `{cmd}`.")

    res = subprocess.run([resolved_cmd, *args],
                         text=True,
                         capture_output=True,
                         **kwargs)

    # Raises `CalledProcessError` on non-zero exit.
    res.check_returncode()

    return res.stdout.strip()


def print_action_output(out, *, name):
    table = str.maketrans({
        "\n": "%0A",
        "\r": "%0D",
        "%":  "%25",
    })
    escaped_out = out.translate(table)
    print(f"::set-output name={name}::{escaped_out}")


raw_pr_body = run("git interpret-trailers --only-input", stdin=sys.stdin)
raw_pr_trailers = run("git interpret-trailers --parse", input=raw_pr_body)

# Remove trailers from the commit message:
filtered_pr_body = raw_pr_body[0:-len(raw_pr_trailers)]

# Format `filtered_body` with Prettier:
formatted_body = run(
    "yarn --silent prettier --parser=markdown --prose-wrap=always --print-width=88",
    input=filtered_pr_body
)

# Join the formatted body with the original trailers:
pr_body = "\n".join([
    formatted_body.strip(),
    "",
    raw_pr_trailers
])

print_action_output(pr_body, name="fmt_result")
