from PIL import Image
import numpy as np
from classabstraite import *
from classfilters import blur, Grayscale, Sepia




def process_image (path):
    image = Image.open(path).convert("RGB")
    image = np.array(image) / 255.0
    return image 

def apply_filters(image: np.ndarray, filters: list[Filter]):
    for filter in filters:
        image = filter.apply(image)
    return image

def apply_layers():
    pass

def apply_blend():
    pass


def compose():
    # im = im_orig
    # for masque in masques: #masques est récupérée du fichier .yaml
    #   im = apply_blend(im,masque)
    


    pass 

def apply_all_modif():
    apply_filters()
    apply_layers()
    #blend()

def show_result():
    pass
