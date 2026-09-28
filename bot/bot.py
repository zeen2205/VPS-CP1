import os
import asyncio
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]  # owner/repository
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])

API = f"https://api.github.com/repos/{GITHUB_REPO}/actions"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def allowed(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == ALLOWED_USER_ID)


async def deny(update: Update):
    await update.effective_message.reply_text("Not authorized.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return await deny(update)

    url = f"{API}/workflows/windows-lab.yml/dispatches"
    response = requests.post(
        url,
        headers=HEADERS,
        json={"ref": "main"},
        timeout=20,
    )

    if response.status_code == 204:
        await update.effective_message.reply_text(
            "Windows lab workflow started.\nUse /status to check it."
        )
    else:
        await update.effective_message.reply_text(
            f"Failed to start workflow: HTTP {response.status_code}"
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return await deny(update)

    response = requests.get(
        f"{API}/workflows/windows-lab.yml/runs?per_page=5",
        headers=HEADERS,
        timeout=20,
    )

    if response.status_code != 200:
        return await update.effective_message.reply_text(
            f"GitHub API error: HTTP {response.status_code}"
        )

    runs = response.json().get("workflow_runs", [])
    if not runs:
        return await update.effective_message.reply_text("No workflow runs found.")

    lines = []
    for run in runs[:5]:
        lines.append(
            f"#{run['run_number']} — {run['status']} / {run['conclusion'] or '-'}"
        )

    await update.effective_message.reply_text("\n".join(lines))


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return await deny(update)

    response = requests.get(
        f"{API}/workflows/windows-lab.yml/runs?status=in_progress&per_page=10",
        headers=HEADERS,
        timeout=20,
    )

    if response.status_code != 200:
        return await update.effective_message.reply_text(
            f"GitHub API error: HTTP {response.status_code}"
        )

    runs = response.json().get("workflow_runs", [])
    if not runs:
        return await update.effective_message.reply_text(
            "No active Windows lab workflow."
        )

    stopped = 0
    for run in runs:
        cancel = requests.post(
            f"{API}/runs/{run['id']}/cancel",
            headers=HEADERS,
            timeout=20,
        )
        if cancel.status_code == 202:
            stopped += 1

    await update.effective_message.reply_text(
        f"Cancellation requested for {stopped} active workflow(s)."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return await deny(update)

    await update.effective_message.reply_text(
        "/start - start Windows lab\n"
        "/status - workflow status\n"
        "/stop - stop active workflow\n"
        "/help - show commands"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()


if __name__ == "__main__":
    main()
