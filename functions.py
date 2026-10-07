
from PIL import Image
import numpy as np
from classabstraite import *
from classfilters import *
from classblend import *
import yaml


# Dictionnaire qui associe le nom donné dans le YAML
# à la classe de blend correspondante.
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


# Dictionnaire qui associe le nom donné dans le YAML
# à la classe de filtre correspondante.
FILTRES = {
    "normal": normal,
    "blur": blur,
    "gaussianblur": gaussianblur,
    "greyscale": Grayscale,
    "sepia": Sepia,
    "blackborder": blackborder
}


def array_from_file_rgba(path: str) -> np.ndarray:
    """
    Charge une image depuis un fichier et la transforme
    en tableau NumPy avec 4 canaux : R, G, B et A.

    Les valeurs sont normalisées entre 0 et 1.
    A = transparence de l'image.
    """

    # On ouvre l'image et on force le format RGBA
    img = Image.open(path).convert("RGBA")

    # On transforme l'image en tableau NumPy
    # puis on divise par 255 pour avoir des valeurs entre 0 et 1.
    return np.array(img) / 255


def readfromyaml(path: str) -> dict:
    """
    Lit un fichier YAML et le transforme en dictionnaire Python.

    Exemple :
        layers:
          - image: photo.jpg
    """

    # Ouverture du fichier YAML
    with open(path, encoding="utf-8", mode="r") as file:

        # safe_load transforme le YAML en dictionnaire Python
        content = yaml.safe_load(file)

    return content


def buildlayers(content: dict) -> np.ndarray:
    """
    Construit l'image finale à partir de tous les calques
    présents dans le fichier YAML.

    Pour chaque calque :
    1. On charge l'image.
    2. On applique ses filtres.
    3. On applique son blend avec l'image finale.
    """

    # Au début, il n'y a encore aucune image finale.
    finalimage = None

    # On parcourt tous les calques du fichier YAML.
    for layer in content["layers"]:

        # Chargement de l'image du calque.
        new_layer = array_from_file_rgba(layer["image"])

        # On récupère les filtres du calque
        # et on les transforme en objets Filter.
        for filtre in dicttolistfilters(layer.get("filters")):

            # On applique le filtre à l'image.
            new_layer = filtre.apply(new_layer)

        # On récupère les informations concernant le blend.
        blendingmode = layer.get("blend")

        # Récupération du nom du blend.
        # Si le nom n'existe pas ou n'est pas une chaîne,
        # on utilise None.
        nameblend = (
            blendingmode.get("name")
            if blendingmode and isinstance(blendingmode.get("name"), str)
            else None
        )

        # Récupération de l'opacité.
        # Si aucune opacité n'est donnée, on utilise 1.0.
        opacity = (
            blendingmode.get("opacity")
            if blendingmode and isinstance(blendingmode.get("opacity"), float)
            else 1.0
        )

        # On force l'opacité à rester entre 0 et 1.
        opacity = max(0, min(opacity, 1.0))

        # Si c'est le premier calque, il devient directement
        # notre image finale.
        #
        # Sinon, on mélange le nouveau calque avec
        # l'image finale déjà construite.
        finalimage = (
            new_layer
            if finalimage is None
            else apply_blend(finalimage, new_layer, blendingmode)
        )

    # On s'assure que toutes les valeurs sont bien
    # comprises entre 0 et 1.
    return np.clip(finalimage, 0, 1)


def apply_filters(image: np.ndarray, filters: list[Filter]):
    """
    Applique une liste de filtres à une image.

    Les filtres sont appliqués dans l'ordre dans lequel
    ils apparaissent dans la liste.
    """

    # On parcourt tous les filtres.
    for filter in filters:

        # Le résultat du filtre devient l'image
        # utilisée par le filtre suivant.
        image = filter.apply(image)

    return image


def dicttolistfilters(filters: list[dict] | None) -> list[Filter]:
    """
    Transforme la liste de filtres provenant du YAML
    en une liste d'objets Filter.

    Exemple YAML :

        filters:
          - name: grayscale
          - name: blur
            params:
              taille: 5
    """

    # Liste qui contiendra les objets Filter.
    listeoffilter: list[Filter] = []

    # Si aucun filtre n'est présent, on utilise une liste vide.
    for f in filters or []:

        try:
            # On récupère le nom du filtre.
            # strip() enlève les espaces inutiles.
            # lower() transforme le nom en minuscules.
            name = f["name"].strip().lower()

            # On récupère les paramètres du filtre.
            # Si aucun paramètre n'existe, on utilise {}.
            params = f.get("params") or {}

            # On récupère la classe correspondante dans FILTRES
            # puis on crée une instance de cette classe.
            #
            # **params permet de transmettre les paramètres
            # du YAML au constructeur du filtre.
            listeoffilter.append(FILTRES[name](**params))

        except KeyError:

            # Si le filtre n'existe pas dans notre dictionnaire,
            # on affiche une erreur avec les filtres disponibles.
            raise ValueError(
                f"Filtre inconnu : '{name}' "
                f"(disponibles : {list(FILTRES)})"
            )

    return listeoffilter


def getblendingmode(name: str) -> Blend:
    """
    Récupère le bon objet Blend à partir de son nom.

    Exemple :
        "multiply" -> MultiplyBlend()
    """

    # On nettoie le nom :
    # - strip() enlève les espaces au début et à la fin
    # - lower() met en minuscules
    # - replace() enlève les espaces et "_"
    key = name.strip().lower().replace("_", "").replace(" ", "")

    # On vérifie que le blend existe.
    if key not in BLENDS:

        raise ValueError(
            f"Blend inconnu : '{name}' "
            f"(disponibles : {list(BLENDS)})"
        )

    # On crée et retourne l'objet Blend correspondant.
    return BLENDS[key]()


def apply_blend(
    background: np.ndarray,
    image: np.ndarray,
    blend: dict | None = None
) -> np.ndarray:
    """
    Mélange une image avec une image de fond.

    background :
        Image déjà construite.

    image :
        Nouveau calque à ajouter.

    blend :
        Dictionnaire contenant le mode de blend et l'opacité.

    Le résultat contient toujours 4 canaux :
        R, G, B, A
    """

    # Si aucun blend n'est donné, on utilise un dictionnaire vide.
    blend = blend or {}

    # Récupération du nom du mode de blend.
    # Par défaut : normal.
    name = blend.get("name", "normal")

    # Récupération de l'opacité.
    # Par défaut : 1.0, donc complètement opaque.
    opacity = float(blend.get("opacity", 1.0))

    # Création de l'objet Blend correspondant.
    mode = getblendingmode(name)

    # On sépare les canaux RGB du fond.
    bg_rgb = background[..., :3]

    # On récupère le canal alpha du fond.
    bg_a = background[..., 3:4]

    # On sépare les canaux RGB du nouveau calque.
    im_rgb = image[..., :3]

    # On récupère le canal alpha du nouveau calque.
    calque_a = image[..., 3:4]

    # Application de la formule du blend.
    #
    # Le résultat est limité entre 0 et 1
    # pour rester dans notre représentation d'image.
    blende = np.clip(mode.apply(bg_rgb, im_rgb, 1.0),0,1)

    # L'opacité réelle du calque dépend :
    # - de son alpha
    # - de son opacité définie dans le YAML
    alpha = calque_a * opacity

    # Mélange des couleurs du fond et du nouveau calque.
    #
    # Plus alpha est grand, plus on voit le nouveau calque.
    rgb = bg_rgb * (1 - alpha) + blende * alpha

    # Calcul du nouvel alpha.
    out_a = alpha + bg_a * (1 - alpha)

    # On rassemble R, G, B et A.
    return np.concatenate([rgb, out_a], axis=-1)


def array_to_img(arr: np.ndarray):
    """
    Transforme un tableau NumPy normalisé [0,1]
    en image PIL utilisable pour être sauvegardée ou affichée.
    """

    # On limite les valeurs entre 0 et 1,
    # puis on les transforme en valeurs entre 0 et 255.
    adjusted = np.array(
        np.clip(arr, 0, 1) * 255,
        dtype=np.uint8
    )

    # Transformation du tableau NumPy en image PIL.
    pil_img = Image.fromarray(adjusted)

    return pil_img


def show_from_array(arr: np.ndarray):
    """
    Affiche directement une image stockée sous forme
    de tableau NumPy.
    """

    # Conversion du tableau NumPy en image PIL.
    img = array_to_img(arr)

    # Affichage de l'image.
    img.show()
