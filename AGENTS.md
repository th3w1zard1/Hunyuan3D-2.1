# Repository Agent Instructions

- Treat `python scripts/push_hf_space.py` as the canonical Hugging Face Space deployment path. Do not switch back to `hub-sync` or ad hoc uploads for validation work.
- When a task affects the Space runtime or UI, complete this loop without skipping steps:
  1. Run the narrowest local test or compile check first.
  2. Commit the validated change.
  3. Push the current commit with `python scripts/push_hf_space.py`.
  4. Wait for the Space rebuild to finish.
  5. Open the public Space and validate generate, export, and download with `assets/example_images/jimeng2.png`.
  6. If Hugging Face runtime behavior changed, validate HF CPU and HF ZeroGPU sequentially by switching the same Space hardware, because one Space cannot expose both modes simultaneously.
  7. If any step fails, fix the smallest affected slice and repeat the same loop.
- Preserve all five runtime profiles when editing startup logic: local GPU, local CPU, HF GPU, HF CPU, and HF ZeroGPU. Shape generation and export must remain available even when texture generation is disabled by fallback.
- Keep ZeroGPU on the Gradio SDK path and preserve `@spaces.GPU` on GPU-dependent functions.
- Surface the active runtime mode in user-visible output or stats whenever you change runtime-selection behavior.
- Never print or commit tokens, credentials, or other secrets.