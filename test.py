from PIL import Image
import numpy as np
from classfilters import blur, Grayscale, Sepia


def testfunc():
    # Chargement de l'image
    image = Image.open("images/layers/0_photo.jpg").convert("RGB")
    image = np.array(image) / 255.0

    print("Image originale :")
    print("shape :", image.shape)
    print("min :", image.min())
    print("max :", image.max())

    # =========================
    # Grayscale
    # =========================
    grayscale = Grayscale()
    gray_image = grayscale.apply(image)

    print("\nGrayscale :")
    print("shape :", gray_image.shape)
    print("min :", gray_image.min())
    print("max :", gray_image.max())

    Image.fromarray(
        np.clip(gray_image * 255, 0, 255).astype(np.uint8)
    ).show()

    # =========================
    # Blur
    # =========================
    blur_filter = blur(5)
    blurred_image = blur_filter.apply(image)

    print("\nBlur :")
    print("shape :", blurred_image.shape)
    print("min :", blurred_image.min())
    print("max :", blurred_image.max())

    Image.fromarray(
        np.clip(blurred_image * 255, 0, 255).astype(np.uint8)
    ).show()

    
    # =========================
    # Sepia
    # =========================
    sepia_filter = Sepia()
    sepia_image = sepia_filter.apply(image)

    print("\nSepia :")
    print("shape :", sepia_image.shape)
    print("min :", sepia_image.min())
    print("max :", sepia_image.max())

    Image.fromarray(
        np.clip(sepia_image * 255, 0, 255).astype(np.uint8)
    ).show()

testfunc()






testfunc()