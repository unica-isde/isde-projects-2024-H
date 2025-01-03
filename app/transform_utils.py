from PIL import Image, ImageEnhance
import os

# Directory to store transformed images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def transform_image(image_id: str, brightness: float, contrast: float, color: float, sharpness: float) -> str:
    """
    Applies the specified transformations to the selected image and saves it.

    Parameters:
    - image_id: The filename of the image to transform.
    - brightness: Adjusts the brightness (default = 1.0).
    - contrast: Adjusts the contrast (default = 1.0).
    - color: Adjusts the color saturation (default = 1.0).
    - sharpness: Adjusts the sharpness (default = 1.0).

    Returns:
    - URL of the transformed image.
    """
    # Validate the selected image exists
    image_path = os.path.join("app/static/images", image_id)
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The selected image '{image_id}' does not exist.")

    # Open the image
    image = Image.open(image_path)

    # Apply brightness transformation
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)

    # Apply contrast transformation
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    # Apply color transformation
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(color)

    # Apply sharpness transformation
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)

    # Save the transformed image
    transformed_filename = f"transformed_{image_id}"
    transformed_path = os.path.join(UPLOAD_FOLDER, transformed_filename)
    image.save(transformed_path)

    # Return the relative URL of the transformed image
    return f"/static/uploads/{transformed_filename}"