from classabstraite import Filter,Layer
from functions import *
def main():
    a=readfromyaml("modifications.yaml")
    b=buildlayers(a)
    c=show_from_array(b)
main()
