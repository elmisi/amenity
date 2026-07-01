#!/usr/bin/env python3
"""
Automated screenshot generator for Amenity documentation.

Uses Textual's test mode to drive the app and capture screenshots.
Run after UI changes to update documentation images.

Usage:
    python scripts/take_screenshots.py

Output:
    screenshots/*.svg - Vector screenshots
"""

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from amenity import Amenity

SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"


def create_demo_dir() -> Path:
    """Create a temporary directory with sample files for screenshots."""
    demo = Path(tempfile.mkdtemp(suffix="_amenity_demo"))

    samples = {
        "report.pdf": "pdf",
        "presentation.pptx": "pdf",
        "photo.jpg": "img",
        "logo.png": "img",
        "article.docx": "word",
        "spreadsheet.xlsx": "xls",
        "budget.ods": "xls",
        "data.json": "json",
        "index.html": "html",
        "archive.zip": "archive",
        "notes.txt": "text",
        "readme.md": "text",
        "email.eml": "text",
        "script.py": "code",
        "main.ts": "code",
        "config.yaml": "code",
        "song.mp3": "music",
        "video.mp4": "video",
        "mystery.bin": "other",
        "readme.long.File.with.dots.txt": "text",
    }

    for name in samples:
        (demo / name).touch()

    return demo


async def take_screenshots():
    """Drive the app and capture screenshots of each screen."""

    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    demo_dir = create_demo_dir()
    print(f"Demo directory: {demo_dir}")

    app = Amenity(directory=str(demo_dir))

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()

        # --- Screenshot 1: Main screen (no selection) ---
        app.save_screenshot(str(SCREENSHOTS_DIR / "01_main_screen.svg"))
        print("✓ 01_main_screen.svg")

        # --- Screenshot 2: Select all files ---
        await pilot.click("#select-all")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "02_all_selected.svg"))
        print("✓ 02_all_selected.svg")

        # --- Screenshot 3: Help modal ---
        await pilot.click("#help")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "03_help_modal.svg"))
        print("✓ 03_help_modal.svg")

        # Close help
        await pilot.click("Button#ok")
        await pilot.pause()

        # --- Screenshot 4: Summary after GO ---
        await pilot.click("#go")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "04_summary.svg"))
        print("✓ 04_summary.svg")

        await pilot.click("Button#ok")
        await pilot.pause()

        print(f"\nScreenshots saved to: {SCREENSHOTS_DIR}")

    shutil.rmtree(demo_dir, ignore_errors=True)


def main():
    print("Generating screenshots for Amenity...\n")
    asyncio.run(take_screenshots())
    print("\nDone!")


if __name__ == "__main__":
    main()
