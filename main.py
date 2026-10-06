from classabstraite import Filter,Layer
from functions import *

paths = ["images/layers/0_picture","images/layers/1_picture","images/layers/2_picture"]


def main():
    for path in paths :
        im = process_image(path)
        im = apply_filters(im)

    show_result(apply_all_modif(im))
