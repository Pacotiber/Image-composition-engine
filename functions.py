from PIL import Image
import numpy as np
from classabstraite import *
from classfilters import *
from classblend import *
import yaml

BLENDS = {
    "normal": NormalBlend,
    "difference": DifferenceBlend,
    "darken": DarkenBlend,
    "multiply": MultiplyBlend,
    "colorburn": ColorBurnBlend,
    "linearburn": LinearBurn,
    "lighten": LigthenBlend,
    "screen": ScreenBlend,
    "colordodge": ColorDodgeBlend,
    "lineardodge": LinearDodgeBlend,
    "add": LinearDodgeBlend,
    "overlay": OverlayBlend,
    "softlight": SoftLightBlend,
    "hardlight": HardLightBlend,
    "vividlight": VividLightBlend,
    "linearlight": LinearLightBlend,
    "pinlight": PinLightBlend,
    "exclusion": ExclusionBlend,
}
FILTRES = {
    "normal": normal,
    "blur": blur,
    "gaussianblur": gaussianblur,
    "greyscale": Grayscale,
    "grayscale": Grayscale,
    "sepia": Sepia,
}

def array_from_file_rgba(path: str) -> np.ndarray:
    """Comme array_from_file, mais garde la transparence : forme (h, l, 4)."""
    img = Image.open(path).convert("RGBA")
    return np.array(img) / 255

def readfromyaml(path:str) ->dict:
    """this function reads the yaml file and turn it into a dict"""
    with open(path,encoding="utf-8",mode="r") as file:
       content= yaml.safe_load(file)
    return content


def buildlayers(content: dict) -> np.ndarray:
    finalimage = None
    for layer in content["layers"]:
        new_layer = array_from_file_rgba(layer["image"])
        for filtre in dicttolistfilters(layer.get("filters")):
            new_layer = filtre.apply(new_layer)
        blendingmode=layer.get("blend")
        nameblend=blendingmode.get("name") if blendingmode else None
        opacity=blendingmode.get("opacity") if blendingmode else 1.0
        finalimage = new_layer if finalimage is None else apply_blend(finalimage, new_layer, blendingmode)

    return np.clip(finalimage, 0, 1)
                    
def apply_filters(image: np.ndarray, filters: list[Filter]):
    for filter in filters:
        image = filter.apply(image)
    return image



def dicttolistfilters(filters: list[dict] | None) -> list[Filter]:
    """Transforme la liste 'filters' d'un calque du YAML en liste d'objets Filter."""
    listeoffilter: list[Filter] = []
    for f in filters or []:                    
        name = f["name"].strip().lower()
        params = f.get("params") or {}          
        listeoffilter.append(FILTRES[name](**params))
    return listeoffilter


def getblendingmode(name: str) -> Blend:
    key = name.strip().lower().replace("_", "").replace(" ", "")
    if key not in BLENDS:
        raise ValueError(f"Blend inconnu : '{name}' (disponibles : {list(BLENDS)})")
    return BLENDS[key]()

def apply_blend(background: np.ndarray, image: np.ndarray, blend: dict | None = None) -> np.ndarray:
    blend = blend or {}                                   # calque sans blend -> normal
    name = blend.get("name", "normal")
    opacity = float(blend.get("opacity", 1.0))
    mode = getblendingmode(name)

    # Le blend se calcule sur RGB uniquement (alpha à part)
    bg_rgb, bg_a = background[..., :3], background[..., 3:4]
    im_rgb, im_a = image[..., :3], image[..., 3:4]

    # Formule pure (opacité 1.0), puis interpolation avec le fond
    blended = np.clip(mode.apply(bg_rgb, im_rgb, 1.0), 0, 1)
    alpha = im_a * opacity                                # opacité du calque x alpha du PNG
    rgb = bg_rgb * (1 - alpha) + blended * alpha
    out_a = alpha + bg_a * (1 - alpha)

    return np.concatenate([rgb, out_a], axis=-1)
def array_to_img(arr: np.ndarray):
    adjusted =  np.array(np.clip(arr, 0, 1) * 255, dtype=np.uint8)
    pil_img = Image.fromarray(adjusted)
    return pil_img

def show_from_array(arr: np.ndarray):
    img = array_to_img(arr)
    img.show()
                
a=readfromyaml("modifications.yaml")
b=buildlayers(a)
c=show_from_array(b)
