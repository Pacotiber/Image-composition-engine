from classabstraite import Filter,Layer
from functions import *

def main():
    im = process_image()
    show_result(apply_all_modif(im))
