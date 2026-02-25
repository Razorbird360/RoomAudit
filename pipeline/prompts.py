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
    "bath_towel": "bath towel",
    "bin":        "rubbish bin",
    "window":     "window",
}

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
        ("a muddy shoe print on the tiled floor",                             "stain"),
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
        ("a visible drink spill stain on the sofa cushion",                   "stain"),
        ("food crumbs scattered on the sofa cushions",                        "debris"),
    ],
    "bath_towel": [
        ("a dirty stained towel with visible brown marks",                    "stain"),
        ("a dirty stained towel hanging on the rack",                         "stain"),
        ("a towel left bundled on the bed",                                   "misplaced"),
    ],
    "bin": [
        ("an overflowing rubbish bin with trash spilling out",                "overflow"),
        ("a rubbish bin not emptied with visible waste inside",               "not_emptied"),
    ],
    "window": [
        ("curtains left open or half drawn in a messy state",                 "curtains"),
        ("dirty smudged window glass with visible fingerprints",              "smudge"),
    ],
}
