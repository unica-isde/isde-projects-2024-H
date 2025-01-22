import asyncio
import os
import time
import aiofiles
from fastapi import UploadFile, HTTPException

from app.config import Configuration

conf = Configuration()


def list_images():
    """Returns the list of available images."""
    img_names = filter(
        lambda x: x.endswith(".JPEG"), os.listdir(conf.image_folder_path)
    )
    return list(img_names)

# helper function to save uploaded files
UPLOAD_FOLDER = "app/static/user_images"
# List of allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/bmp"}

def allowed_file(filename: str, content_type: str) -> bool:
    """Check if the file has an allowed extension and MIME type."""
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower() in ALLOWED_EXTENSIONS and content_type in ALLOWED_MIME_TYPES

async def save_uploaded_file(image_file: UploadFile) -> tuple[str, str]:
    """
    This method saves the user uploaded file with a unique name, and returns the file path and new filename.
    Returns:
        tuple[str, str]: The file path and the new filename
    """
    try:
        # Get the original filename and content type
        original_filename = image_file.filename
        content_type = image_file.content_type

        # Validate the file
        if not allowed_file(original_filename, content_type):
            raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")

        # Get the current Unix epoch time
        epoch_time = int(time.time())

        # Modify the filename to include the original filename and the Unix epoch time
        filename, file_extension = os.path.splitext(original_filename)
        new_filename = f"{filename}_{epoch_time}{file_extension}"

        # Construct the full file path
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)

        # Save the file
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await image_file.read())

        return file_path, new_filename

    except Exception as e:
        # Handle any exceptions that occur during the file upload process
        raise HTTPException(status_code=400, detail=f"Error uploading file: {str(e)}")

# helper function to remove old user uploaded files
async def delete_old_files():
    """Helper function to delete files older than a certain age."""
    while True:
        # Define the maximum age of files in seconds
        max_age = 3600  # 1 hour
        current_time = time.time()

        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age:
                os.remove(file_path)

        await asyncio.sleep(600)  # Check every 10 minutes
