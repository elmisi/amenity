#!/usr/bin/env python3
"""TUI file organizer — classify and move files into category folders."""

from pathlib import Path
import shutil

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Header, Label

VERSION_FILE = Path(__file__).parent / "VERSIONE"
APP_VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "?"

CATEGORY_MAP: dict[str, set[str]] = {
    "pdf":     {".pdf", ".ppt", ".pptx"},
    "img":     {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".avif", ".ico"},
    "word":    {".doc", ".docx", ".odt", ".pages"},
    "xls":     {".xls", ".xlsx", ".csv", ".numbers", ".ods"},
    "json":    {".json", ".jsonl"},
    "html":    {".html", ".htm"},
    "archive": {".zip", ".tar", ".gz", ".rar", ".7z", ".deb", ".iso", ".har"},
    "text":    {".txt", ".md", ".eml", ".ics", ".env", ".log", ".lic", ".pem", ".mermaid", ".lottie"},
    "code":    {".py", ".js", ".ts", ".rs", ".go", ".c", ".h", ".cpp", ".jsx", ".yaml"},
    "video":   {".mp4", ".mkv", ".avi", ".mov", ".mpeg"},
    "music":   {".mp3", ".flac", ".wav", ".aac"},
}

CATEGORY_ORDER = [
    "pdf", "img", "word", "xls", "json", "html",
    "archive", "text", "code", "video", "music", "other",
]


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat
    return "other"


def sort_key(item: tuple[Path, str]) -> tuple[int, str]:
    path, cat = item
    order = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else 99
    return (order, path.name.lower())


class SummaryScreen(ModalScreen):
    def __init__(self, summary: dict[str, int], skipped: list[str], errors: list[str]):
        super().__init__()
        self.summary = summary
        self.skipped = skipped
        self.errors = errors

    CSS = """
    SummaryScreen { align: center middle; }
    #dialog { width: 60; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    Button { margin-top: 1; width: 100%; }
    """

    def compose(self):
        with Vertical(id="dialog"):
            yield Label("✔ Done!")
            for cat, count in sorted(self.summary.items()):
                yield Label(f"  {cat}: {count} file{'s' if count > 1 else ''}")
            if self.skipped:
                yield Label("")
                yield Label("Skipped (already exists):")
                for f in self.skipped[:10]:
                    yield Label(f"  · {f}")
                if len(self.skipped) > 10:
                    yield Label(f"  ... and {len(self.skipped) - 10} more")
            if self.errors:
                yield Label("")
                yield Label("Errors:")
                for e in self.errors[:5]:
                    yield Label(f"  ✗ {e}")
            yield Button("OK", variant="primary", id="ok")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            self.dismiss()


class HelpScreen(ModalScreen):
    CSS = """
    HelpScreen { align: center middle; }
    #dialog { width: 72; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    Button { margin-top: 1; width: 100%; }
    """

    def compose(self):
        with Vertical(id="dialog"):
            yield Label("Amenity — File Organizer", classes="title")
            yield Label("")
            yield Label("Amenity scans a directory, classifies each file by extension, and lets you")
            yield Label("move selected files into category-named subfolders (e.g., pdf/, img/, text/).")
            yield Label("")
            yield Label("How to use:")
            yield Label("  • Navigate the file list with ↑/↓ arrow keys")
            yield Label("  • Toggle selection with Space or click")
            yield Label("  • Toggle all with the Select All / Deselect All buttons")
            yield Label("  • Press GO to move all selected files into their category folders")
            yield Label("  • Existing files at the destination are skipped automatically")
            yield Label("")
            yield Label("Supported categories:")
            yield Label("  pdf · img · word · xls · json · html · archive · text · code · video · music · other")
            yield Label("")
            yield Label("Keybindings:")
            yield Label("  Space  — toggle current row")
            yield Label("  q      — quit")
            yield Button("OK", variant="primary", id="ok")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            self.dismiss()


class Amenity(App):
    CSS = """
    Button { margin: 0 1; min-width: 10; }
    #file-table { height: 1fr; }
    #footer-bar { height: 3; padding: 0 1; align: center middle; }
    #status-label { margin: 0 2; content-align: center middle; }
    """

    BINDINGS = [
        Binding("space", "toggle_selected", "Toggle selection"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, directory: str | None = None):
        super().__init__()
        self.directory = Path(directory or Path.cwd()).resolve()
        self.files: list[Path] = []
        self.selected: set[int] = set()

    def compose(self):
        yield Header()
        yield DataTable(id="file-table")
        with Horizontal(id="footer-bar"):
            yield Button("Select All", id="select-all", variant="primary")
            yield Button("Deselect All", id="deselect-all")
            yield Label(id="status-label")
            yield Button("GO", id="go", variant="success")
            yield Button("Help", id="help")
            yield Button("Exit", id="exit")

    def on_mount(self):
        self.title = f"Amenity v{APP_VERSION} — {self.directory.name}"
        table = self.query_one("#file-table", DataTable)
        table.cursor_type = "row"
        self.refresh_files()

    def refresh_files(self):
        table = self.query_one("#file-table", DataTable)
        table.clear()
        table.columns.clear()
        table.add_column("", width=3)
        table.add_column("Category", width=12)
        table.add_column("File", width=None)

        items: list[tuple[Path, str]] = []
        for p in sorted(self.directory.iterdir()):
            if p.is_file() and not p.name.startswith('.'):
                items.append((p, classify(p)))

        items.sort(key=sort_key)
        self.files = [p for p, _ in items]
        self.selected.clear()

        for i, (path, cat) in enumerate(items):
            table.add_row("☐", cat, path.name, key=str(i))

        self.update_status()

    def update_status(self):
        n = len(self.selected)
        text = f"{n} file{'s' if n != 1 else ''} selected"
        self.query_one("#status-label", Label).update(text)

    def toggle_row(self, index: int):
        if index in self.selected:
            self.selected.remove(index)
        else:
            self.selected.add(index)
        table = self.query_one("#file-table", DataTable)
        marker = "☑" if index in self.selected else "☐"
        table.update_cell_at((index, 0), marker)
        self.update_status()

    def action_toggle_selected(self):
        table = self.query_one("#file-table", DataTable)
        if table.cursor_row is not None:
            self.toggle_row(table.cursor_row)
            table.move_cursor(row=table.cursor_row + 1)

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.toggle_row(event.cursor_row)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id
        if bid == "select-all":
            for i in range(len(self.files)):
                if i not in self.selected:
                    self.toggle_row(i)
        elif bid == "deselect-all":
            for i in list(self.selected):
                self.toggle_row(i)
        elif bid == "help":
            self.push_screen(HelpScreen())
        elif bid == "go":
            self.run_go()
        elif bid == "exit":
            self.exit()

    def run_go(self):
        if not self.selected:
            self.notify("No files selected", severity="warning")
            return

        summary: dict[str, int] = {}
        skipped: list[str] = []
        errors: list[str] = []

        for idx in self.selected:
            filepath = self.files[idx]
            cat = classify(filepath)
            dest_dir = self.directory / cat
            dest_dir.mkdir(exist_ok=True)
            dest_path = dest_dir / filepath.name

            if dest_path.exists():
                skipped.append(filepath.name)
                continue

            try:
                shutil.move(str(filepath), str(dest_path))
                summary[cat] = summary.get(cat, 0) + 1
            except Exception as e:
                errors.append(f"{filepath.name}: {e}")

        self.push_screen(SummaryScreen(summary, skipped, errors))
        self.refresh_files()


if __name__ == "__main__":
    import sys
    dir_arg = sys.argv[1] if len(sys.argv) > 1 else None
    Amenity(directory=dir_arg).run()
