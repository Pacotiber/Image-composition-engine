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
        R,G,B=image[:,:,0],image[:,:,1],image[:,:,2]
        gray=0.299*R+0.587*G+0.114*B
        new = image.copy()
        new[:,:,0] = gray
        new[:,:,1]=gray
        new[:,:,2]=gray
        return new

class Sepia(Filter): 
    def __init__(self):
        super().__init__("greyscale",{})
    def apply(self,image: np.ndarray) -> np.ndarray:
        """Effet sépia : chaque nouvelle couleur est un mélange pondéré de R, G, B."""
        matrice = np.array([
        [0.393, 0.769, 0.189], # nouveau rouge
        [0.349, 0.686, 0.168],  # nouveau vert
        [0.272, 0.534, 0.131],  # nouveau bleu
        ])
        new =image @ matrice.T
        return np.clip(new,0,1) 

        

        
        
 

