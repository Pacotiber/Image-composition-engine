import numpy as np
from PIL import Image
from classabstraite import Filter
from scipy.ndimage import convolve

class blur(Filter):
    def __init__(self,taille:int):
        super().__init__("blur",{"taille":taille})
    def apply(self, image: np.ndarray):
        """Flou moyenneur : chaque pixel devient la moyenne de son voisinage taille x taille."""
        noyau = np.ones((self.parameters["taille"], self.parameters["taille"])) / (self.parameters["taille"] * self.parameters["taille"])
        return convolve(image, noyau[:, :, None], mode="nearest")
    
class Grayscale(Filter):
    def __init__(self):
        super().__init__("grayscale",{})
    def apply(self, image: np.ndarray):
        pass
       