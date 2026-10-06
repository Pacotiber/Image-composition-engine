from re import S
import numpy as np
from PIL import Image
from scipy.ndimage import convolve
from sympy import im
from abc import abstractmethod

class Layer:
    def __init__(self,image: np.ndarray, opacity: float, filters: list[str], blend: str):
        self.image=image
        self.opacity=opacity
        self.filters=filters
        self.blend=blend

class Filter:
    def __init__(self, name: str, parameters: dict):
        self.name=name
        self.parameters=parameters
    @abstractmethod
    def apply(self, image: np.ndarray):
        pass
class Blend:
    @abstractmethod
    def apply(self,background :np.ndarray,image :np.ndarray,opacity):
        pass