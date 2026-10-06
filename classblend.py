from classabstraite import *
import numpy as np
class DifferenceBlend(Blend):
    def apply(self,background,image,opacity):
        return background-opacity*image
