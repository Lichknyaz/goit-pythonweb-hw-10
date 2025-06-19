import os
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status


def get_cloudinary_config():
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')

    if not all([cloud_name, api_key, api_secret]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary configuration is missing. Please check environment variables."
        )

    return {
        'cloud_name': cloud_name,
        'api_key': api_key,
        'api_secret': api_secret,
        'secure': True
    }

def upload_avatar(file):
    try:
        cloudinary.config(**get_cloudinary_config())

        result = cloudinary.uploader.upload(
            file,
            folder="avatars",
            public_id=None,
            overwrite=True,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )

