from classabstraite import *
import numpy as np


class NormalBlend(Blend):
    """Normal : le calque recouvre le fond (seule l'image du calque est conservée)."""
    def apply(self,background,image,opacity):
        return image
class DifferenceBlend(Blend):
    """Différence : valeur absolue de l'écart entre fond et calque (zones identiques -> noir)."""
    def apply(self,background,image,opacity):
        return np.abs(background-opacity*image)
class DarkenBlend(Blend):
    """Obscurcir : garde le plus sombre des deux pixels (minimum)."""
    def apply(self,background,image,opacity):
        return np.minimum(background,image*opacity)
class MultiplyBlend(Blend):
    """Produit : multiplie fond et calque, le résultat est toujours plus sombre."""
    def apply(self,background,image,opacity):
        return background*image*opacity
class ColorBurnBlend(Blend):
    """Densité couleur + : assombrit le fond en augmentant le contraste selon le calque."""
    def apply(self,background,image,opacity):
        return 1-(1-background)/(image*opacity)
class LinearBurn(Blend):
    """Densité linéaire + : additionne fond et calque puis retire 1, ce qui assombrit."""
    def apply(self,background,image,opacity):
        return background+image*opacity-1
class LigthenBlend(Blend):
    """Éclaircir : garde le plus clair des deux pixels (maximum)."""
    def apply(self,background,image,opacity):
        return np.maximum(background,image*opacity)
class ScreenBlend(Blend):
    """Superposition écran : inverse de Produit, le résultat est toujours plus clair."""
    def apply(self,background,image,opacity):
        return 1-(1-background)*(1-image*opacity)
class ColorDodgeBlend(Blend):
    """Densité couleur - : éclaircit le fond en augmentant le contraste selon le calque."""
    def apply(self,background,image,opacity):
        return background/(1-image*opacity)
class LinearDodgeBlend(Blend):
    """Densité linéaire - (Add) : additionne simplement fond et calque."""
    def apply(self,background,image,opacity):
        return background+image*opacity
class OverlayBlend(Blend):
    """Incrustation : Produit sur les zones sombres du fond, Écran sur les claires (contraste accru)."""
    def apply(self,background,image,opacity):
        return np.where(background<0.5,2*background*image*opacity,1-2*(1-background)*(1-image*opacity))
class SoftLightBlend(Blend):
    """Lumière tamisée : version douce d'Incrustation, éclaircit ou assombrit légèrement."""
    def apply(self,background,image,opacity):
        return (1-2*image*opacity)*background**2+2*image*opacity*background
class HardLightBlend(Blend):
    """Lumière crue : comme Incrustation, mais le choix Produit/Écran dépend du calque."""
    def apply(self,background,image,opacity):
        return np.where(image*opacity<0.5,2*background*image*opacity,1-2*(1-background)*(1-image*opacity))
class VividLightBlend(Blend):
    """Lumière vive : Densité couleur + ou - selon le calque, effet très contrasté."""
    def apply(self,background,image,opacity):
        return np.where(image*opacity<0.5,1-(1-background)/(2*image*opacity),background/(2*(1-image*opacity)))
class LinearLightBlend(Blend):
    """Lumière linéaire : Densité linéaire + ou - selon le calque."""
    def apply(self,background,image,opacity):
        return np.where(image*opacity<0.5,background+2*image*opacity-1,background+2*(image*opacity-0.5))
class PinLightBlend(Blend):
    """Lumière ponctuelle : remplace les pixels par le plus sombre ou le plus clair selon le calque."""
    def apply(self,background,image,opacity):
        return np.where(image*opacity<0.5,np.min(background,2*image*opacity),np.max(background,2*(image*opacity-0.5)))
class ExclusionBlend(Blend):
    """Exclusion : proche de Différence mais avec un contraste plus faible."""
    def apply(self,background,image,opacity):
        return background+image*opacity-2*background*image*opacity