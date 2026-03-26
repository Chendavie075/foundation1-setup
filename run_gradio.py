import os
from pathlib import Path

import torch

from stable_audio_tools.interface.gradio import create_ui


REPO_ROOT = Path(__file__).resolve().parent
CACHE_ROOT = REPO_ROOT / ".cache"


def ensure_localhost_bypasses_proxy():
    loopback_hosts = ["127.0.0.1", "localhost"]
    for key in ("NO_PROXY", "no_proxy"):
        current = os.environ.get(key, "").strip()
        if not current:
            os.environ[key] = ",".join(loopback_hosts)
            continue

        entries = [item.strip() for item in current.split(",") if item.strip()]
        missing = [host for host in loopback_hosts if host not in entries]
        if missing:
            os.environ[key] = ",".join(entries + missing)


def ensure_runtime_cache_dirs():
    hf_home = CACHE_ROOT / "hf"
    hf_hub_cache = hf_home / "hub"
    tmp_dir = CACHE_ROOT / "tmp"
    numba_dir = CACHE_ROOT / "numba"
    candidate_t5_dirs = [
        CACHE_ROOT / "hf-models" / "t5-base",
        REPO_ROOT.parent / "hf-models" / "t5-base",
    ]

    for path in (hf_home, hf_hub_cache, tmp_dir, numba_dir):
        path.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("HF_HOME", str(hf_home))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(hf_hub_cache))

    # Windows + numba/librosa can hang on some system temp paths; keep these local to the repo.
    os.environ["TEMP"] = str(tmp_dir)
    os.environ["TMP"] = str(tmp_dir)
    os.environ["NUMBA_CACHE_DIR"] = str(numba_dir)

    for t5_dir in candidate_t5_dirs:
        if t5_dir.is_dir():
            os.environ.setdefault("FOUNDATION_T5_PATH", str(t5_dir))
            break


def patch_transformers_audio_imports():
    try:
        import transformers.utils as transformers_utils
        from transformers.utils import import_utils as transformers_import_utils
    except Exception:
        return

    def _false():
        return False

    transformers_utils.is_librosa_available = _false
    transformers_import_utils.is_librosa_available = _false


def patch_gradio_local_network_checks():
    try:
        import gradio.blocks as gradio_blocks
        import gradio.networking as gradio_networking
    except Exception:
        return

    if getattr(gradio_blocks, "_foundation_localhost_patch", False):
        return

    def _should_bypass_proxy(url):
        url = str(url)
        return url.startswith("http://127.0.0.1") or url.startswith("http://localhost") or url.startswith("https://127.0.0.1") or url.startswith("https://localhost")

    original_get = gradio_blocks.httpx.get
    original_head = gradio_networking.httpx.head

    def _patched_get(url, *args, **kwargs):
        if _should_bypass_proxy(url):
            kwargs.setdefault("trust_env", False)
        return original_get(url, *args, **kwargs)

    def _patched_head(url, *args, **kwargs):
        if _should_bypass_proxy(url):
            kwargs.setdefault("trust_env", False)
        return original_head(url, *args, **kwargs)

    gradio_blocks.httpx.get = _patched_get
    gradio_networking.httpx.head = _patched_head
    gradio_blocks._foundation_localhost_patch = True


def prepare_runtime():
    ensure_localhost_bypasses_proxy()
    ensure_runtime_cache_dirs()
    patch_transformers_audio_imports()
    patch_gradio_local_network_checks()


def main(args):
    torch.manual_seed(42)
    prepare_runtime()

    interface = create_ui(
        model_config_path=args.model_config,
        ckpt_path=args.ckpt_path,
        pretrained_name=args.pretrained_name,
        pretransform_ckpt_path=args.pretransform_ckpt_path,
        model_half=args.model_half,
        gradio_title=args.title,
    )
    interface.queue()
    interface.launch(
        share=args.share,
        auth=(args.username, args.password) if args.username is not None else None,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run gradio interface")
    parser.add_argument("--pretrained-name", type=str, help="Name of pretrained model", required=False)
    parser.add_argument("--model-config", type=str, help="Path to model config", required=False)
    parser.add_argument("--ckpt-path", type=str, help="Path to model checkpoint", required=False)
    parser.add_argument("--pretransform-ckpt-path", type=str, help="Optional to model pretransform checkpoint", required=False)
    parser.add_argument("--share", action="store_true", help="Create a publicly shareable link", required=False)
    parser.add_argument("--username", type=str, help="Gradio username", required=False)
    parser.add_argument("--password", type=str, help="Gradio password", required=False)
    parser.add_argument("--model-half", action="store_true", help="Whether to use half precision", required=False, default=True)
    parser.add_argument("--title", type=str, help="Display Title top of Gradio", required=False)
    args = parser.parse_args()
    main(args)
