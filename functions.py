def process_image ():
    pass
def apply_filters():
    pass

def apply_layers():
    pass

def apply_blend():
    pass


def compose():
    im = im_orig
    for masque in masques: #masques est récupérée du fichier .yaml
        im = apply_blend(im,masque)
    


    pass 

def apply_all_modif():
    apply_filters()
    apply_layers()
    blend()

def show_result():
    pass
