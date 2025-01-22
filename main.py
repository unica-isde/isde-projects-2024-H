import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.transform_utils import transform_image
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.ml.classification_utils import classify_image
from app.utils import list_images, save_uploaded_file, delete_old_files
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background task
    task = asyncio.create_task(delete_old_files())
    yield
    # Shutdown: Cancel the background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
app = FastAPI(lifespan=lifespan)
config = Configuration()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Set up a folder for storing user-uploaded images
UPLOAD_FOLDER = "app/static/user_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/info")
def info() -> dict[str, list[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images}
    return data


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The home page of the service."""
    return templates.TemplateResponse("home.html", {"request": request})

# New feature : image histogram
@app.get("/histogram", response_class=HTMLResponse)
def home(request: Request):
    """This page allows the user to generate a color histogram of an image."""
    return templates.TemplateResponse("histogram.html", {"request": request, "images": list_images()})


# New feature : image upload
@app.post("/classify_upload")
async def upload_image(request: Request, model_id: str = Form(...), image_file: UploadFile = File(...)):
    """Uploads an image file to the server, and classifies it using the specified model."""
    path = "custom"
    # Save the uploaded file with a unique name
    file_path, new_filename = await save_uploaded_file(image_file)

    # Use the saved file for classification
    classification_scores = classify_image(model_id=model_id, img_id=new_filename, path=path)
    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_file.filename,
            "classification_scores": json.dumps(classification_scores),
            "img_path": f"/static/user_images/{new_filename}",
        },
    )

@app.get("/classify_upload", response_class=HTMLResponse)
def upload_form(request: Request):
    """
    Renders a form to select an image to upload, and specify transformation model to use.
    """
    return templates.TemplateResponse(
        "classify_upload.html", {"request": request, "models": Configuration.models}
    )

@app.get("/classifications")
def create_classify(request: Request):
    """
    This page allows classification of an image chosen in a preset folder, along with a model.
    """
    return templates.TemplateResponse(
        "classification_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classifications")
async def request_classification(request: Request):
    """
        POST request to classify an image using a specified model.
        Takes the image ID and model ID from the form data as parameters,
        and returns the classification results HTML page.
    """
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    model_id = form.model_id
    classification_scores = classify_image(model_id=model_id, img_id=image_id, path="default")
    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "classification_scores": json.dumps(classification_scores),
            "img_path": f"/static/imagenet_subset/{image_id}",
        },
    )

@app.get("/download_results")
async def download_results(scores: str):
    """
    Endpoint to download classification scores as JSON.
    """
    # Convert the results string into a JSON object
    scores_dict = json.loads(scores)

    # Return a JSON response with the appropriate headers for downloading
    return JSONResponse(
        content=scores_dict,
        headers={"Content-Disposition": "attachment; filename=results.json"},
    )

# New feature: Image Transformation
@app.get("/transform", response_class=HTMLResponse)
def transform_form(request: Request):
    """
    Renders a form to select an image and specify transformation parameters.
    """
    return templates.TemplateResponse(
        "transform_select.html", {"request": request, "images": list_images()}
    )

@app.post("/transform")
async def transform_post(
    request: Request,
    image_id: str = Form(...),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    color: float = Form(1.0),
    sharpness: float = Form(1.0),
):
    """
    Handles the POST request for applying image transformations.
    Delegates processing to the `transform_image` function.
    """
    # Call the helper function to apply transformations
    transformed_image_b64 = transform_image(
        image_id=image_id,
        brightness=brightness,
        contrast=contrast,
        color=color,
        sharpness=sharpness,
    )

    # Return the result page with the transformed image
    return templates.TemplateResponse(
        "transform_output.html",
        {
            "request": request,
            "image_id": image_id,
            "transformed_image_b64": transformed_image_b64,
        },
    )