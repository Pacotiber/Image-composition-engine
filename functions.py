from PIL import Image
import numpy as np
from classabstraite import *
from classfilters import *
from classblend import *
import yaml

# Associe le nom d'un blend dans le YAML à sa classe
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
# Associe le nom d'un filtre dans le YAML à sa classe
FILTRES = {
    "normal": normal,
    "blur": blur,
    "gaussianblur": gaussianblur,
    "greyscale": Grayscale,
    "sepia": Sepia,
    "blackborder": blackborder
}

def array_from_file_rgba(path: str) -> np.ndarray:
    """Charge une image en RGBA et la renvoie en tableau (h, l, 4) de valeurs dans [0, 1]."""
    img = Image.open(path).convert("RGBA")
    return np.array(img) / 255

def readfromyaml(path:str) ->dict:
    """Lit le fichier YAML (en UTF-8) et le renvoie sous forme de dictionnaire."""
    with open(path,encoding="utf-8",mode="r") as file:
       content= yaml.safe_load(file)
    return content


def buildlayers(content: dict) -> np.ndarray:
    """Construit l'image finale : charge chaque calque, applique ses filtres,
    puis le mélange sur le résultat précédent avec son blend. Le premier calque sert de fond."""
    finalimage = None
    for layer in content["layers"]:
        new_layer = array_from_file_rgba(layer["image"])
        for filtre in dicttolistfilters(layer.get("filters")):
            new_layer = filtre.apply(new_layer)
        blendingmode=layer.get("blend")
        nameblend=blendingmode.get("name") if blendingmode and isinstance(blendingmode.get("name"),str) else None
        opacity= blendingmode.get("opacity") if blendingmode and isinstance(blendingmode.get("opacity"),float) else 1.0
        opacity = max(0, min(opacity, 1.0))
        finalimage = new_layer if finalimage is None else apply_blend(finalimage, new_layer, blendingmode)

    return np.clip(finalimage, 0, 1)
                    
def apply_filters(image: np.ndarray, filters: list[Filter]):
    """Applique une liste de filtres à une image, dans l'ordre, et renvoie le résultat."""
    for filter in filters:
        image = filter.apply(image)
    return image



def dicttolistfilters(filters: list[dict] | None) -> list[Filter]:
    """Transforme la liste 'filters' d'un calque du YAML en liste d'objets Filter.
    Lève une ValueError si le nom du filtre est inconnu."""
    listeoffilter: list[Filter] = []
    for f in filters or []:  
        try:                 
            name = f["name"].strip().lower()
            params = f.get("params") or {}          
            listeoffilter.append(FILTRES[name](**params))
        except KeyError:
            raise ValueError(f"Filtre inconnu : '{name}' (disponibles : {list(FILTRES)})")
    return listeoffilter


def getblendingmode(name: str) -> Blend:
    """Renvoie une instance de Blend à partir de son nom (casse, '_' et espaces ignorés)."""
    key = name.strip().lower().replace("_", "").replace(" ", "")
    if key not in BLENDS:
        raise ValueError(f"Blend inconnu : '{name}' (disponibles : {list(BLENDS)})")
    return BLENDS[key]()

def apply_blend(background: np.ndarray, image: np.ndarray, blend: dict | None = None) -> np.ndarray:
    """Mélange un calque sur le fond selon son blend (name) et son opacité (opacity).
    Le blend est calculé sur RGB, puis pondéré par l'alpha du calque x l'opacité."""
    blend = blend or {}                                   # calque sans blend -> normal
    name = blend.get("name","normal")
    opacity =float(blend.get("opacity",1.0))
    mode= getblendingmode(name)
    bg_rgb = background[..., :3]
    bg_a = background[..., 3:4]
    im_rgb= image[..., :3]
    if(len(bg_rgb)==len(im_rgb)):
        raise ValueError(f"Les dimensions du fond {bg_rgb.shape} et du calque {im_rgb.shape} ne correspondent pas.")
    calque_a =image[..., 3:4] #on recup la veleure de A pour le calque
    blende = np.clip(mode.apply(bg_rgb, im_rgb, 1.0), 0, 1)
    alpha = calque_a* opacity  # opacité du calque x alpha de l'image 
    rgb = bg_rgb*(1 - alpha) +blende* alpha #moyenne pondérée entre le fond et le calque
    out_a= alpha+ bg_a *(1 -alpha)
    return np.concatenate([rgb, out_a], axis=-1) #on recole les caunaux r,g,b,a

def array_to_img(arr: np.ndarray):
    """Convertit un tableau de valeurs dans [0, 1] en image PIL (entiers 0-255)."""
    adjusted =  np.array(np.clip(arr, 0, 1) * 255, dtype=np.uint8)
    pil_img = Image.fromarray(adjusted)
    return pil_img

def show_from_array(arr: np.ndarray):
    """Convertit un tableau en image et l'ouvre dans le visionneur par défaut."""
    img = array_to_img(arr)
    img.show()