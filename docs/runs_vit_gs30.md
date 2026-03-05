# ViT training runs — FLUX guidance_scale=30

Tested whether adding LoRA adapters to the vision encoder on top of the LLM improves classification. The run used the same synthetic dataset as the LLM-only runs and showed a clear failure mode — the ViT learns FLUX inpainting artefacts rather than actual defects.

---

## ViT Run 1

Qwen3-VL-4B, QLoRA r=32, alpha=16, lr=5e-5, 10 epochs (early stopped), batch 2 x grad_accum 4. finetune_vision_layers=True, lora_dropout=0.10, warmup_ratio=0.10, EarlyStoppingCallback(patience=2). Same balanced dataset as LLM-only runs (3x clean upsampling, 1:1 ratio).

- Accuracy: 0.587
- Precision: 0.568
- Recall: 0.991
- F1: 0.722

Train and eval loss tracked together cleanly. Early stopping triggered at ~step 500, best checkpoint at ~step 450.

### Issue: structural messy bias

Confusion matrix:
```
TN=10  FP=80
FN=1   TP=105
```

The model predicted messy for 80 out of 90 clean rooms (89% false positive rate). Lowering alpha (32→16) and raising dropout (0.05→0.10) made no difference. The problem is not regularisation strength.

The issue is that at guidance_scale=30 the FLUX images have a very distinctive texture. That texture shows up in every messy image and nowhere in the clean ones, so it's by far the easiest thing for the ViT adapters to latch onto. The ViT ends up learning to detect whether an image was inpainted rather than whether the room is dirty.

What makes the false positives so bad is that fine-tuning the ViT also changes how clean rooms get encoded. The adapted ViT is now tuned toward patterns that don't exist in real photos, so when it sees a clean room the resulting image tokens don't clearly signal "clean" anymore. The LLM never gets a useful representation of the clean room to work from.

The LLM-only model handles this better because the ViT is frozen and still encodes images normally. The LLM adapters learn from real image content rather than from a distorted view, which is why the clean room recall is so much higher even on the same dataset.

All metrics are worse than LLM-only run 4 (F1 0.722 vs 0.774, Accuracy 0.587 vs 0.714). ViT fine-tuning on guidance_scale=30 data is counterproductive. Will revisit after re-running inpainting at guidance_scale=10.

---
