# Windows RDP Lab

A small personal lab for starting a temporary Windows GitHub Actions runner and
connecting to it over a private Tailscale network.

## Important

This repository intentionally does **not** create, print, or transmit an RDP
administrator password through Telegram.

The workflow enables RDP on the GitHub-hosted Windows runner and connects it to
your Tailscale network. The runner is temporary and is automatically terminated
when the GitHub Actions job ends.

## 1. GitHub secrets

Add this repository secret:

- `TAILSCALE_AUTH_KEY` — a Tailscale authentication key suitable for ephemeral
  lab machines.

Do not put the key directly into the workflow or commit it to Git.

## 2. Telegram bot

Create a Telegram bot using BotFather and obtain its bot token.

Find your own numeric Telegram user ID using a trusted Telegram user-ID method.
Put that value in `ALLOWED_USER_ID`.

## 3. GitHub token

Create a GitHub token with only the repository Actions permission needed to
dispatch/cancel workflow runs.

For a fine-grained token, grant access to this repository and the minimum
Actions permission required for your setup.

## 4. Environment variables

From the `bot` directory:

    export TELEGRAM_BOT_TOKEN="..."
    export GITHUB_TOKEN="..."
    export GITHUB_REPO="OWNER/REPOSITORY"
    export ALLOWED_USER_ID="123456789"

On Windows PowerShell, use:

    $env:TELEGRAM_BOT_TOKEN="..."
    $env:GITHUB_TOKEN="..."
    $env:GITHUB_REPO="OWNER/REPOSITORY"
    $env:ALLOWED_USER_ID="123456789"

Install dependencies:

    python -m pip install -r requirements.txt

Run:

    python bot.py

## 5. Telegram commands

    /start
    /status
    /stop
    /help

`/start` dispatches `.github/workflows/windows-lab.yml`.

`/stop` cancels active runs of that workflow.

## 6. Connect from mobile

Install a Tailscale client on the phone and sign in to the same tailnet.

After `/start`, open the GitHub Actions run and read the **Windows Lab** job
summary. It contains the Tailscale IPv4 address and RDP port.

Use a mobile RDP client and connect to:

    TAILSCALE_IP:3389

The workflow deliberately does not send an RDP password through Telegram.

## Security notes

- Keep the Tailscale network private.
- Do not expose TCP 3389 to the public internet.
- Restrict the Telegram bot to your own Telegram user ID.
- Keep the GitHub token and Tailscale auth key out of source control.
- Use a short workflow timeout for temporary testing.
- Treat the GitHub runner as disposable: do not store sensitive data on it.
# VPS-CP1
