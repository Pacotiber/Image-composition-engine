from classabstraite import Filter,Layer
from functions import *

paths = ["images/layers/0_picture","images/layers/1_picture","images/layers/2_picture"]


def main():
   a=readfromyaml("modifications.yaml")
   b=buildlayers(a)
   show_from_array(b)
