import argparse
import json
import os
from pathlib import Path

from huggingface_hub import snapshot_download


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config.json"
CACHE_ROOT = REPO_ROOT / ".cache"


def resolve_repo_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_model_allow_patterns(repo_id: str):
    repo_id = repo_id.strip()
    if repo_id == "RoyalCities/Foundation-1":
        return [
            "Foundation_1.safetensors",
            "model_config.json",
            "LICENSE*",
            "README*",
            "Master_Tag_Reference.md",
        ]
    return None


def prepare_transformers_environment():
    os.environ.setdefault("HF_HOME", str(CACHE_ROOT / "hf"))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(CACHE_ROOT / "hf" / "hub"))
    os.environ.setdefault("TRANSFORMERS_NO_LIBROSA", "1")

    try:
        import transformers.utils as transformers_utils
        from transformers.utils import import_utils as transformers_import_utils
    except Exception:
        return

    def _false():
        return False

    transformers_utils.is_librosa_available = _false
    transformers_import_utils.is_librosa_available = _false


def download_model(repo_id: str, models_dir: Path):
    target_dir = models_dir / repo_id.replace("/", "-")
    target_dir.mkdir(parents=True, exist_ok=True)

    if any(target_dir.iterdir()):
        print(f"Model already present: {target_dir}")
        return

    print(f"Downloading {repo_id} into {target_dir}")
    snapshot_download(
        repo_id=repo_id,
        repo_type="model",
        local_dir=str(target_dir),
        allow_patterns=get_model_allow_patterns(repo_id),
    )
    print(f"Finished downloading model: {repo_id}")


def download_t5(target_dir: Path):
    prepare_transformers_environment()

    from transformers import AutoTokenizer, T5EncoderModel

    target_dir.mkdir(parents=True, exist_ok=True)

    if (target_dir / "config.json").exists():
        print(f"T5 cache already present: {target_dir}")
        return

    print(f"Downloading t5-base into {target_dir}")
    tokenizer = AutoTokenizer.from_pretrained("t5-base")
    tokenizer.save_pretrained(target_dir)

    model = T5EncoderModel.from_pretrained("t5-base")
    model.save_pretrained(target_dir)
    print("Finished downloading t5-base")


def main():
    parser = argparse.ArgumentParser(description="Download Foundation One model assets into this repository.")
    parser.add_argument("--model-id", default="RoyalCities/Foundation-1", help="Hugging Face model id to download into the models directory.")
    parser.add_argument("--skip-model", action="store_true", help="Skip the Foundation model download.")
    parser.add_argument("--download-t5", action="store_true", help="Also save a local copy of t5-base into .cache/hf-models/t5-base.")
    args = parser.parse_args()

    config = load_config()
    models_dir = resolve_repo_path(config["models_directory"])
    t5_dir = CACHE_ROOT / "hf-models" / "t5-base"

    models_dir.mkdir(parents=True, exist_ok=True)
    t5_dir.parent.mkdir(parents=True, exist_ok=True)

    if not args.skip_model:
        download_model(args.model_id, models_dir)

    if args.download_t5:
        download_t5(t5_dir)


if __name__ == "__main__":
    main()
