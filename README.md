# Amenity

A terminal-based file organizer built with [Textual](https://textual.textualize.io/).

Scan a directory, classify files by extension, select which ones to move, and let Amenity sort them into category-named subfolders.

## Features

- Scans and classifies files into categories: `pdf`, `img`, `word`, `xls`, `json`, `html`, `archive`, `text`, `code`, `video`, `music`, `other`
- Interactive TUI with keyboard navigation (↑/↓/Space) and mouse support
- Select / deselect files individually or in bulk
- One-click GO to move files into category folders
- Skips existing files at the destination to avoid overwrites
- Summary report after each run

## Usage

```bash
python3 amenity.py              # scan current directory
python3 amenity.py /some/path   # scan a specific directory
```

### Controls

| Key / Button   | Action                     |
|----------------|----------------------------|
| `↑` / `↓`      | Navigate the file list     |
| `Space`        | Toggle selection, move down|
| `Select All`   | Select every file          |
| `Deselect All` | Clear all selections       |
| `GO`           | Move selected files        |
| `Help`         | Show this help screen      |
| `Exit` / `q`   | Quit                       |

## Categories

| Folder       | Extensions                                                                 |
|-------------|----------------------------------------------------------------------------|
| `pdf`       | `.pdf`, `.ppt`, `.pptx`                                                    |
| `img`       | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.svg`, `.avif`, `.ico` |
| `word`      | `.doc`, `.docx`, `.odt`, `.pages`                                          |
| `xls`       | `.xls`, `.xlsx`, `.csv`, `.numbers`, `.ods`                                |
| `json`      | `.json`, `.jsonl`                                                          |
| `html`      | `.html`, `.htm`                                                            |
| `archive`   | `.zip`, `.tar`, `.gz`, `.rar`, `.7z`, `.deb`, `.iso`, `.har`              |
| `text`      | `.txt`, `.md`, `.eml`, `.ics`, `.env`, `.log`, `.lic`, `.pem`, `.mermaid`, `.lottie` |
| `code`      | `.py`, `.js`, `.ts`, `.rs`, `.go`, `.c`, `.h`, `.cpp`, `.jsx`, `.yaml`    |
| `video`     | `.mp4`, `.mkv`, `.avi`, `.mov`, `.mpeg`                                    |
| `music`     | `.mp3`, `.flac`, `.wav`, `.aac`                                            |
| `other`     | Everything else + files without extension                                  |

## Requirements

- Python 3.12+
- [Textual](https://pypi.org/project/textual/) (`pip install textual`)
