import os

project_root = os.path.dirname(os.path.abspath(__file__))


class Configuration:
    """
    Contains the configuration information for the app.
    Custom paths for user-uploaded images and the ImageNet images are defined here.
    """

    # classification
    image_folder_path = os.path.join(project_root, "static/imagenet_subset")
    user_folder_path = os.path.join(project_root, "static/user_images")
    models = (
        "resnet18",
        "alexnet",
        "vgg16",
        "inception_v3",
    )
