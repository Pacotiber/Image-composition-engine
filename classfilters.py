import numpy as np
from PIL import Image
from classabstraite import Filter
from scipy.ndimage import convolve
class normal(Filter):
    def __init__(self):
        super().__init__("normal",{})
    def apply(self, image: np.ndarray):
        return image
class blur(Filter):
    """Flou moyenneur (pas de params dans le YAML -> valeur par défaut)."""
    def __init__(self, taille: int = 5):
        super().__init__("blur", {"taille": taille})

    def apply(self, image: np.ndarray):
        t = self.parameters["taille"]
        noyau = np.ones((t, t)) / (t * t)
        return convolve(image, noyau[:, :, None], mode="nearest")
class gaussianblur(Filter):
    def __init__(self, window: int, sigma: float):
        super().__init__("gaussianblur", {"window": window, "sigma": sigma})

    def apply(self, image: np.ndarray):
        """Flou gaussien : noyau window x window pondéré par une gaussienne d'écart-type sigma."""
        window = self.parameters["window"]
        sigma = self.parameters["sigma"]
        ax = np.arange(window) - (window - 1) / 2
        xx, yy = np.meshgrid(ax, ax)
        noyau = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        noyau /= noyau.sum()  # normalisation : la somme vaut 1

        return convolve(image, noyau[:, :, None], mode="nearest")
    
class Grayscale(Filter):
    def __init__(self):
        super().__init__("grayscale",{})
    def apply(self, image: np.ndarray):
        R,G,B=image[:,:,0],image[:,:,1],image[:,:,2]
        gray=0.299*R+0.587*G+0.114*B
        new = image.copy()
        new[:,:,0] = gray
        new[:,:,1]=gray
        new[:,:,2]=gray
        return new

class Sepia(Filter): 
    def __init__(self):
        super().__init__("sepia",{})
    def apply(self,image: np.ndarray) -> np.ndarray:
        """Effet sépia : chaque nouvelle couleur est un mélange pondéré de R, G, B."""
        matrice = np.array([
        [0.393, 0.769, 0.189], # nouveau rouge
        [0.349, 0.686, 0.168],  # nouveau vert
        [0.272, 0.534, 0.131],  # nouveau bleu
        ])
        new =image @ matrice.T
        return np.clip(new,0,1) 

        

        
        
 

