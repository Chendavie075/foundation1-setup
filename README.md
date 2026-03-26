# RC Stable Audio Tools for Foundation-1

This fork packages a working local setup for Foundation-1, an open-source music generation model that can generate audio and export MIDI for DAW workflows.

The repository is prepared for a public GitHub workflow:

- Source code can be pushed to GitHub.
- Python environments, caches, generated audio, and model weights stay out of git.
- Windows setup, model download, and startup are handled by repo-local scripts.
- The launcher includes the localhost proxy workaround needed for some Windows environments where Gradio startup checks fail with `502`.

## What This Repo Does

- Generates audio from prompts with BPM, key, and bar controls.
- Exports MIDI alongside generated audio.
- Supports local model downloads into the repo `models/` folder.
- Uses repo-local caches under `.cache/` instead of relying on global temp paths.

## Hardware

- NVIDIA GPU with at least 8 GB VRAM is recommended for Foundation-1.
- Windows + NVIDIA is the main tested path for this repo.
- RTX 50-series users should stay on the included `torch 2.7.1 + cu128` install path.

## What You Can Push To GitHub

Safe to publish:

- source code
- scripts
- `README.md`
- `config.json`

Do not publish:

- `env/`
- `.venv/`
- `.cache/`
- `generations/`
- `models/`

The Foundation-1 model weights are not included in this repository. Code and weights use different licenses, so keep that separation explicit.

## Windows Quick Start

### 1. Clone the repository

```powershell
git clone https://github.com/your-user/RC-stable-audio-tools.git
cd RC-stable-audio-tools
```

### 2. Install Miniconda and Git

Install both first, then make sure `conda` is available in PowerShell.

### 3. Create the repo-local environment

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

This creates a local environment at `.\env`, installs `torch 2.7.1 + cu128`, pins `numpy 1.23.5`, and installs this repository.

### 4. Download Foundation-1

```powershell
.\env\python.exe .\scripts\download_models.py --model-id RoyalCities/Foundation-1 --download-t5
```

This downloads:

- `RoyalCities/Foundation-1` into `.\models\RoyalCities-Foundation-1`
- `t5-base` into `.\.cache\hf-models\t5-base`

You can skip this step and use the in-app download tab instead, but pre-downloading is more reliable if you plan to move this repo between machines.

### 5. Start the UI

```powershell
.\start-foundation1.bat
```

Then open the `http://127.0.0.1:<port>` URL printed in the terminal.

If `7860` is already in use, Gradio may select another local port.

## Usage Notes

- On first load, the model can take some time to move to GPU.
- `flash_attn not installed` is a warning, not a blocker.
- Some Gradio and PyTorch `FutureWarning` messages are harmless for inference.
- Generated audio and MIDI files are written to `generations/` by default.

## Config

`config.json` controls local paths and the curated model list shown in the download tab.

Example:

```json
{
  "models_directory": "models",
  "generations_directory": "generations",
  "model_downloads": [
    {
      "path": "models",
      "options": [
        "RoyalCities/Foundation-1"
      ]
    }
  ]
}
```

Relative paths are resolved from the repository root, so the app no longer depends on the shell's current working directory.

## Public GitHub Checklist

Before you push:

1. Keep model weights and generated assets out of git.
2. Commit only the source and script changes.
3. Create a new GitHub repo and push this repository there.
4. Mention in your repo description that users still need to download Foundation-1 separately.

## Upstream

This project is based on [Stability AI's stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools) and adds a Foundation-1-oriented local workflow on top.
