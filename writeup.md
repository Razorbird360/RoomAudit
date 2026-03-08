# RoomAudit — writeup

## Overview

roomaudit is an automated hotel room cleanliness inspector. Given a photo of a hotel room, it returns a structured JSON verdict: clean or messy, with a list of detected defects (object, defect type, description). No labelled messy room dataset exists publicly, so the full training pipeline was built around synthetic data generation.

---

## Synthetic Data Pipeline

The core challenge was the absence of labelled training data. The pipeline generates messy room images synthetically from clean ones:

1. **Image sourcing** — 218 clean hotel room images collected from Unsplash, Pexels, and Flickr.
2. **Segmentation** — SAM3 (Meta, ~848M params) segments named objects in each image using text prompts and saves binary masks.
3. **Inpainting** — FLUX.1 Fill Dev inpaints defects onto segmented regions using ~35 curated defect prompts. Up to 3 defects are stacked per variant, and 3 messy variants are produced per clean image, giving 654 synthetic messy images.
4. **Dataset** — Clean images are repeated 3x to balance the 1:1 clean/messy ratio. Final dataset: 1308 rows, 85/15 train/eval split.

SAM3 and FLUX can't coexist in 16GB VRAM, so the pipeline runs in two sequential phases with VRAM cleared between them. Crash-resume logic means overnight runs can be interrupted without losing progress.

---

## Training

All training used Qwen3-VL-4B-Instruct with 4-bit QLoRA via Unsloth (r=32) on the 1308-row balanced dataset. Three approaches were explored.

**LLM-only, single-turn (4 runs):**
The model receives the full room image and returns a verdict in one pass. After fixing a class imbalance bug in run 1, runs 2-4 converged to a stable ceiling: F1 0.774, precision 0.676, recall 0.906. The eval loss floor (~0.036) was identical across all runs regardless of LR or epoch count, indicating data quality is the bottleneck rather than training configuration.

**ViT + LLM (1 run):**
Added LoRA to the vision encoder as well as the language layers. Performance got worse (F1 0.722, 89% false positive rate on clean rooms). The ViT adapters learned to detect FLUX inpainting artefacts as a proxy for the messy class, since every messy image was inpainted and no clean images were. Fine-tuning the vision encoder on this dataset is counterproductive.

**Agentic two-turn (2 runs):**
A two-turn format where the model first scouts 1-2 regions to inspect, then gives a final verdict after seeing the crops. Both runs scored below the single-turn baseline (best F1 0.740, clean room accuracy 40-56%). The two-turn format amplifies spurious patterns from the synthetic data, and the scout step appears to create a false association between close inspection and defect presence. Cleaner inpainting data is a prerequisite before this approach can be fairly evaluated.

**Best results (LLM-only, run 4):** *(note: the web app runs the agentic adapter by default — change `ADAPTER_PATH` in `backend/model.py` to switch)*

>`lora_adapter` has better classification accuracy. `lora_adapter_agent` has better region selection for the crop inspection step. Use the former if you only care about the final verdict, the latter to demonstrate crop reasoning.

| Metric | Score |
|---|---|
| Accuracy | 0.714 |
| Precision | 0.676 |
| Recall | 0.906 |
| F1 | 0.774 |

All three adapters and the training dataset are published at [huggingface.co/RanenSim/RoomAudit-Lora](https://huggingface.co/RanenSim/RoomAudit-Lora).

Full project log including model choices, rejected alternatives, and detailed run notes: [docs/documentation.md](docs/documentation.md).

---

## Key Findings

- The guidance_scale=30 inpainting ceiling dominates all results. Lowering to guidance_scale=10 for more realistic synthetic defects is the highest-priority next step.
- ViT fine-tuning backfires on synthetic data because artefact detection is an easier signal than actual defect detection. Worth revisiting once data quality improves.
- The agentic format is architecturally sound for ambiguous borderline cases, but is more sensitive to data quality than single-turn and needs cleaner data to evaluate fairly.
- Recall of 0.906 is strong (few missed messy rooms), but the ~32% false positive rate on clean rooms is the main weakness.

---

## Future Work

### Data quality
- **Re-run inpainting at guidance_scale=10** — the most impactful change available. guidance_scale=30 produces over-saturated, dramatic defects; 10 keeps texture much closer to the source image. All three training approaches should be re-evaluated on new data before drawing final conclusions.
- **Expand the clean image set** — 218 is a small base. More variety in room layouts and lighting conditions would improve generalisation.
- **Mix in real messy images** — even a small number of real labelled examples would help close the domain gap between synthetic and real-world defects.

### Model scale
- **Qwen3-VL-8B** — the 4B model was constrained by 16GB VRAM. The 8B variant (~24GB base) is feasible on cloud hardware and should handle subtle defects better with its stronger visual prior.
- **Higher LoRA rank** — currently r=32. Increasing to r=64 or r=128 becomes more relevant as data quality improves and the current rank becomes the bottleneck.
- **ViT fine-tuning on guidance_scale=10 data** — with more realistic synthetic defects, the visual difference between clean and messy is more authentic. The vision encoder may genuinely benefit from adaptation once the artefact shortcut is removed.

### Agentic format
- **Re-run on guidance_scale=10 data** — the architecture is worth a fair evaluation with cleaner training signal.
- **GRPO reward fine-tuning** — the two-turn format is a natural fit for reward-based training: reward correct final verdicts where the scout regions were genuinely informative. This would be a meaningful improvement over pure SFT for the agentic case.
- **More crop regions and adaptive crop resolution** — currently 1-2 crops at fixed bounding box scale. Allowing more regions for complex rooms and scaling crop resolution to the size of the requested area would improve the quality of the scout step.

### Pipeline
- **Keep FLUX transformer in VRAM** — `enable_model_cpu_offload()` causes heavy SSD thrash between images as the transformer swaps in and out. Keeping the transformer in VRAM and offloading only T5 would speed up inpainting substantially.
- **Cloud for future inpainting runs** — the 42-hour local run could take a few hours on an A100 (~$6-8 on Vast.ai), making it practical to iterate on guidance_scale settings quickly.

### Evaluation
- **Real-world test set** — the model has only been evaluated on held-out synthetic samples. A set of real hotel room photos would give a more meaningful accuracy figure.
- **Defect-level evaluation** — currently the metric is binary clean/messy. Evaluating whether the reported defect objects and types are correct would reveal whether the model is making accurate attributions or just getting the label right by coincidence.
