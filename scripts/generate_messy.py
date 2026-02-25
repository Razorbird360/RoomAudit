# Loads SAM3 once, then for each image in data/clean/ runs every object prompt
# and prints what was detected. DEFECT_PROMPTS are defined here ready for FLUX
# inpainting in the next phase.
#
# Before running:
#   pip install git+https://github.com/facebookresearch/sam3.git
#   huggingface-cli login
#   huggingface-cli download facebook/sam3  (weights cached to ~/.cache/huggingface/hub/)


from pathlib import Path
from PIL import Image
from tqdm import tqdm
from huggingface_hub import hf_hub_download
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor

ROOT = Path(__file__).parent.parent
CLEAN_DIR = ROOT / "data" / "clean"
MODEL_ID = "facebook/sam3"
CONFIDENCE_THRESHOLD = 0.5

# SAM3 text prompts — what objects to look for in each image
OBJECT_PROMPTS = {
    "pillow":     "pillow",
    "bed_sheet":  "bed sheet",
    "blanket":    "blanket",
    "floor":      "floor",
    "carpet":     "carpet",
    "chair":      "chair",
    "desk":       "desk",
    "mirror":     "mirror",
    "sofa":       "sofa",
    "toilet":     "toilet bowl",
    "bath_towel": "bath towel",
    "sink":       "bathroom sink",
    "bin":        "rubbish bin",
    "window":     "window",
    "minibar":    "minibar",
}

# FLUX inpainting prompts — what defects to paint onto each object
# Each entry is a list of (flux_prompt, short_label) tuples.
DEFECT_PROMPTS = {
    "pillow": [
        ("a dark strand of hair lying across the white pillow",               "hair"),
        ("a visible yellow stain on the white pillow",                        "stain"),
        ("a pillow with a visible head indentation and creased pillowcase",   "crumpled"),
        ("a blood stain on the white pillow",                                 "stain"),
        ("a pillow missing its pillowcase exposing the bare pillow",          "missing_cover"),
    ],
    "bed_sheet": [
        ("crumpled used-looking sheets with visible body impressions",        "crumpled"),
        ("dark hairs scattered across the white bed sheet",                   "hair"),
        ("a brown stain on the white bed sheet",                              "stain"),
        ("a blood stain on the white bed sheet",                              "stain"),
        ("bedsheets pulled back and bunched up at the foot of the bed",       "unmade"),
    ],
    "blanket": [
        ("a crumpled bunched-up blanket not properly spread on the bed",      "crumpled"),
        ("dark hair strands on the white blanket cover",                      "hair"),
        ("a visible stain on the blanket cover",                              "stain"),
    ],
    "floor": [
        ("scattered dust and debris on the floor near the bed",               "debris"),
        ("a wet footprint stain on the tiled floor",                          "stain"),
        ("tissue paper left on the floor",                                    "litter"),
        ("food crumbs scattered on the floor",                                "debris"),
        ("a used plastic bag left on the floor",                              "litter"),
        ("a sauce or drink spill stain on the floor",                         "stain"),
    ],
    "carpet": [
        ("a visible stain on the carpet",                                     "stain"),
        ("food crumbs ground into the carpet",                                "debris"),
        ("a wet patch on the carpet",                                         "stain"),
    ],
    "chair": [
        ("crumbs and food debris scattered on the seat cushion",              "debris"),
        ("a visible stain on the fabric chair seat",                          "stain"),
        ("clothes left draped over the chair",                                "personal_item"),
    ],
    "desk": [
        ("food takeaway containers left on the desk",                         "litter"),
        ("used coffee cups and food wrappers on the desk",                    "litter"),
        ("a sticky spill stain on the desk surface",                          "stain"),
        ("a sauce or drink spill on the desk surface",                        "stain"),
    ],
    "mirror": [
        ("smudge marks and fingerprints on the mirror surface",               "smudge"),
        ("toothpaste splatter on the mirror",                                 "splatter"),
        ("a dirty streaked mirror with visible grime",                        "dirty"),
    ],
    "sofa": [
        ("visible indentation and creasing from recent use",                  "used"),
        ("food crumbs scattered on the sofa cushions",                        "debris"),
    ],
    "toilet": [
        ("brown limescale stains visible inside the toilet bowl",             "stain"),
    ],
    "bath_towel": [
        ("a used damp towel left crumpled on the floor",                      "used"),
        ("a dirty stained towel hanging on the rack",                         "stain"),
        ("a towel left bundled on the bed",                                   "misplaced"),
    ],
    "sink": [
        ("toothpaste splatter and soap residue around the sink basin",        "residue"),
        ("hair strands in the bathroom sink",                                 "hair"),
    ],
    "bin": [
        ("an overflowing rubbish bin with trash spilling out",                "overflow"),
        ("a rubbish bin not emptied with visible waste inside",               "not_emptied"),
    ],
    "window": [
        ("curtains left open or half drawn in a messy state",                 "curtains"),
    ],
    "minibar": [
        ("empty minibar bottles left out on the counter",                     "litter"),
        ("minibar items left scattered outside the fridge",                   "misplaced"),
    ],
}


LOG_FILE = Path(__file__).parent / "detections.txt"


def log(f, msg):
    print(msg)
    f.write(msg + "\n")


def main():
    if not CLEAN_DIR.is_dir():
        raise SystemExit(f"Directory not found: {CLEAN_DIR}")

    image_paths = sorted(CLEAN_DIR.glob("*.jpg"))
    if not image_paths:
        raise SystemExit(f"No .jpg images found in {CLEAN_DIR}")

    print(f"Loading SAM3 from {MODEL_ID} ...")
    checkpoint = hf_hub_download(repo_id=MODEL_ID, filename="sam3.pt")
    model = build_sam3_image_model(checkpoint_path=checkpoint)
    processor = Sam3Processor(model)
    print(f"SAM3 loaded. Processing {len(image_paths)} images ...\n")

    with open(LOG_FILE, "w") as f:
        for img_path in tqdm(image_paths, desc="Scanning images"):
            log(f, f"[{img_path.name}]")
            image = Image.open(img_path).convert("RGB")
            state = processor.set_image(image)

            any_detected = False
            for obj_key, sam_prompt in OBJECT_PROMPTS.items():
                output = processor.set_text_prompt(state=state, prompt=sam_prompt)
                scores = output.get("scores", [])
                if hasattr(scores, "tolist"):
                    scores = scores.tolist()
                if scores and max(scores) >= CONFIDENCE_THRESHOLD:
                    log(f, f"  '{sam_prompt}' detected (score={max(scores):.2f})")
                    any_detected = True
                    # TODO: pass output["masks"] + DEFECT_PROMPTS[obj_key] to FLUX

            if not any_detected:
                log(f, "  (no objects detected above threshold)")
            log(f, "")


if __name__ == "__main__":
    main()
