from django.core.exceptions import ValidationError
from django.conf import settings

COMPONENT_TO_GLB = {
    "cpu": "cpu.glb",
    "gpu": "gpu.glb",
    "ram": "ram.glb",
    "motherboard": "motherboard.glb",
    "cooling": "fan_large.glb",
    "case_white": "case_white.glb",
    "case_black": "case_black.glb",
    "window_fan_white": "fan_window_white.glb",
    "monitor": "monitor.glb",
    "storage": "storage.glb"
}

def validate_3d_model_file(file, max_size_mb=100):
    """
    Validate 3D model file before storage.
    
    Args:
        file: Django UploadedFile object
        max_size_mb: Maximum file size in megabytes (default 100MB)
    
    Raises:
        ValidationError: If file is invalid
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    # Check file size
    if file.size > max_size_bytes:
        raise ValidationError(
            f"3D model file too large. Maximum size is {max_size_mb}MB. "
            f"Your file is {file.size / (1024*1024):.2f}MB."
        )
    
    # Check file extension
    allowed_extensions = ['.glb', '.gltf']
    file_ext = None
    if hasattr(file, 'name') and file.name:
        import os
        _, file_ext = os.path.splitext(file.name.lower())
    
    if file_ext not in allowed_extensions:
        raise ValidationError(
            f"Invalid file format. Only {', '.join(allowed_extensions)} files are allowed. "
            f"Got: {file_ext or 'unknown'}"
        )
    
    return True

def validate_image_file(file, max_size_mb=10):
    """
    Validate image file before storage.
    
    Args:
        file: Django UploadedFile object
        max_size_mb: Maximum file size in megabytes (default 10MB)
    
    Raises:
        ValidationError: If file is invalid
    """
    import os
    
    max_size_bytes = max_size_mb * 1024 * 1024
    
    # Check file size
    if file.size > max_size_bytes:
        raise ValidationError(
            f"Image file too large. Maximum size is {max_size_mb}MB. "
            f"Your file is {file.size / (1024*1024):.2f}MB."
        )
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_ext = os.path.splitext(file.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise ValidationError(
            f"Invalid image format. Allowed types: JPG, PNG, GIF, WebP"
        )
    
    return True
