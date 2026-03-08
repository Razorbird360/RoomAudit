# Agentic training runs — FLUX guidance_scale=30

Two-turn agentic format: the model first scouts 1-2 regions to inspect (Round 1), then gives a final cleanliness verdict after seeing the crops (Round 2). Both runs used the same synthetic dataset as the LLM-only and ViT runs. The data quality ceiling from guidance_scale=30 still applies here, and the agentic format turned out to add its own training challenges on top.

---

## Run 1

Qwen3-VL-4B, QLoRA r=32, lr=1e-4, 4 epochs, batch 2 x grad_accum 4, EarlyStoppingCallback(patience=4). Same balanced dataset as LLM-only runs (3x clean upsampling, 654:654). Scout prompt: "Focus on areas most likely to have defects". Clean crops: 2 largest mask objects (no defect-prone targeting), same pair repeated across all 3 clean repeats.

- F1: 0.740
- Clean room accuracy: 56.4%

Loss curve was healthy — no overfitting, train and eval tracked together. Best checkpoint around step 480, early stopping didn't trigger (ran all 550 steps). F1 is worse than the single-turn baseline (0.774), and clean accuracy of 56.4% is basically a coin flip.

### Issues identified

Three data problems and one hyperparameter problem:

**Scout prompt bias** — "Focus on areas most likely to have defects" primes the model to look for defects before Round 2 even starts. On clean images, the model enters Round 2 already in defect-finding mode and invents problems in the crops.

**Wrong crops for clean samples** — `preferred_obj=None` picks the 2 largest masks, which tend to be large flat surfaces like desks and windows. The model never learns "I looked at the pillow and it was clean." It only sees surfaces that rarely carry defects, so it has no clean training signal for the objects that matter.

**Identical clean repeats** — all 3 clean repeats for a given image use the same crop pair. The model gets 3 copies of the same sample with no variety, which just reinforces whatever it picked up the first time rather than building a robust clean-room representation.

**LR** — 1e-4 is fine for single-turn but the agentic loss landscape is noisier (two turns, longer sequences). The model ran all 550 steps without early stopping, suggesting slight overtraining on messy patterns near the end.

Fix: neutral scout prompt, cycle preferred object across the 3 clean repeats (pillow → bed_sheet → floor → ...), add "If no defects are visible, set clean=true" to the Round 2 prompt, lower LR to 5e-5, loosen early stopping to patience=6. See run 2.

---

## Run 2

Same model (Qwen3-VL-4B, r=32). Neutral scout prompt ("Choose regions that would give the most useful evidence about cleanliness"). Clean crops now cycle through defect-prone objects per repeat (`CLEAN_PREFERRED_OBJS = ["pillow", "bed_sheet", "floor", "carpet", "chair", "bin", "bath_towel"]`). Added explicit clean-path sentence to Round 2 prompt. lr=5e-5, epochs=15, EarlyStoppingCallback(patience=6). Best checkpoint: step 1075, eval_loss 0.051568. Early stopping triggered at step 1225 (~epoch 8.8).

- Accuracy: 0.663
- Precision: 0.622
- Recall: 0.902
- F1: 0.736

Confusion matrix:
```
TN=38  FP=56
FN=10  TP=92
```

Clean accuracy: 40% (38/94). Worse than run 1 despite the data fixes.

Loss curve was clean and steady from step 25 to around step 1075, then plateaued with oscillation while train loss kept falling to ~0.013. Overfitting onset confirmed at step 1075 — the best checkpoint is correct, but the gap between train (0.013) and eval (0.051) at that point shows the model had already started to overfit messy patterns.

The data fixes didn't move the needle on clean accuracy — it actually got worse (40% vs 56%). The agentic format is harder to train on guidance_scale=30 synthetic data than single-turn. The likely reason: clean room crops of a pillow or floor are visually very similar to a FLUX-inpainted messy room with subtle stains, and the two-turn format gives the model more chances to find spurious patterns in those crops. The scout step may also be creating a false signal — the model learns to associate "inspecting an area closely → defect present" regardless of what it actually sees.

Both agentic runs are below the single-turn baseline (F1 0.774). The agentic format on guidance_scale=30 data is not an improvement. Will revisit after re-running inpainting at guidance_scale=10 for cleaner synthetic defects.
