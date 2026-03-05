import subprocess


def notify(title: str, message: str) -> None:
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}"',
    ])
