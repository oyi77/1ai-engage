
## Image Optimization Service - 2026-04-18

### Implementation Success
- Created `src/oneai_reach/application/product/image_service.py` with 4 core methods
- All tests passed: magic bytes validation, optimization, thumbnails, EXIF stripping

### Key Patterns
1. **Magic Bytes Validation**: Detect format before PIL processing (JPEG: `\xff\xd8\xff`, PNG: `\x89PNG\r\n\x1a\n`, WebP: `RIFF...WEBP`)
2. **EXIF Stripping**: Use `ImageOps.exif_transpose()` to apply orientation then strip metadata (privacy)
3. **RGBA → RGB Conversion**: Create white background, paste with alpha mask for JPEG compatibility
4. **LANCZOS Filter**: High-quality resampling for resize/thumbnail operations
5. **Progressive JPEG**: Enable `progressive=True` for better web loading experience
6. **Filesystem Storage**: Store in `data/products/{product_id}/images/` (not database BLOBs)

### Performance Results
- Original: 142 KB → Optimized: 37 KB (73.7% reduction)
- Thumbnail: 1 KB (400x400 with aspect ratio maintained)
- EXIF data successfully stripped (verified with PIL getexif())

### ValidationError Pattern
- Domain exceptions require `field`, `value`, `reason` (not `message`)
- Example: `ValidationError(field="image", value="unknown format", reason="Unsupported...")`

### Media Processing Pattern (from audio_service.py)
- Similar structure: validate → process → save
- Use subprocess for external tools, PIL for image manipulation
- Log file sizes before/after for monitoring

