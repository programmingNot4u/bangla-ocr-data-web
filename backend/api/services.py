# api/services.py
import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def upload_image_to_cloudinary(image_file):
    """
    Uploads an image file to Cloudinary.
    """
    try:
        upload_result = cloudinary.uploader.upload(
            image_file,
            folder="chrono_scribe_submissions" # Optional: organize uploads in a folder
        )
        return {
            "success": True,
            "url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}