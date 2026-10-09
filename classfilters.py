import numpy as np
from classabstraite import Filter
from scipy.ndimage import convolve

TAILLE_NOYAU_MAX = 51
SIGMA_MAX = 50.0  #evite de sature la memoire  


def verifier_entier(valeur, nom: str, mini: int, maxi: int) -> int:
    """Vérifie qu'un paramètre est un entier compris entre mini et maxi, sinon lève une ValueError."""
    if isinstance(valeur, bool) or not isinstance(valeur, int) or not mini <= valeur <= maxi:
        raise ValueError(f"Paramètre '{nom}' invalide : {valeur!r} (entier attendu entre {mini} et {maxi})")
    return valeur


def verifier_reel(valeur, nom: str, mini: float, maxi: float) -> float:
    """Vérifie qu'un paramètre est un nombre fini dans ]mini, maxi], sinon lève une ValueError."""
    if isinstance(valeur,bool) or not isinstance(valeur, (int,float)) or not mini < valeur <= maxi:
        raise ValueError(f"Paramètre '{nom}' invalide : {valeur!r} (nombre attendu dans ]{mini}, {maxi}])")
    return float(valeur)


class normal(Filter):
    """Filtre neutre : renvoie l'image sans la modifier."""
    def __init__(self):
        super().__init__("normal", {})

    def apply(self, image: np.ndarray):
        return image

class blur(Filter):
    """Flou moyenneur : chaque pixel devient la moyenne de son voisinage taille x taille."""
    def __init__(self, taille: int = 5):
        taille = verifier_entier(taille, "taille", 1,TAILLE_NOYAU_MAX)
        super().__init__("blur", {"taille": taille})

    def apply(self, image: np.ndarray):
        t = self.parameters["taille"]
        noyau = np.ones((t, t)) / (t * t)
        return convolve(image, noyau[:, :, None], mode="nearest")


class gaussianblur(Filter):
    """Flou gaussien : les pixels proches du centre pèsent plus que les lointains (window = taille du noyau, sigma = force du flou)."""
    def __init__(self, window: int, sigma: float):
        window = verifier_entier(window, "window", 1, TAILLE_NOYAU_MAX)
        sigma = verifier_reel(sigma, "sigma", 0, SIGMA_MAX)
        super().__init__("gaussianblur", {"window": window, "sigma": sigma})

    def apply(self, image: np.ndarray):
        window = self.parameters["window"]
        sigma = self.parameters["sigma"]
        ax= np.arange(window) - (window - 1) / 2
        xx, yy= np.meshgrid(ax, ax)
        noyau= np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        noyau /= noyau.sum()
        return convolve(image, noyau[:, :, None], mode="nearest")


class Grayscale(Filter):
    """Niveaux de gris : chaque pixel prend sa luminance (0.299 R + 0.587 G + 0.114 B)."""
    def __init__(self):
        super().__init__("grayscale", {})

    def apply(self, image: np.ndarray):
        R, G, B = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        gray = 0.299 * R + 0.587 * G + 0.114 * B
        new = image.copy()
        new[:, :, 0]= gray
        new[:, :, 1] = gray
        new[:, :, 2] = gray
        return new


class Sepia(Filter):
    """Effet sépia : chaque nouvelle couleur est un mélange pondéré de R, G, B."""
    def __init__(self):
        super().__init__("sepia", {})

    def apply(self, image: np.ndarray) -> np.ndarray:
        matrice = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        new= image.copy()
        new[..., :3]= np.clip(image[..., :3] @ matrice.T, 0, 1)  # la matrice ne s'applique qu'à R, G, B (alpha conservé)
        return new


class blackborder(Filter):
    """Cadre noir : met à 0 une bordure de border_size pixels sur les quatre côtés."""
    def __init__(self, border_size: int):
        border_size = verifier_entier(border_size, "border_size", 0, 100000)
        super().__init__("blackborder", {"border_size": border_size})

    def apply(self, image: np.ndarray):
        epaisseur = self.parameters["border_size"]
        image = image.copy()  
        if epaisseur== 0:    
            return image
        image[:epaisseur,:,:] =0
        image[-epaisseur:,:, :]= 0
        image[:,:epaisseur, :] = 0
        image[:, -epaisseur:, :]= 0
        return image