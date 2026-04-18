"""Image optimization service for product images.

Handles image validation, optimization, thumbnail generation, and storage
for product images with EXIF stripping and format conversion.
"""

import io
import logging
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageOps

from oneai_reach.domain.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ImageService:
    """Service for image processing and storage operations."""

    # Magic bytes for supported image formats
    MAGIC_BYTES = {
        b"\xff\xd8\xff": "image/jpeg",
        b"\x89PNG\r\n\x1a\n": "image/png",
        b"RIFF": "image/webp",  # WebP starts with RIFF
    }

    def __init__(self, storage_base_path: str = "data/products"):
        """Initialize image service.

        Args:
            storage_base_path: Base directory for storing product images
        """
        self.storage_base_path = Path(storage_base_path)

    def validate_image_magic(self, file_bytes: bytes) -> str:
        """Validate image format using magic bytes.

        Args:
            file_bytes: Raw image bytes

        Returns:
            MIME type of the image (image/jpeg, image/png, image/webp)

        Raises:
            ValidationError: If image format is not supported
        """
        if len(file_bytes) < 8:
            raise ValidationError(
                field="image",
                value=f"{len(file_bytes)} bytes",
                reason="File too small to be a valid image",
            )

        # Check magic bytes
        for magic, mime_type in self.MAGIC_BYTES.items():
            if file_bytes.startswith(magic):
                # Additional check for WebP
                if magic == b"RIFF" and file_bytes[8:12] != b"WEBP":
                    continue
                logger.info(f"Detected image format: {mime_type}")
                return mime_type

        raise ValidationError(
            field="image",
            value="unknown format",
            reason="Unsupported image format. Only JPEG, PNG, and WebP are allowed",
        )

    def optimize_image(
        self,
        file_bytes: bytes,
        max_edge: int = 2048,
        quality: int = 85,
    ) -> bytes:
        """Optimize image by resizing, stripping EXIF, and compressing.

        Args:
            file_bytes: Raw image bytes
            max_edge: Maximum dimension (width or height) in pixels
            quality: JPEG quality (1-100, default 85)

        Returns:
            Optimized image bytes

        Raises:
            ValidationError: If image cannot be processed
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(file_bytes))

            # Apply EXIF orientation and strip EXIF data
            img = ImageOps.exif_transpose(img)

            # Convert RGBA to RGB for JPEG compatibility
            if img.mode == "RGBA":
                # Create white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Resize if needed
            if max(img.size) > max_edge:
                ratio = max_edge / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                logger.info(f"Resized image to {new_size}")

            # Save optimized image
            output = io.BytesIO()
            img.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
            )
            optimized_bytes = output.getvalue()

            logger.info(
                f"Optimized image: {len(file_bytes)} → {len(optimized_bytes)} bytes "
                f"({len(optimized_bytes) / len(file_bytes) * 100:.1f}%)"
            )

            return optimized_bytes

        except Exception as e:
            raise ValidationError(
                field="image",
                value="processing error",
                reason=f"Failed to optimize image: {str(e)}",
            )

    def create_thumbnail(
        self,
        file_bytes: bytes,
        size: Tuple[int, int] = (400, 400),
    ) -> bytes:
        """Create thumbnail from image.

        Args:
            file_bytes: Raw image bytes
            size: Thumbnail size as (width, height) tuple

        Returns:
            Thumbnail image bytes

        Raises:
            ValidationError: If thumbnail cannot be created
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(file_bytes))

            # Apply EXIF orientation
            img = ImageOps.exif_transpose(img)

            # Convert RGBA to RGB for JPEG
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.LANCZOS)

            # Save thumbnail
            output = io.BytesIO()
            img.save(
                output,
                format="JPEG",
                quality=85,
                optimize=True,
            )
            thumbnail_bytes = output.getvalue()

            logger.info(f"Created thumbnail: {img.size} ({len(thumbnail_bytes)} bytes)")

            return thumbnail_bytes

        except Exception as e:
            raise ValidationError(
                field="image",
                value="thumbnail error",
                reason=f"Failed to create thumbnail: {str(e)}",
            )

    def save_image(
        self,
        file_bytes: bytes,
        product_id: str,
        filename: str,
    ) -> Path:
        """Save image to local filesystem.

        Args:
            file_bytes: Image bytes to save
            product_id: Product identifier
            filename: Filename for the image

        Returns:
            Path to saved image

        Raises:
            ValidationError: If image cannot be saved
        """
        try:
            # Create product images directory
            product_dir = self.storage_base_path / product_id / "images"
            product_dir.mkdir(parents=True, exist_ok=True)

            # Save image
            image_path = product_dir / filename
            image_path.write_bytes(file_bytes)

            logger.info(f"Saved image: {image_path} ({len(file_bytes)} bytes)")

            return image_path

        except Exception as e:
            raise ValidationError(
                field="image",
                value=filename,
                reason=f"Failed to save image: {str(e)}",
            )
