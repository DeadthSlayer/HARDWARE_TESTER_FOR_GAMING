# RunWise AI

RunWise AI predicts whether a laptop can run popular games and creative software smoothly.

The project now supports two Python-only interfaces:

- `app.py` - Rich-powered terminal application
- `streamlit_app.py` - locally hosted Streamlit dashboard

Both interfaces reuse the same hardware detection, JSON database, and rule-based prediction engine.

## Features

- Automatic CPU, RAM, GPU, storage, battery, OS, and screen resolution detection
- Smart fallback fields only when a hardware detail cannot be detected
- Compatibility score out of 100
- Estimated FPS or smoothness score
- Lag chance: Low, Medium, High
- Battery drain: Mild, Moderate, Heavy
- Thermals: Cool, Warm, Hot
- Recommended graphics/settings output
- Search system for games and software
- Rule-based prediction logic with a future-ready engine interface for ML models
- JSON database with minimum and recommended requirements
- Beginner-friendly modular project structure
- PyInstaller-ready terminal packaging path

## Project Structure

```text
RunWise AI/
|-- app.py
|-- streamlit_app.py
|-- requirements.txt
|-- README.md
|-- hardware/
|   |-- __init__.py
|   |-- detector.py
|   |-- models.py
|   `-- scoring.py
|-- predictor/
|   |-- __init__.py
|   |-- engine.py
|   `-- models.py
|-- database/
|   |-- __init__.py
|   `-- game_database.py
|-- utils/
|   |-- __init__.py
|   |-- display.py
|   `-- paths.py
`-- data/
    `-- games.json
```

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The Terminal App

```bash
python app.py
```

## Run The Local Streamlit App

Double-click this file on Windows:

```text
run_local.bat
```

If Python is missing, the launcher can install Python 3.12 with `winget` or open the official Python download page. During manual installation, enable `Add python.exe to PATH`.

Or run Streamlit manually:

```bash
streamlit run streamlit_app.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Open that URL in your browser. The app runs locally on your machine and does not require Node.js, React, or any JavaScript framework.

## Packaging The Terminal App With PyInstaller

Install requirements first, then run:

```bash
pyinstaller --onefile --name RunWiseAI --add-data "data/games.json;data" app.py
```

On macOS or Linux, use a colon in `--add-data`:

```bash
pyinstaller --onefile --name RunWiseAI --add-data "data/games.json:data" app.py
```

The executable will be created inside the `dist` folder.

## Database

The app includes requirements for:

- GTA V
- Valorant
- Minecraft
- Cyberpunk 2077
- Blender
- Premiere Pro
- OBS Studio
- Fortnite
- CS2

To add more titles, edit `data/games.json` and follow the existing structure.

## Prediction Logic

The initial engine is rule-based. It compares detected hardware scores against each title's minimum and recommended scores.

The `BasePredictionEngine` class in `predictor/engine.py` is intentionally small so future models can be introduced cleanly, such as:

- Linear Regression
- Random Forest Regression
- Gradient Boosting

## Notes

Hardware detection varies by operating system and permissions. Windows systems get the richest detection path through `wmi`, PowerShell, and `psutil`. If a field cannot be detected, the terminal app prompts for it, while the Streamlit app shows editable sidebar fields.
