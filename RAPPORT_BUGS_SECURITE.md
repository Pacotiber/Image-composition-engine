# Rapport de tests : bugs et sécurité

Date : 2026-10-08. Tests lancés avec le `.venv` du projet (Python 3.13.15, numpy 2.5.3, Pillow 12.3.0, scipy 1.18.1).

## 1. Résultat de l'exécution

| Test | Résultat |
|---|---|
| `main.py` avec `modifications.yaml` tel quel | ❌ **Plante** : `4_romain.png` fait 1500×1000 alors que les autres images font 1908×1272 (la vérification de taille fonctionne, mais le pipeline par défaut ne passe donc pas) |
| Pipeline avec les 4 premiers calques | ✅ OK, rendu visuel correct |
| 18 blends sur de vraies images | ✅ 15 OK · ⚠️ 2 produisent des NaN (`colorburn`, `vividlight`) · ❌ 1 plante (`pinlight`) |
| 6 filtres | ✅ 5 OK · ❌ `sepia` plante |

---

## 2. Bugs fonctionnels

### ✅ B1 : `PinLightBlend` plante systématiquement — CORRIGÉ (`classblend.py:68`)
`np.min(background, 2*image*opacity)` : le 2ᵉ argument de `np.min` est un **axe**, pas un 2ᵉ tableau.
→ `TypeError: only integer scalar arrays can be converted to a scalar index`.
**Correction :** utiliser `np.minimum(...)` et `np.maximum(...)`.

### ✅ B2 : `Sepia` plante sur toutes les images — CORRIGÉ (`classfilters.py:66`)
Les images sont chargées en RGBA (4 canaux) mais la matrice est 3×3 → `image @ matrice.T` échoue (`matmul: mismatch in core dimension`).
**Correction :** appliquer la matrice sur `image[..., :3]` et recoller le canal alpha.

### ✅ B3 : division par zéro → NaN — CORRIGÉ (dénominateur ≥ EPS) (`colorburn`, `colordodge`, `vividlight`)
- `ColorBurn` : `/(image*opacity)` avec un pixel de calque = 0
- `ColorDodge` : `/(1-image*opacity)` avec un pixel = 1
- `VividLight` : les deux

`np.clip` ne supprime **pas** les NaN. Comme `rgb = bg*(1-alpha) + blende*alpha` et que `NaN * 0 = NaN`, même les zones **transparentes** du calque sont corrompues (test : 3143 pixels NaN, tous dans des zones où alpha = 0). Ces NaN deviennent du noir (ou une valeur indéfinie) à la conversion en `uint8`.
**Correction :** `np.divide(..., where=denom!=0)` ou un epsilon, puis `np.nan_to_num`.

### 🟠 B4 : la vérification de taille ne compare que la hauteur (`functions.py:106`)
`len(bg_rgb) != len(im_rgb)` ne compare que la 1ʳᵉ dimension. Deux images de même hauteur mais de largeur différente passent le test puis plantent avec une erreur numpy peu claire.
**Correction :** `if bg_rgb.shape != im_rgb.shape:`

### ✅ B5 : `blackborder` avec `border_size: 0` rend toute l'image noire — CORRIGÉ (+ ne modifie plus l'image en place) (`classfilters.py:77-80`)
`image[-0:]` correspond à **toute** l'image en Python. Une valeur négative donne aussi un résultat absurde.
**Correction :** vérifier `border_size > 0` (et ne rien faire si 0).

### 🟠 B6 : l'opacité n'est jamais bornée (`functions.py:61-62` et `101`)
Dans `buildlayers`, la variable `opacity` est calculée et bornée entre 0 et 1, mais **jamais utilisée** (code mort). `apply_blend` relit `blend["opacity"]` sans la borner :
- `opacity: 5` → couleurs hors limites (`[3.44, -1.97, -2.27]` avant le clip final)
- `opacity: "nan"` → `float("nan")` est accepté → image entièrement NaN

De même, `nameblend` est calculé mais jamais utilisé.
**Correction :** borner l'opacité dans `apply_blend` et refuser NaN/inf (`math.isfinite`).

### 🟡 B7 : `dicttolistfilters` masque la vraie erreur (`functions.py:79-85`)
- Filtre sans clé `name` → `UnboundLocalError` (la variable `name` n'existe pas encore dans le `except`)
- `except KeyError` attrape aussi les KeyError internes et affiche à tort « filtre inconnu »
- Paramètres invalides (`{foo: 1}`) → `TypeError` non géré

### 🟡 B8 : paramètres de filtre non validés
- `blur` avec `taille: 0` → `RuntimeError` de scipy ; `taille: "5"` → `TypeError`
- `gaussianblur` avec `sigma: 0` → division par zéro, image entièrement noire/NaN

### 🟡 B9 : YAML mal formé → crashs bruts
- fichier vide → `TypeError: 'NoneType' object is not subscriptable`
- pas de clé `layers` → `KeyError`
- `layers: []` → `np.clip(None)` → `TypeError`
- `blend: {name: null}` → `AttributeError: 'NoneType' object has no attribute 'strip'`
- `layer["image"]` absent → `KeyError`

### 🟡 B10 : divers
- `blackborder` **modifie l'image d'entrée en place** (les autres filtres renvoient une nouvelle image). Faire `image = image.copy()`.
- Le `blend` du premier calque est ignoré sans avertissement.
- Le YAML utilise `greyscale` alors que la classe s'appelle `Grayscale` / `"grayscale"` : risque de confusion.
- `from re import S` (inutilisé) dans `classabstraite.py`.
- `main.py` appelle `main()` sans `if __name__ == "__main__":`, donc un simple import lance tout le pipeline.
- Les chemins du YAML utilisent `\` : ils ne marchent que sous Windows. Utiliser `/`.
- `images/upsidedown_bike.af~lock~` (fichier de verrou Affinity) est versionné → l'ajouter au `.gitignore`.
- Le point d'entrée `pyproject.toml` (`image_composition_engine:main`) affiche seulement « Hello… » et ne lance pas le moteur.

---

## 3. Failles de sécurité

> Point positif : `yaml.safe_load` est bien utilisé (pas `yaml.load`), ce qui évite l'exécution de code arbitraire via le YAML. 👍

### ✅ S1 : lecture de fichiers arbitraires (path traversal) — CORRIGÉ (`chemin_image_securise` dans `functions.py`)
`layer["image"]` est passé directement à `Image.open()` sans contrôle. Un YAML fourni par un tiers peut lire n'importe quelle image du disque (`../../`, chemin absolu, partage réseau `\\serveur\...`). Test : `C:\Windows\Web\Screen\img100.jpg` est lu sans erreur.
**Correction :** résoudre le chemin (`Path(p).resolve()`) et vérifier qu'il reste dans le dossier `images/` (`is_relative_to`).

### ✅ S2 : déni de service (DoS) par les paramètres de filtre — CORRIGÉ (`taille`/`window` ≤ 51, `0 < sigma ≤ 50` dans `classfilters.py`)
Aucune borne sur `taille`, `window`, `border_size` :
- `blur` avec `taille: 100000` → noyau de 10¹⁰ éléments → saturation mémoire / plantage
- `gaussianblur` avec `window: 50000` → même problème (`meshgrid` énorme)
- de gros noyaux même « raisonnables » (ex. 501) rendent la convolution extrêmement lente

**Correction :** imposer des bornes (ex. `1 <= taille <= 51`, entier impair) et vérifier le type.

### 🟠 S3 : images géantes (decompression bomb) et consommation mémoire
Pillow avertit au-delà d'environ 89 Mpx et refuse au-delà d'environ 179 Mpx, mais chaque image est convertie en `float64` RGBA (32 octets/pixel). Une image de 80 Mpx tout juste sous la limite occupe déjà environ **2,5 Go** par calque, et le nombre de calques n'est pas limité.
**Correction :** limiter les dimensions et le nombre de calques, utiliser `float32`, et activer `warnings.simplefilter("error", Image.DecompressionBombWarning)`.

### 🟠 S4 : injection de paramètres via `**params`
`FILTRES[name](**params)` transmet tout le dictionnaire YAML au constructeur, sans contrôle de type (chaînes, listes, nombres négatifs, booléens…). Combiné à S2, cela permet des entrées malveillantes. Valider chaque paramètre explicitement.

### 🟡 S5 : valeurs non finies acceptées
`float()` accepte `"nan"`, `"inf"`, `"1e308"`. Une opacité NaN corrompt toute l'image (cf. B6).

### 🟡 S6 : messages d'erreur
Les exceptions Python brutes (tracebacks) exposent les chemins internes de la machine. Pour un outil exposé à des utilisateurs, intercepter les erreurs dans `main()` et afficher un message propre.

### 🟡 S7 : `from module import *`
Les imports wildcard en cascade (`functions` → `classabstraite` → `numpy`, `PIL`…) mélangent les espaces de noms. Une classe peut en écraser une autre sans qu'on le voie (ex. `normal` filtre vs blend). Ce n'est pas une faille directe, mais cela rend le code plus difficile à auditer.

---

## 4. Priorités conseillées
1. Corriger **B1** (pinlight) et **B2** (sepia) : ces fonctions ne marchent pas du tout.
2. Corriger **B3** (NaN) et **B4** (taille).
3. Ajouter la validation des chemins (**S1**) et des bornes sur les paramètres (**S2**, **S4**).
4. Redimensionner `4_romain.png` ou le retirer du YAML pour que `main.py` passe.
