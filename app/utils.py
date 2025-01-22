import asyncio
import os
import time
import aiofiles
from fastapi import UploadFile

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
async def save_uploaded_file(image_file: UploadFile) -> tuple[str, str]:
    # Get the original filename
    original_filename = image_file.filename

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

# helper function to remove old user uploaded files
async def delete_old_files():
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
