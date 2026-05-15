# Hunyuan 3D is licensed under the TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT
# except for the third-party components listed below.
# Hunyuan 3D does not impose any additional limitations beyond what is outlined
# in the repsective licenses of these third-party components.
# Users must comply with all terms and conditions of original licenses of these third-party
# components and must ensure that the usage of the third party components adheres to
# all relevant laws and regulations.

# For avoidance of doubts, Hunyuan 3D means the large language models and
# their software and algorithms, including trained model weights, parameters (including
# optimizer states), machine-learning model code, inference-enabling code, training-enabling code,
# fine-tuning enabling code and other elements of the foregoing made publicly available
# by Tencent in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT.

import logging
import os
from functools import wraps

import torch


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


logger = get_logger('hy3dgen.shapgen')


SHAPE_MODEL_FALLBACKS = {
    'tencent/Hunyuan3D-2.1': [
        ('tencent/Hunyuan3D-2.1', 'hunyuan3d-dit-v2-1'),
        ('tencent/Hunyuan3D-2', 'hunyuan3d-dit-v2-0'),
        ('tencent/Hunyuan3D-2mini', 'hunyuan3d-dit-v2-mini'),
    ],
}


def _shape_model_candidates(model_path, subfolder):
    explicit_fallbacks = os.environ.get('HY3D_MODEL_FALLBACKS', '').strip()
    candidates = [(model_path, subfolder)]

    if explicit_fallbacks:
        for item in explicit_fallbacks.split(','):
            item = item.strip()
            if not item:
                continue
            if ':' in item:
                repo_id, candidate_subfolder = item.rsplit(':', 1)
            else:
                repo_id, candidate_subfolder = item, subfolder
            candidate = (repo_id.strip(), candidate_subfolder.strip())
            if candidate not in candidates:
                candidates.append(candidate)
        return candidates

    for candidate in SHAPE_MODEL_FALLBACKS.get(model_path, []):
        if candidate not in candidates:
            candidates.append(candidate)
    return candidates


def _direct_model_dir(model_path, subfolder):
    direct_root = os.path.expanduser(model_path)
    direct_dir = os.path.join(direct_root, subfolder)
    if os.path.exists(direct_dir):
        return direct_root, direct_dir
    return None, None


def _cached_model_dir(base_dir, model_path, subfolder):
    cache_root = os.path.expanduser(os.path.join(base_dir, model_path))
    cache_dir = os.path.join(cache_root, subfolder)
    return cache_root, cache_dir


class synchronize_timer:
    """ Synchronized timer to count the inference time of `nn.Module.forward`.

        Supports both context manager and decorator usage.

        Example as context manager:
        ```python
        with synchronize_timer('name') as t:
            run()
        ```

        Example as decorator:
        ```python
        @synchronize_timer('Export to trimesh')
        def export_to_trimesh(mesh_output):
            pass
        ```
    """

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        """Context manager entry: start timing."""
        if os.environ.get('HY3DGEN_DEBUG', '0') == '1':
            self.start = torch.cuda.Event(enable_timing=True)
            self.end = torch.cuda.Event(enable_timing=True)
            self.start.record()
            return lambda: self.time

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Context manager exit: stop timing and log results."""
        if os.environ.get('HY3DGEN_DEBUG', '0') == '1':
            self.end.record()
            torch.cuda.synchronize()
            self.time = self.start.elapsed_time(self.end)
            if self.name is not None:
                logger.info(f'{self.name} takes {self.time} ms')

    def __call__(self, func):
        """Decorator: wrap the function to time its execution."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
            return result

        return wrapper


def smart_load_model(
    model_path,
    subfolder,
    use_safetensors,
    variant,
):
    original_model_path = model_path
    base_dir = os.environ.get('HY3DGEN_MODELS', '~/.cache/hy3dgen')
    resolved_model_path = None
    last_error = None

    for candidate_model_path, candidate_subfolder in _shape_model_candidates(original_model_path, subfolder):
        direct_root, direct_dir = _direct_model_dir(candidate_model_path, candidate_subfolder)
        if direct_dir is not None:
            logger.info(f'Try to load model from direct local path: {direct_dir}')
            resolved_model_path = direct_dir
            break

        model_fld, candidate_model_dir = _cached_model_dir(base_dir, candidate_model_path, candidate_subfolder)
        logger.info(f'Try to load model from cache path: {candidate_model_dir}')
        if os.path.exists(candidate_model_dir):
            resolved_model_path = candidate_model_dir
            break

        logger.info('Model path not exists, try to download from huggingface')
        try:
            from huggingface_hub import snapshot_download
            path = snapshot_download(
                repo_id=candidate_model_path,
                allow_patterns=[f"{candidate_subfolder}/*"],
                local_dir=model_fld,
            )
            resolved_model_path = os.path.join(path, candidate_subfolder)
            if (candidate_model_path, candidate_subfolder) != (original_model_path, subfolder):
                logger.warning(
                    "Falling back from %s/%s to %s/%s",
                    original_model_path,
                    subfolder,
                    candidate_model_path,
                    candidate_subfolder,
                )
            break
        except ImportError:
            logger.warning(
                "You need to install HuggingFace Hub to load models from the hub."
            )
            raise RuntimeError(f"Model path {candidate_model_dir} not found")
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Failed to load model candidate %s/%s: %s",
                candidate_model_path,
                candidate_subfolder,
                exc,
            )

    if resolved_model_path is None:
        if last_error is not None:
            raise last_error
        raise FileNotFoundError(f"Model path {original_model_path} not found")

    extension = 'ckpt' if not use_safetensors else 'safetensors'
    variant = '' if variant is None else f'.{variant}'
    ckpt_name = f'model{variant}.{extension}'
    config_path = os.path.join(resolved_model_path, 'config.yaml')
    ckpt_path = os.path.join(resolved_model_path, ckpt_name)
    return config_path, ckpt_path
