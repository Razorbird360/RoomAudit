# Normalises data/clean/ in-place:
#   - Resize any image where max(width, height) > 1920 → longest edge = 1920 px
#     (aspect ratio preserved, LANCZOS resampling)
#   - Snap both dimensions to nearest multiple of 16 (required by FLUX)
#   - Convert any PNG → JPG (quality=95), delete the original .png
#   - Print before/after stats (count, min/max/median longest edge)
#   - Idempotent — re-running is a no-op

from pathlib import Path
import statistics
from PIL import Image

MAX_EDGE = 1920
QUALITY = 95
SUPPORTED = {".jpg", ".jpeg", ".png"}

ROOT = Path(__file__).parent.parent
CLEAN_DIR = ROOT / "data" / "clean"

def main():
    if not CLEAN_DIR.is_dir():
        raise SystemExit(f"Directory not found: {CLEAN_DIR}")

    image_paths = sorted(p for p in CLEAN_DIR.iterdir() if p.suffix.lower() in SUPPORTED)

    # Print before stats
    edges_before = [max(Image.open(p).size) for p in image_paths]
    if edges_before:
        print(f"BEFORE: count={len(edges_before)}, min={min(edges_before)}, max={max(edges_before)}, median={statistics.median(edges_before):.0f}")
    else:
        print("BEFORE: no images found")

    resized = 0
    converted = 0

    for img_path in image_paths:
        img = Image.open(img_path).convert("RGB")
        w, h = img.size

        # Scale down if too large, then snap both dims to multiple of 16
        w_new, h_new = w, h
        if max(w, h) > MAX_EDGE:
            scale = MAX_EDGE / max(w, h)
            w_new, h_new = int(w * scale), int(h * scale)
        w_new = round(w_new / 16) * 16
        h_new = round(h_new / 16) * 16

        if (w_new, h_new) != (w, h):
            img = img.resize((w_new, h_new), Image.LANCZOS)
            resized += 1

        out_path = img_path.with_suffix(".jpg")
        img.save(out_path, "JPEG", quality=QUALITY)

        if img_path.suffix.lower() == ".png":
            img_path.unlink()
            converted += 1

    # Print after stats
    after_paths = sorted(p for p in CLEAN_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg"})
    edges_after = [max(Image.open(p).size) for p in after_paths]
    if edges_after:
        print(f"AFTER:  count={len(edges_after)}, min={min(edges_after)}, max={max(edges_after)}, median={statistics.median(edges_after):.0f}")

    print(f"Resized: {resized}  |  PNG→JPG converted: {converted}")


if __name__ == "__main__":
    main()
