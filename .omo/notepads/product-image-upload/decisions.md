
## Image Service Architecture Decisions - 2026-04-18

### Storage Strategy: Filesystem over Database
**Decision**: Store images in `data/products/{product_id}/images/` directory structure
**Rationale**: 
- Database BLOBs cause performance issues at scale
- Filesystem allows CDN/static serving without app layer
- Easier backup/migration of media files
- Follows existing pattern from audio_service.py

### Format Standardization: Convert to JPEG
**Decision**: All optimized images saved as progressive JPEG (quality 85)
**Rationale**:
- Consistent format simplifies downstream processing
- JPEG provides best size/quality tradeoff for photos
- Progressive loading improves perceived performance
- Quality 85 is sweet spot (minimal visual loss, good compression)

### EXIF Stripping: Privacy First
**Decision**: Strip all EXIF metadata during optimization
**Rationale**:
- EXIF can contain GPS coordinates, camera info, timestamps
- Privacy risk for user-uploaded product images
- Reduces file size slightly
- Use `ImageOps.exif_transpose()` to preserve orientation before stripping

### Validation: Magic Bytes over Extension
**Decision**: Validate format using magic bytes, not file extension
**Rationale**:
- File extensions can be spoofed
- Magic bytes are reliable format indicators
- Security best practice for user uploads
- Prevents malicious file uploads

