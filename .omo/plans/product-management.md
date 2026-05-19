# Product Management Feature - Full E-Commerce Catalog

## TL;DR

> **Quick Summary**: Build complete product catalog system with variants, hybrid multi-tenancy (global + per-WA overrides), image upload, CS integration, CSV import/export, and full-text search.
> 
> **Deliverables**:
> - Product catalog with variant support (size/color combinations)
> - Hybrid multi-tenancy (global products + per-WA-number pricing/stock overrides)
> - Image upload with optimization (Pillow) + multiple images per product
> - CS engine integration (product lookup in conversations)
> - CSV bulk import/export with validation
> - Full-text search (FTS5) + filtering (category, stock status)
> - Dashboard UI for product management
> 
> **Estimated Effort**: Large (25-35 hours)
> **Parallel Execution**: YES - 5 waves
> **Critical Path**: Domain Models → Repositories → API Endpoints → Dashboard UI

---

## Context

### Original Request
User wants to separate product knowledge/catalog from general Knowledge Base Q&A system. Need dedicated product management with structured fields (Name, Description, Price, Stock, Variants, Images).

### Interview Summary
**Key Discussions**:
- **Product Variants**: YES - Need size/color/variant support with variant-specific pricing and stock
- **Product Images**: HYBRID - Support both external URLs AND file upload with optimization
- **Multi-Tenancy**: HYBRID - Global catalog (master products) + per-WA-number overrides (pricing, stock, visibility)
- **CS Integration**: Product Lookup - CS can search products by name and return product info in conversations
- **Import/Export**: YES - CSV bulk import/export with validation
- **Search/Filtering**: YES - FTS5 full-text search + filter by category/stock status

**Research Findings**:
- **Variant Pattern**: Separate tables (products → product_variants → inventory) following Saleor/Medusa/Merchant patterns
- **Multi-Tenancy**: Two-tier with COALESCE queries (global + overrides) following DevGab 2026 best practices
- **Image Upload**: FastAPI UploadFile + Pillow optimization + magic byte validation following official docs
- **CS Integration**: Extend KnowledgeEntry model with product fields, inject into KB search flow
- **CSV Format**: Shopify-inspired (one row per variant) with streaming validation

### Metis Review
**Identified Gaps** (addressed):
- Variant complexity adds 3-5x effort → Accepted by user
- Image upload requires new infrastructure → Local storage (MVP) → S3 (production)
- Hybrid multi-tenancy requires override query logic → COALESCE pattern proven in research
- CS integration requires KB extension → Extend KnowledgeEntry with product category
- Import/export requires validation pipeline → Row-level errors with downloadable CSV

---

## Work Objectives

### Core Objective
Build full-featured product catalog system integrated with existing 1ai-reach architecture, supporting variants, multi-tenancy, images, CS lookup, and bulk operations.

### Concrete Deliverables
- 6 new database tables (products, product_variants, inventory, product_overrides, product_images, variant_options)
- Domain models: Product, ProductVariant, Inventory, ProductOverride, ProductImage
- Repository interfaces + SQLite implementations
- FastAPI endpoints: CRUD, upload, import/export, search
- Image optimization service (Pillow)
- CS integration (product lookup in conversations)
- Dashboard UI: product management page with variant matrix
- CSV import/export with validation

### Definition of Done
- [ ] All database tables created with proper indexes
- [ ] Domain models with Pydantic validation
- [ ] Repository CRUD operations working
- [ ] API endpoints returning correct data
- [ ] Image upload + optimization working
- [ ] CSV import/export with validation working
- [ ] CS engine can search and return product info
- [ ] Dashboard UI can manage products with variants
- [ ] All QA scenarios pass with evidence captured

### Must Have
- Product variants with independent pricing/stock
- Hybrid multi-tenancy (global + per-WA overrides)
- Image upload with Pillow optimization
- CS integration (product lookup)
- CSV import/export with row-level validation
- FTS5 full-text search
- Dashboard product management UI

### Must NOT Have (Guardrails)
- E-commerce checkout flow (out of scope)
- Payment processing (out of scope)
- Shipping/logistics integration (out of scope)
- Multi-currency support (IDR only)
- Advanced inventory management (reorder points, suppliers)
- Order management system (Phase 2)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest for backend, playwright for frontend)
- **Automated tests**: Tests-after (implementation first, then tests)
- **Framework**: pytest (backend), playwright (frontend)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Backend/API**: Use Bash (curl) — Send requests, assert status + response fields
- **Database**: Use Bash (sqlite3) — Query tables, verify schema, check data
- **Frontend/UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **Image Processing**: Use Bash (python) — Process test image, verify output dimensions/size

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.

```
Wave 1 (Foundation - 7 tasks, can start immediately):
├── Task 1: Database schema + migrations [quick]
├── Task 2: Domain models (Product, ProductVariant, Inventory, etc.) [quick]
├── Task 3: Repository interfaces (abstract) [quick]
├── Task 4: Image optimization service [unspecified-high]
├── Task 5: CSV validation utilities [quick]
├── Task 6: Dashboard API types (TypeScript) [quick]
└── Task 7: Extend KnowledgeEntry for products [quick]

Wave 2 (Repositories - 4 tasks, after Wave 1):
├── Task 8: SQLite ProductRepository implementation [unspecified-high]
├── Task 9: SQLite ProductVariantRepository implementation [unspecified-high]
├── Task 10: SQLite InventoryRepository implementation [unspecified-high]
└── Task 11: SQLite ProductOverrideRepository implementation [unspecified-high]

Wave 3 (API Layer - 6 tasks, after Wave 2):
├── Task 12: Product CRUD endpoints [unspecified-high]
├── Task 13: Variant CRUD endpoints [unspecified-high]
├── Task 14: Image upload endpoint [unspecified-high]
├── Task 15: CSV import endpoint [deep]
├── Task 16: CSV export endpoint [unspecified-high]
└── Task 17: Product search endpoint (FTS5) [unspecified-high]

Wave 4 (Integration - 3 tasks, after Wave 3):
├── Task 18: CS engine product lookup integration [deep]
├── Task 19: webhook_server.py backward-compat layer [quick]
└── Task 20: Dashboard product management UI [visual-engineering]

Wave 5 (Final Verification - 4 tasks, after Wave 4):
├── Task F1: API integration tests [unspecified-high]
├── Task F2: Dashboard E2E tests (Playwright) [unspecified-high]
├── Task F3: CSV import/export round-trip test [unspecified-high]
└── Task F4: CS product lookup E2E test [deep]

Critical Path: Task 1 → Task 2 → Task 8 → Task 12 → Task 20
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 7 (Wave 1)
```

---

## TODOs

- [x] 1. Database Schema + Migrations

  **What to do**:
  - Create migration script `src/oneai_reach/infrastructure/database/migrations/001_create_products_tables.sql`
  - Define 6 tables: products, product_variants, inventory, product_overrides, product_images, variant_options
  - Add indexes: idx_variants_product, idx_variants_sku, idx_inventory_variant, idx_overrides_tenant_product, idx_images_product
  - Use TEXT for IDs (UUID), INTEGER for prices (cents), TEXT for timestamps (ISO format)
  - Add FOREIGN KEY constraints with ON DELETE CASCADE
  - Follow existing pattern from knowledge_base table (PRAGMA journal_mode=WAL)

  **Must NOT do**:
  - Use auto-increment for product IDs (use UUID TEXT instead)
  - Store prices as REAL (use INTEGER cents to avoid float issues)
  - Create migrations system (just _init_schema() like existing repos)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Straightforward schema definition following existing patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-7)
  - **Blocks**: Tasks 8-11 (repositories need schema)
  - **Blocked By**: None

  **References**:
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py:52-79` - Schema initialization pattern (_init_schema method)
  - `src/oneai_reach/infrastructure/database/sqlite_conversation_repository.py:52-78` - FOREIGN KEY pattern
  - Research findings: Separate tables pattern (products → variants → inventory)
  - Research findings: Two-tier multi-tenancy (products + product_overrides)

  **Acceptance Criteria**:
  - [ ] Migration script exists at correct path
  - [ ] All 6 tables defined with correct columns and types
  - [ ] All indexes created
  - [ ] FOREIGN KEY constraints with CASCADE
  - [ ] PRAGMA journal_mode=WAL included

  **QA Scenarios**:
  ```
  Scenario: Schema creates all tables successfully
    Tool: Bash (sqlite3)
    Preconditions: Fresh database file
    Steps:
      1. sqlite3 test.db < migrations/001_create_products_tables.sql
      2. sqlite3 test.db "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
      3. Assert output contains: inventory, product_images, product_overrides, product_variants, products, variant_options
    Expected Result: All 6 tables exist
    Evidence: .sisyphus/evidence/task-1-schema-tables.txt

  Scenario: Indexes are created correctly
    Tool: Bash (sqlite3)
    Preconditions: Schema applied
    Steps:
      1. sqlite3 test.db "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';"
      2. Assert output contains: idx_variants_product, idx_variants_sku, idx_inventory_variant, idx_overrides_tenant_product, idx_images_product
    Expected Result: All 5 indexes exist
    Evidence: .sisyphus/evidence/task-1-schema-indexes.txt

  Scenario: Foreign key constraints work
    Tool: Bash (sqlite3)
    Preconditions: Schema applied
    Steps:
      1. sqlite3 test.db "INSERT INTO products (id, name, base_price) VALUES ('prod-1', 'Test', 1000);"
      2. sqlite3 test.db "INSERT INTO product_variants (id, product_id, sku, price_cents) VALUES ('var-1', 'prod-1', 'SKU-1', 1000);"
      3. sqlite3 test.db "DELETE FROM products WHERE id='prod-1';"
      4. sqlite3 test.db "SELECT COUNT(*) FROM product_variants WHERE id='var-1';"
      5. Assert output is 0 (CASCADE delete worked)
    Expected Result: Variant deleted when parent product deleted
    Evidence: .sisyphus/evidence/task-1-schema-cascade.txt
  ```

  **Commit**: YES
  - Message: `feat(db): add product catalog schema with variants and multi-tenancy`
  - Files: `src/oneai_reach/infrastructure/database/migrations/001_create_products_tables.sql`
  - Pre-commit: `sqlite3 test.db < migrations/001_create_products_tables.sql && sqlite3 test.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"`

- [x] 2. Domain Models (Product, ProductVariant, Inventory, etc.)

  **What to do**:
  - Create `src/oneai_reach/domain/models/product.py`
  - Define Pydantic models: Product, ProductVariant, Inventory, ProductOverride, ProductImage, VariantOption
  - Add field validation: price > 0, stock >= 0, SKU pattern, status enum
  - Add computed properties: `available` (on_hand - reserved), `is_in_stock`, `effective_price`
  - Follow existing pattern from KnowledgeEntry (model_config, field_validator, properties)
  - Add enums: ProductStatus, VisibilityStatus, InventoryReason

  **Must NOT do**:
  - Add business logic methods (belongs in services)
  - Import infrastructure code (domain must be pure)
  - Use SQLAlchemy models (use Pydantic only)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Straightforward Pydantic model definition

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3-7)
  - **Blocks**: Tasks 8-11 (repositories need models)
  - **Blocked By**: None

  **References**:
  - `src/oneai_reach/domain/models/knowledge.py:18-87` - Pydantic model pattern with validation
  - `src/oneai_reach/domain/models/conversation.py:27-87` - Enum usage and field validation
  - Research findings: Product/Variant/Inventory structure from Saleor/Medusa

  **Acceptance Criteria**:
  - [ ] All 6 models defined with correct fields
  - [ ] Field validators for price, stock, SKU
  - [ ] Enums for status fields
  - [ ] Computed properties (available, is_in_stock)
  - [ ] model_config with from_attributes=True

  **QA Scenarios**:
  ```
  Scenario: Product model validates correctly
    Tool: Bash (python)
    Preconditions: Models file created
    Steps:
      1. python3 -c "from oneai_reach.domain.models.product import Product; p = Product(id='p1', name='Test', base_price=1000); print(p.name)"
      2. Assert output is "Test"
    Expected Result: Model instantiates without errors
    Evidence: .sisyphus/evidence/task-2-model-valid.txt

  Scenario: Price validation rejects negative values
    Tool: Bash (python)
    Preconditions: Models file created
    Steps:
      1. python3 -c "from oneai_reach.domain.models.product import ProductVariant; ProductVariant(id='v1', product_id='p1', sku='SKU1', price_cents=-100)" 2>&1
      2. Assert output contains "ValidationError" or "must be positive"
    Expected Result: Validation error raised
    Evidence: .sisyphus/evidence/task-2-model-price-validation.txt

  Scenario: Inventory available property computes correctly
    Tool: Bash (python)
    Preconditions: Models file created
    Steps:
      1. python3 -c "from oneai_reach.domain.models.product import Inventory; i = Inventory(id='i1', variant_id='v1', on_hand=100, reserved=30); print(i.available)"
      2. Assert output is "70"
    Expected Result: available = on_hand - reserved
    Evidence: .sisyphus/evidence/task-2-model-inventory-available.txt
  ```

  **Commit**: YES
  - Message: `feat(domain): add product catalog domain models with validation`
  - Files: `src/oneai_reach/domain/models/product.py`
  - Pre-commit: `python3 -c "from oneai_reach.domain.models.product import Product, ProductVariant, Inventory"`

- [x] 3. Repository Interfaces (Abstract)

  **What to do**:
  - Create `src/oneai_reach/domain/repositories/product_repository.py`
  - Define abstract interfaces: ProductRepository, ProductVariantRepository, InventoryRepository, ProductOverrideRepository
  - Define method signatures: get_by_id, get_all, save, update, delete, search, get_effective_product
  - Follow existing pattern from KnowledgeRepository (Protocol class, docstrings)
  - Add type hints for all methods

  **Must NOT do**:
  - Implement concrete logic (abstract only)
  - Import SQLite or infrastructure code
  - Add business logic (pure data access interface)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Interface definition following existing pattern

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-2, 4-7)
  - **Blocks**: Tasks 8-11 (implementations need interfaces)
  - **Blocked By**: Task 2 (needs domain models for type hints)

  **References**:
  - `src/oneai_reach/domain/repositories/knowledge_repository.py:9-216` - Abstract repository pattern
  - `src/oneai_reach/domain/repositories/conversation_repository.py` - Protocol class usage

  **Acceptance Criteria**:
  - [ ] All 4 repository interfaces defined
  - [ ] Method signatures with type hints
  - [ ] Docstrings for all methods
  - [ ] get_effective_product method for override merging

  **QA Scenarios**:
  ```
  Scenario: Repository interfaces import successfully
    Tool: Bash (python)
    Preconditions: Repository interfaces file created
    Steps:
      1. python3 -c "from oneai_reach.domain.repositories.product_repository import ProductRepository, ProductVariantRepository, InventoryRepository, ProductOverrideRepository; print('OK')"
      2. Assert output is "OK"
    Expected Result: All interfaces import without errors
    Evidence: .sisyphus/evidence/task-3-repo-interfaces-import.txt

  Scenario: ProductRepository has required methods
    Tool: Bash (python)
    Preconditions: Repository interfaces file created
    Steps:
      1. python3 -c "from oneai_reach.domain.repositories.product_repository import ProductRepository; import inspect; methods = [m for m in dir(ProductRepository) if not m.startswith('_')]; print(','.join(sorted(methods)))"
      2. Assert output contains: get_by_id, get_all, save, update, delete, search
    Expected Result: All CRUD methods defined
    Evidence: .sisyphus/evidence/task-3-repo-methods.txt
  ```

  **Commit**: YES
  - Message: `feat(domain): add product repository interfaces`
  - Files: `src/oneai_reach/domain/repositories/product_repository.py`
  - Pre-commit: `python3 -c "from oneai_reach.domain.repositories.product_repository import ProductRepository"`

- [x] 4. Image Optimization Service

  **What to do**:
  - Create `src/oneai_reach/application/product/image_service.py`
  - Implement `optimize_image(file_bytes, max_edge=2048, quality=85)` using Pillow
  - Add EXIF stripping with `ImageOps.exif_transpose()` for privacy
  - Implement `create_thumbnail(file_bytes, size=(400,400))` with LANCZOS filter
  - Add magic byte validation for JPEG/PNG/WebP
  - Convert RGBA → RGB for JPEG compatibility
  - Add `save_image(file_bytes, product_id, filename)` for local storage
  - Follow research findings: progressive JPEG, quality 85, LANCZOS resampling

  **Must NOT do**:
  - Store images in database as BLOB (use filesystem)
  - Skip EXIF stripping (privacy risk)
  - Use low-quality filters (NEAREST, BILINEAR)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Image processing requires careful implementation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-3, 5-7)
  - **Blocks**: Task 14 (upload endpoint needs image service)
  - **Blocked By**: None

  **References**:
  - Research findings: FastAPI image upload best practices (Pillow optimization)
  - Research findings: Magic byte validation for security
  - `src/oneai_reach/application/voice/audio_service.py:37-119` - Media processing pattern

  **Acceptance Criteria**:
  - [ ] optimize_image function with Pillow
  - [ ] EXIF stripping implemented
  - [ ] Thumbnail generation with LANCZOS
  - [ ] Magic byte validation
  - [ ] RGBA → RGB conversion
  - [ ] Local filesystem storage

  **QA Scenarios**:
  ```
  Scenario: Optimize image reduces file size
    Tool: Bash (python)
    Preconditions: Test image file exists (test.jpg, 5MB)
    Steps:
      1. python3 -c "from oneai_reach.application.product.image_service import optimize_image; import os; original = open('test.jpg', 'rb').read(); optimized = optimize_image(original); print(f'{len(original)},{len(optimized)}')"
      2. Parse output as original_size,optimized_size
      3. Assert optimized_size < original_size
    Expected Result: Optimized image is smaller than original
    Evidence: .sisyphus/evidence/task-4-image-optimize.txt

  Scenario: EXIF data is stripped
    Tool: Bash (python)
    Preconditions: Test image with EXIF data
    Steps:
      1. python3 -c "from PIL import Image; from oneai_reach.application.product.image_service import optimize_image; import io; original = open('test_with_exif.jpg', 'rb').read(); optimized = optimize_image(original); img = Image.open(io.BytesIO(optimized)); exif = img.getexif(); print(len(exif))"
      2. Assert output is "0"
    Expected Result: No EXIF data in optimized image
    Evidence: .sisyphus/evidence/task-4-image-exif-strip.txt

  Scenario: Magic byte validation rejects non-image files
    Tool: Bash (python)
    Preconditions: Test text file (not an image)
    Steps:
      1. python3 -c "from oneai_reach.application.product.image_service import validate_image_magic; validate_image_magic(b'not an image')" 2>&1
      2. Assert output contains "ValidationError" or "Invalid image"
    Expected Result: Validation error raised
    Evidence: .sisyphus/evidence/task-4-image-magic-validation.txt
  ```

  **Commit**: YES
  - Message: `feat(product): add image optimization service with Pillow`
  - Files: `src/oneai_reach/application/product/image_service.py`
  - Pre-commit: `python3 -c "from oneai_reach.application.product.image_service import optimize_image, create_thumbnail"`

- [x] 5. CSV Validation Utilities

  **What to do**:
  - Create `src/oneai_reach/application/product/csv_validator.py`
  - Implement `validate_product_csv(rows)` with row-level error tracking
  - Add field validators: SKU pattern, price format, stock integer, parent_sku existence
  - Implement `generate_error_report(errors, rows)` for downloadable CSV
  - Add streaming validation for large files (chunk size 50K rows)
  - Follow research findings: Shopify CSV format, row-level errors with line numbers

  **Must NOT do**:
  - Load entire CSV into memory (use streaming)
  - Skip validation (security risk)
  - Fail entire import on single error (partial import)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Validation logic following research patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-4, 6-7)
  - **Blocks**: Task 15 (import endpoint needs validator)
  - **Blocked By**: None

  **References**:
  - Research findings: CSV validation strategies (row-level errors, streaming)
  - Research findings: Shopify CSV format (one row per variant)

  **Acceptance Criteria**:
  - [ ] validate_product_csv function
  - [ ] Row-level error tracking with line numbers
  - [ ] Field validators (SKU, price, stock)
  - [ ] Error report generation
  - [ ] Streaming validation support

  **QA Scenarios**:
  ```
  Scenario: Valid CSV passes validation
    Tool: Bash (python)
    Preconditions: Valid test CSV file
    Steps:
      1. python3 -c "from oneai_reach.application.product.csv_validator import validate_product_csv; import csv; rows = list(csv.DictReader(open('test_valid.csv'))); errors = validate_product_csv(rows); print(len(errors))"
      2. Assert output is "0"
    Expected Result: No validation errors
    Evidence: .sisyphus/evidence/task-5-csv-valid.txt

  Scenario: Invalid price format is caught
    Tool: Bash (python)
    Preconditions: CSV with invalid price
    Steps:
      1. python3 -c "from oneai_reach.application.product.csv_validator import validate_product_csv; rows = [{'sku': 'SKU1', 'price': 'invalid', 'stock': '10'}]; errors = validate_product_csv(rows); print(errors[0]['field'])"
      2. Assert output is "price"
    Expected Result: Price validation error detected
    Evidence: .sisyphus/evidence/task-5-csv-price-validation.txt

  Scenario: Error report includes line numbers
    Tool: Bash (python)
    Preconditions: CSV with errors
    Steps:
      1. python3 -c "from oneai_reach.application.product.csv_validator import validate_product_csv, generate_error_report; rows = [{'sku': '', 'price': '10'}]; errors = validate_product_csv(rows); report = generate_error_report(errors, rows); print('row_number' in report)"
      2. Assert output is "True"
    Expected Result: Error report contains row numbers
    Evidence: .sisyphus/evidence/task-5-csv-error-report.txt
  ```

  **Commit**: YES
  - Message: `feat(product): add CSV validation utilities with row-level errors`
  - Files: `src/oneai_reach/application/product/csv_validator.py`
  - Pre-commit: `python3 -c "from oneai_reach.application.product.csv_validator import validate_product_csv"`

- [x] 6. Dashboard API Types (TypeScript)

  **What to do**:
  - Update `dashboard/src/lib/api.ts`
  - Add TypeScript interfaces: Product, ProductVariant, Inventory, ProductOverride, ProductImage
  - Add API helper functions: fetchProducts, createProduct, uploadImage, importCSV
  - Follow existing pattern from KBEntry, Conversation types
  - Add proper type exports

  **Must NOT do**:
  - Duplicate types (reuse existing patterns)
  - Add business logic (types only)
  - Break existing API types

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: TypeScript interface definition

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-5, 7)
  - **Blocks**: Task 20 (dashboard UI needs types)
  - **Blocked By**: None

  **References**:
  - `dashboard/src/lib/api.ts:1-135` - Existing API types pattern
  - Domain models from Task 2 (mirror structure in TypeScript)

  **Acceptance Criteria**:
  - [ ] All product-related interfaces defined
  - [ ] API helper functions added
  - [ ] Proper exports
  - [ ] No TypeScript errors

  **QA Scenarios**:
  ```
  Scenario: TypeScript types compile without errors
    Tool: Bash
    Preconditions: Types added to api.ts
    Steps:
      1. cd dashboard && npx tsc --noEmit src/lib/api.ts
      2. Assert exit code is 0
    Expected Result: No TypeScript compilation errors
    Evidence: .sisyphus/evidence/task-6-types-compile.txt
  ```

  **Commit**: YES
  - Message: `feat(dashboard): add product management API types`
  - Files: `dashboard/src/lib/api.ts`
  - Pre-commit: `cd dashboard && npx tsc --noEmit src/lib/api.ts`

- [x] 7. Extend KnowledgeEntry for Products

  **What to do**:
  - Update `src/oneai_reach/domain/models/knowledge.py`
  - Add optional fields: product_id, sku, price, stock_level, variants_json
  - Add new category: `KnowledgeCategory.PRODUCT = "product"`
  - Add `is_product` property to distinguish product entries
  - Maintain backward compatibility (all new fields optional)

  **Must NOT do**:
  - Break existing KB functionality
  - Make product fields required
  - Change existing categories

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Simple model extension

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-6)
  - **Blocks**: Task 18 (CS integration needs product category)
  - **Blocked By**: None

  **References**:
  - `src/oneai_reach/domain/models/knowledge.py:10-87` - Existing KnowledgeEntry model

  **Acceptance Criteria**:
  - [ ] Optional product fields added
  - [ ] PRODUCT category added to enum
  - [ ] is_product property implemented
  - [ ] Backward compatibility maintained

  **QA Scenarios**:
  ```
  Scenario: Existing KB entries still work
    Tool: Bash (python)
    Preconditions: KnowledgeEntry extended
    Steps:
      1. python3 -c "from oneai_reach.domain.models.knowledge import KnowledgeEntry, KnowledgeCategory; kb = KnowledgeEntry(wa_number_id='wa1', category=KnowledgeCategory.FAQ, question='Q', answer='A'); print(kb.is_product)"
      2. Assert output is "False"
    Expected Result: Non-product entries work as before
    Evidence: .sisyphus/evidence/task-7-kb-backward-compat.txt

  Scenario: Product entries can be created
    Tool: Bash (python)
    Preconditions: KnowledgeEntry extended
    Steps:
      1. python3 -c "from oneai_reach.domain.models.knowledge import KnowledgeEntry, KnowledgeCategory; kb = KnowledgeEntry(wa_number_id='wa1', category=KnowledgeCategory.PRODUCT, question='Product X', answer='Available', product_id='p1', sku='SKU1', price=1000); print(kb.is_product)"
      2. Assert output is "True"
    Expected Result: Product entries work correctly
    Evidence: .sisyphus/evidence/task-7-kb-product-entry.txt
  ```

  **Commit**: YES
  - Message: `feat(domain): extend KnowledgeEntry with product fields`
  - Files: `src/oneai_reach/domain/models/knowledge.py`
  - Pre-commit: `python3 -c "from oneai_reach.domain.models.knowledge import KnowledgeEntry, KnowledgeCategory; print(KnowledgeCategory.PRODUCT)"`

- [x] 8. SQLite ProductRepository Implementation

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/sqlite_product_repository.py`
  - Implement ProductRepository interface with all CRUD methods
  - Add `get_effective_product(wa_number_id, product_id)` with COALESCE query for overrides
  - Add `search(wa_number_id, query)` with FTS5 full-text search
  - Follow existing pattern from SQLiteKnowledgeRepository (connection, row mapping, transactions)
  - Add proper error handling (RepositoryError, NotFoundError)

  **Must NOT do**:
  - Skip transaction handling
  - Forget to close connections
  - Hardcode database path

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Complex repository with multi-tenancy logic

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 9-11)
  - **Blocks**: Task 12 (API needs repository)
  - **Blocked By**: Tasks 1-3 (needs schema, models, interfaces)

  **References**:
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py:28-537` - Repository pattern
  - Research findings: COALESCE query for override merging
  - Task 1: Database schema

  **Acceptance Criteria**:
  - [ ] All CRUD methods implemented
  - [ ] get_effective_product with COALESCE
  - [ ] FTS5 search implemented
  - [ ] Transaction handling
  - [ ] Error handling

  **QA Scenarios**:
  ```
  Scenario: Create and retrieve product
    Tool: Bash (python)
    Steps:
      1. python3 -c "from oneai_reach.infrastructure.database.sqlite_product_repository import SQLiteProductRepository; from oneai_reach.domain.models.product import Product; repo = SQLiteProductRepository('test.db'); p = Product(id='p1', name='Test', base_price=1000); repo.save(p); retrieved = repo.get_by_id('p1'); print(retrieved.name)"
      2. Assert output is "Test"
    Expected Result: Product saved and retrieved correctly
    Evidence: .sisyphus/evidence/task-8-repo-crud.txt

  Scenario: Override merging works correctly
    Tool: Bash (python)
    Steps:
      1. Create global product with base_price=1000
      2. Create override for wa_number_id='wa1' with price=800
      3. Call get_effective_product('wa1', 'p1')
      4. Assert effective_price is 800 (override takes precedence)
    Expected Result: Override price returned
    Evidence: .sisyphus/evidence/task-8-repo-override.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): implement SQLite product repository with multi-tenancy`
  - Files: `src/oneai_reach/infrastructure/database/sqlite_product_repository.py`

- [x] 9. SQLite ProductVariantRepository Implementation

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/sqlite_product_variant_repository.py`
  - Implement ProductVariantRepository interface
  - Add `find_by_product(product_id)` to get all variants for a product
  - Add `find_by_sku(sku)` for SKU lookup
  - Follow existing repository pattern

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8, 10-11)
  - **Blocks**: Task 13 (API needs repository)
  - **Blocked By**: Tasks 1-3

  **References**:
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py` - Repository pattern
  - Task 1: Database schema

  **QA Scenarios**:
  ```
  Scenario: Find variants by product ID
    Tool: Bash (python)
    Steps:
      1. Create product with 3 variants
      2. Call find_by_product('p1')
      3. Assert 3 variants returned
    Expected Result: All variants for product returned
    Evidence: .sisyphus/evidence/task-9-repo-find-variants.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): implement SQLite product variant repository`
  - Files: `src/oneai_reach/infrastructure/database/sqlite_product_variant_repository.py`

- [x] 10. SQLite InventoryRepository Implementation

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/sqlite_inventory_repository.py`
  - Implement InventoryRepository interface
  - Add `adjust_stock(variant_id, delta, reason)` with audit logging
  - Add `reserve_stock(variant_id, quantity)` and `release_stock(variant_id, quantity)`
  - Follow existing repository pattern

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8-9, 11)
  - **Blocks**: Task 13 (API needs repository)
  - **Blocked By**: Tasks 1-3

  **References**:
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py` - Repository pattern
  - Research findings: Inventory tracking with on_hand/reserved/available

  **QA Scenarios**:
  ```
  Scenario: Stock adjustment updates inventory
    Tool: Bash (python)
    Steps:
      1. Create inventory with on_hand=100
      2. Call adjust_stock(variant_id, -10, 'sale')
      3. Assert on_hand is now 90
    Expected Result: Stock adjusted correctly
    Evidence: .sisyphus/evidence/task-10-repo-adjust-stock.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): implement SQLite inventory repository with audit log`
  - Files: `src/oneai_reach/infrastructure/database/sqlite_inventory_repository.py`

- [x] 11. SQLite ProductOverrideRepository Implementation

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/sqlite_product_override_repository.py`
  - Implement ProductOverrideRepository interface
  - Add `get_override(wa_number_id, product_id)` for single override
  - Add `get_all_overrides(wa_number_id)` for all overrides for a WA number
  - Add `reset_override(wa_number_id, product_id)` to delete override (fall back to global)
  - Follow existing repository pattern

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8-10)
  - **Blocks**: Task 12 (API needs repository)
  - **Blocked By**: Tasks 1-3

  **References**:
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py` - Repository pattern
  - Research findings: Override lifecycle (create, update, delete, reset)

  **QA Scenarios**:
  ```
  Scenario: Reset override falls back to global
    Tool: Bash (python)
    Steps:
      1. Create global product with base_price=1000
      2. Create override with price=800
      3. Call reset_override('wa1', 'p1')
      4. Call get_effective_product('wa1', 'p1')
      5. Assert effective_price is 1000 (global)
    Expected Result: Override deleted, global value used
    Evidence: .sisyphus/evidence/task-11-repo-reset-override.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): implement SQLite product override repository`
  - Files: `src/oneai_reach/infrastructure/database/sqlite_product_override_repository.py`

- [x] 12. Product CRUD Endpoints

  **What to do**:
  - Create `src/oneai_reach/api/v1/products.py`
  - Implement endpoints: GET /products, GET /products/{id}, POST /products, PATCH /products/{id}, DELETE /products/{id}
  - Add query params: wa_number_id (for multi-tenancy), category, visibility
  - Return effective values (with overrides merged) when wa_number_id provided
  - Add Pydantic request/response schemas
  - Follow existing API pattern from kb.py, conversations.py

  **Must NOT do**:
  - Add business logic in routes (delegate to repositories)
  - Skip input validation
  - Return raw database rows (use Pydantic schemas)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 13-17)
  - **Blocks**: Task 20 (dashboard needs API)
  - **Blocked By**: Tasks 8, 11 (needs repositories)

  **References**:
  - `src/oneai_reach/api/v1/mcp.py:23-553` - API endpoint pattern
  - Research findings: Multi-tenancy query pattern

  **QA Scenarios**:
  ```
  Scenario: Create product via API
    Tool: Bash (curl)
    Steps:
      1. curl -X POST http://localhost:8000/api/v1/products -H "Content-Type: application/json" -d '{"name":"Test Product","base_price":1000,"category":"electronics"}' | jq '.id'
      2. Assert output is non-empty UUID
    Expected Result: Product created successfully
    Evidence: .sisyphus/evidence/task-12-api-create.txt

  Scenario: Get effective product with override
    Tool: Bash (curl)
    Steps:
      1. Create global product with base_price=1000
      2. Create override for wa_number_id='wa1' with price=800
      3. curl -s "http://localhost:8000/api/v1/products/{id}?wa_number_id=wa1" | jq '.effective_price'
      4. Assert output is 800
    Expected Result: Override price returned
    Evidence: .sisyphus/evidence/task-12-api-override.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add product CRUD endpoints with multi-tenancy`
  - Files: `src/oneai_reach/api/v1/products.py`

- [x] 13. Variant CRUD Endpoints

  **What to do**:
  - Add to `src/oneai_reach/api/v1/products.py`
  - Implement endpoints: GET /products/{id}/variants, POST /products/{id}/variants, PATCH /variants/{id}, DELETE /variants/{id}
  - Add inventory adjustment endpoint: POST /variants/{id}/inventory/adjust
  - Return variant with inventory data (on_hand, reserved, available)
  - Follow existing API pattern

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 14-17)
  - **Blocks**: Task 20 (dashboard needs API)
  - **Blocked By**: Tasks 9, 10 (needs repositories)

  **References**:
  - `src/oneai_reach/api/v1/mcp.py` - API endpoint pattern
  - Research findings: Variant-specific pricing/stock

  **QA Scenarios**:
  ```
  Scenario: Add variant to product
    Tool: Bash (curl)
    Steps:
      1. curl -X POST http://localhost:8000/api/v1/products/{id}/variants -H "Content-Type: application/json" -d '{"sku":"SKU-001","title":"Large/Red","price_cents":2499,"metadata_json":{"color":"red","size":"L"}}' | jq '.sku'
      2. Assert output is "SKU-001"
    Expected Result: Variant created successfully
    Evidence: .sisyphus/evidence/task-13-api-variant-create.txt

  Scenario: Adjust inventory
    Tool: Bash (curl)
    Steps:
      1. curl -X POST http://localhost:8000/api/v1/variants/{id}/inventory/adjust -H "Content-Type: application/json" -d '{"delta":10,"reason":"restock"}' | jq '.on_hand'
      2. Assert output is increased by 10
    Expected Result: Inventory adjusted
    Evidence: .sisyphus/evidence/task-13-api-inventory-adjust.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add variant CRUD and inventory adjustment endpoints`
  - Files: `src/oneai_reach/api/v1/products.py`

- [x] 14. Image Upload Endpoint

  **What to do**:
  - Add to `src/oneai_reach/api/v1/products.py`
  - Implement endpoint: POST /products/{id}/images (accepts multipart/form-data)
  - Use FastAPI UploadFile for file handling
  - Call image_service.optimize_image() and image_service.create_thumbnail()
  - Save to local storage: data/products/{product_id}/images/
  - Store metadata in product_images table
  - Return image URLs

  **Must NOT do**:
  - Store images in database as BLOB
  - Skip image optimization
  - Accept files without validation

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12-13, 15-17)
  - **Blocks**: Task 20 (dashboard needs API)
  - **Blocked By**: Task 4 (needs image service)

  **References**:
  - Research findings: FastAPI file upload with UploadFile
  - Task 4: Image optimization service

  **QA Scenarios**:
  ```
  Scenario: Upload image successfully
    Tool: Bash (curl)
    Steps:
      1. curl -X POST http://localhost:8000/api/v1/products/{id}/images -F "file=@test.jpg" | jq '.id'
      2. Assert output is non-empty UUID
    Expected Result: Image uploaded and optimized
    Evidence: .sisyphus/evidence/task-14-api-image-upload.txt

  Scenario: Uploaded image file exists on disk
    Tool: Bash
    Steps:
      1. Upload image via API
      2. Extract s3_key from response
      3. ls data/products/{product_id}/images/{filename}
      4. Assert file exists
    Expected Result: Image file saved to disk
    Evidence: .sisyphus/evidence/task-14-api-image-file.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add image upload endpoint with optimization`
  - Files: `src/oneai_reach/api/v1/products.py`

- [x] 15. CSV Import Endpoint

  **What to do**:
  - Add to `src/oneai_reach/api/v1/products.py`
  - Implement endpoint: POST /products/import (accepts multipart/form-data CSV)
  - Use csv_validator.validate_product_csv() for validation
  - Stream CSV parsing (don't load entire file into memory)
  - Return validation errors with row numbers if any
  - Accept valid rows, skip invalid (partial import)
  - Process in background (return 202 Accepted)

  **Must NOT do**:
  - Load entire CSV into memory
  - Fail entire import on single error
  - Block request/response cycle

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Complex streaming validation + background processing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12-14, 16-17)
  - **Blocks**: Task 20 (dashboard needs API)
  - **Blocked By**: Task 5 (needs CSV validator)

  **References**:
  - Research findings: CSV streaming validation
  - Task 5: CSV validation utilities
  - `dashboard/src/app/api/kb/import/route.ts:8-51` - Existing import pattern

  **QA Scenarios**:
  ```
  Scenario: Import valid CSV successfully
    Tool: Bash (curl)
    Steps:
      1. curl -X POST http://localhost:8000/api/v1/products/import -F "file=@test_valid.csv" | jq '.imported'
      2. Assert output > 0
    Expected Result: Valid rows imported
    Evidence: .sisyphus/evidence/task-15-api-import-valid.txt

  Scenario: Import returns validation errors
    Tool: Bash (curl)
    Steps:
      1. curl -X POST http://localhost:8000/api/v1/products/import -F "file=@test_invalid.csv" | jq '.errors | length'
      2. Assert output > 0
    Expected Result: Validation errors returned
    Evidence: .sisyphus/evidence/task-15-api-import-errors.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add CSV import endpoint with streaming validation`
  - Files: `src/oneai_reach/api/v1/products.py`

- [x] 16. CSV Export Endpoint

  **What to do**:
  - Add to `src/oneai_reach/api/v1/products.py`
  - Implement endpoint: GET /products/export?wa_number_id={id}&format=csv
  - Export products with variants (one row per variant, Shopify format)
  - Include effective values (with overrides) when wa_number_id provided
  - Return CSV file with proper Content-Type and Content-Disposition headers
  - Support filtering by category, visibility

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12-15, 17)
  - **Blocks**: Task 20 (dashboard needs API)
  - **Blocked By**: Task 8 (needs repository)

  **References**:
  - Research findings: Shopify CSV export format
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py:513-537` - Export pattern

  **QA Scenarios**:
  ```
  Scenario: Export products to CSV
    Tool: Bash (curl)
    Steps:
      1. curl -s "http://localhost:8000/api/v1/products/export?format=csv" -o export.csv
      2. wc -l export.csv
      3. Assert line count > 1 (header + data)
    Expected Result: CSV file generated
    Evidence: .sisyphus/evidence/task-16-api-export.txt

  Scenario: Export includes variants
    Tool: Bash (curl)
    Steps:
      1. Create product with 3 variants
      2. curl -s "http://localhost:8000/api/v1/products/export?format=csv" | grep -c "SKU-"
      3. Assert count is 3
    Expected Result: All variants exported
    Evidence: .sisyphus/evidence/task-16-api-export-variants.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add CSV export endpoint with variant support`
  - Files: `src/oneai_reach/api/v1/products.py`

- [x] 17. Product Search Endpoint (FTS5)

  **What to do**:
  - Add to `src/oneai_reach/api/v1/products.py`
  - Implement endpoint: GET /products/search?q={query}&wa_number_id={id}
  - Use FTS5 full-text search on product name and description
  - Add filters: category, stock_status (in_stock/out_of_stock), min_price, max_price
  - Return effective values (with overrides) when wa_number_id provided
  - Add pagination (limit, offset)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12-16)
  - **Blocks**: Task 18 (CS integration needs search)
  - **Blocked By**: Task 8 (needs repository with FTS5)

  **References**:
  - `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py:313-334` - FTS5 search pattern
  - Research findings: FTS5 full-text search

  **QA Scenarios**:
  ```
  Scenario: Search finds products by name
    Tool: Bash (curl)
    Steps:
      1. curl -s "http://localhost:8000/api/v1/products/search?q=shirt" | jq '.results | length'
      2. Assert output > 0
    Expected Result: Products found
    Evidence: .sisyphus/evidence/task-17-api-search.txt

  Scenario: Filter by stock status works
    Tool: Bash (curl)
    Steps:
      1. curl -s "http://localhost:8000/api/v1/products/search?stock_status=in_stock" | jq '.results[].stock_level'
      2. Assert all values > 0
    Expected Result: Only in-stock products returned
    Evidence: .sisyphus/evidence/task-17-api-filter-stock.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add product search endpoint with FTS5 and filters`
  - Files: `src/oneai_reach/api/v1/products.py`

- [x] 18. CS Engine Product Lookup Integration

  **What to do**:
  - Create `src/oneai_reach/application/customer_service/product_search_service.py`
  - Implement `detect_product_inquiry(message_text)` to detect product intent (keywords: "produk", "varian", "harga", "stock", "ada gak")
  - Implement `search_products(wa_number_id, query)` wrapping product repository search
  - Update `src/oneai_reach/application/customer_service/cs_engine_service.py`
  - Add product search after KB search in `handle_inbound_message()`
  - Format product results for LLM prompt: "Product: {name}, Price: Rp{price}, Stock: {available}, Variants: {list}"
  - Update response generation prompt to handle product info naturally

  **Must NOT do**:
  - Break existing KB search functionality
  - Add product search if not product inquiry
  - Return raw product data (format for conversation)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Complex integration with existing CS flow

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4 (sequential after Wave 3)
  - **Blocks**: Task F4 (E2E test needs CS integration)
  - **Blocked By**: Tasks 7, 17 (needs extended KB model and search endpoint)

  **References**:
  - `src/oneai_reach/application/customer_service/cs_engine_service.py:323-532` - Message handling flow
  - `src/oneai_reach/application/customer_service/playbook_service.py:153-226` - Scenario detection pattern
  - Task 7: Extended KnowledgeEntry with product fields

  **QA Scenarios**:
  ```
  Scenario: Product inquiry detected correctly
    Tool: Bash (python)
    Steps:
      1. python3 -c "from oneai_reach.application.customer_service.product_search_service import detect_product_inquiry; result = detect_product_inquiry('Ada produk baju gak?'); print(result)"
      2. Assert output is "True"
    Expected Result: Product inquiry detected
    Evidence: .sisyphus/evidence/task-18-cs-detect-inquiry.txt

  Scenario: CS response includes product info
    Tool: Bash (python)
    Steps:
      1. Create test product with stock
      2. Simulate incoming message: "Ada baju merah?"
      3. Call cs_engine.handle_inbound_message()
      4. Assert response contains product name and price
    Expected Result: Product info in response
    Evidence: .sisyphus/evidence/task-18-cs-response-product.txt

  Scenario: Out-of-stock products mentioned correctly
    Tool: Bash (python)
    Steps:
      1. Create test product with stock=0
      2. Simulate incoming message about that product
      3. Assert response mentions "habis" or "tidak tersedia"
    Expected Result: Out-of-stock mentioned
    Evidence: .sisyphus/evidence/task-18-cs-out-of-stock.txt
  ```

  **Commit**: YES
  - Message: `feat(cs): integrate product lookup into conversation flow`
  - Files: `src/oneai_reach/application/customer_service/product_search_service.py`, `src/oneai_reach/application/customer_service/cs_engine_service.py`

- [x] 19. webhook_server.py Backward-Compat Layer

  **What to do**:
  - Update `webhook_server.py`
  - Add Flask routes: GET /api/products, POST /api/products, GET /api/products/{id}/variants
  - Proxy requests to FastAPI server (http://localhost:8000/api/v1/products)
  - Follow existing pattern from KB endpoints (lines 280-316)
  - Maintain backward compatibility with dashboard API proxy

  **Must NOT do**:
  - Add business logic (just proxy)
  - Break existing KB/conversation endpoints
  - Change response format

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Simple proxy layer following existing pattern

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Task 18, 20)
  - **Blocks**: Task 20 (dashboard needs backward-compat)
  - **Blocked By**: Task 12 (needs FastAPI endpoints)

  **References**:
  - `webhook_server.py:280-316` - Existing KB endpoint proxy pattern
  - `webhook_server.py:78-736` - Flask app structure

  **QA Scenarios**:
  ```
  Scenario: Proxy forwards requests correctly
    Tool: Bash (curl)
    Steps:
      1. curl -s http://localhost:8766/api/products | jq '.count'
      2. Assert output >= 0
    Expected Result: Request proxied to FastAPI
    Evidence: .sisyphus/evidence/task-19-proxy-forward.txt

  Scenario: Dashboard API proxy still works
    Tool: Bash (curl)
    Steps:
      1. curl -s http://localhost:8502/api/products | jq '.count'
      2. Assert output >= 0
    Expected Result: Dashboard → webhook_server → FastAPI chain works
    Evidence: .sisyphus/evidence/task-19-dashboard-proxy.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add product endpoints to webhook_server backward-compat layer`
  - Files: `webhook_server.py`

- [x] 20. Dashboard Product Management UI

  **What to do**:
  - Create `dashboard/src/app/(dashboard)/products/page.tsx`
  - Implement product list with table (name, category, base_price, stock, actions)
  - Add WA number selector dropdown (for viewing effective prices with overrides)
  - Implement Add/Edit product dialog with form (name, description, category, base_price, base_stock)
  - Add variant management: variant matrix UI (size × color grid) with inline editing
  - Add image upload: drag-drop or file input with preview and thumbnail display
  - Add CSV import/export buttons with validation error display
  - Follow existing pattern from KB page (SWR, Dialog, Table, shadcn/ui components)
  - Add to sidebar navigation between KB and Pipeline

  **Must NOT do**:
  - Use server components (use "use client")
  - Invent new UI patterns (follow KB page)
  - Skip loading states

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []
  - **Reason**: Complex UI with multiple features

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4 (sequential after Wave 3)
  - **Blocks**: Task F2 (E2E test needs UI)
  - **Blocked By**: Tasks 12-17, 19 (needs all API endpoints and proxy)

  **References**:
  - `dashboard/src/app/(dashboard)/kb/page.tsx:1-180` - Existing page pattern
  - `dashboard/src/components/sidebar.tsx:8-40` - Navigation pattern
  - Task 6: TypeScript API types

  **QA Scenarios**:
  ```
  Scenario: Product page loads without errors
    Tool: Playwright
    Steps:
      1. Navigate to http://localhost:8502/products
      2. Wait for page load
      3. Assert page title contains "Products" or "Product Management"
    Expected Result: Page loads successfully
    Evidence: .sisyphus/evidence/task-20-ui-page-load.png

  Scenario: Create product form works
    Tool: Playwright
    Steps:
      1. Navigate to /products
      2. Click "Add" button
      3. Fill form: name="Test Product", base_price=1000
      4. Click "Save"
      5. Assert product appears in table
    Expected Result: Product created via UI
    Evidence: .sisyphus/evidence/task-20-ui-create-product.png

  Scenario: Image upload shows preview
    Tool: Playwright
    Steps:
      1. Open product edit dialog
      2. Upload test image
      3. Assert preview image displayed
    Expected Result: Image preview shown
    Evidence: .sisyphus/evidence/task-20-ui-image-preview.png

  Scenario: CSV import validation errors displayed
    Tool: Playwright
    Steps:
      1. Click "Import" button
      2. Upload invalid CSV
      3. Assert error messages displayed with row numbers
    Expected Result: Validation errors shown
    Evidence: .sisyphus/evidence/task-20-ui-import-errors.png
  ```

  **Commit**: YES
  - Message: `feat(dashboard): add product management UI with variants and images`
  - Files: `dashboard/src/app/(dashboard)/products/page.tsx`, `dashboard/src/components/sidebar.tsx`

---

## Final Verification Wave



- [x] F1. API Integration Tests

  **What to do**:
  - Create `tests/integration/test_product_api.py`
  - Test full CRUD flow: create product → add variants → update inventory → get effective product
  - Test multi-tenancy: global product + WA override → verify COALESCE query
  - Test image upload: upload → optimize → retrieve
  - Test CSV import: valid CSV → import → verify data
  - Use pytest with fixtures for database setup/teardown

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks F2-F4)
  - **Blocks**: None
  - **Blocked By**: Tasks 1-19 (all implementation complete)

  **QA Scenarios**:
  ```
  Scenario: Full CRUD flow works end-to-end
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/integration/test_product_api.py::test_full_crud_flow -v
      2. Assert exit code is 0
    Expected Result: All CRUD operations pass
    Evidence: .sisyphus/evidence/task-f1-crud-flow.txt
  ```

  **Commit**: YES
  - Message: `test(product): add API integration tests`
  - Files: `tests/integration/test_product_api.py`

- [x] F2. Dashboard E2E Tests (Playwright)

  **What to do**:
  - Create `dashboard/tests/e2e/products.spec.ts`
  - Test product creation flow: navigate → fill form → add variants → save
  - Test image upload: select file → preview → upload → verify thumbnail
  - Test CSV import: upload CSV → view validation → confirm import
  - Use Playwright with screenshots for evidence

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks F1, F3-F4)
  - **Blocks**: None
  - **Blocked By**: Tasks 1-20 (all implementation complete)

  **QA Scenarios**:
  ```
  Scenario: Product creation flow works in UI
    Tool: Playwright
    Steps:
      1. npx playwright test tests/e2e/products.spec.ts
      2. Assert exit code is 0
    Expected Result: All UI tests pass
    Evidence: .sisyphus/evidence/task-f2-ui-tests.txt
  ```

  **Commit**: YES
  - Message: `test(dashboard): add product management E2E tests`
  - Files: `dashboard/tests/e2e/products.spec.ts`

- [x] F3. CSV Import/Export Round-Trip Test

  **What to do**:
  - Create test: export products → import to new DB → verify data integrity
  - Test variant preservation: export with variants → import → verify all variants exist
  - Test error handling: import invalid CSV → verify error report
  - Use pytest with temp database

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks F1-F2, F4)
  - **Blocks**: None
  - **Blocked By**: Tasks 1-19 (all implementation complete)

  **QA Scenarios**:
  ```
  Scenario: Export → Import preserves all data
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/integration/test_csv_roundtrip.py -v
      2. Assert exit code is 0
    Expected Result: Data integrity maintained
    Evidence: .sisyphus/evidence/task-f3-csv-roundtrip.txt
  ```

  **Commit**: YES
  - Message: `test(product): add CSV import/export round-trip tests`
  - Files: `tests/integration/test_csv_roundtrip.py`

- [x] F4. CS Product Lookup E2E Test

  **What to do**:
  - Create test: send WhatsApp message with product query → verify CS response includes product info
  - Test stock awareness: query out-of-stock product → verify CS mentions unavailability
  - Test variant listing: query product with variants → verify CS lists all options
  - Use mock WAHA webhook + real CS engine

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks F1-F3)
  - **Blocks**: None
  - **Blocked By**: Tasks 1-19 (all implementation complete)

  **QA Scenarios**:
  ```
  Scenario: CS engine returns product info in conversation
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/integration/test_cs_product_lookup.py -v
      2. Assert exit code is 0
    Expected Result: CS correctly handles product queries
    Evidence: .sisyphus/evidence/task-f4-cs-lookup.txt
  ```

  **Commit**: YES
  - Message: `test(cs): add product lookup E2E tests`
  - Files: `tests/integration/test_cs_product_lookup.py`

---

## Commit Strategy

- **Wave 1**: 7 individual commits (foundation tasks)
- **Wave 2**: 4 individual commits (repository implementations)
- **Wave 3**: 6 individual commits (API endpoints)
- **Wave 4**: 3 individual commits (integration tasks)
- **Wave 5**: 4 individual commits (test tasks)

---

## Success Criteria

### Verification Commands
```bash
# Database schema
sqlite3 data/1ai_reach.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'product%';"
# Expected: products, product_variants, product_images, product_overrides

# API health
curl -s http://localhost:8000/api/v1/products | jq '.count'
# Expected: >= 0

# Dashboard build
cd dashboard && npm run build
# Expected: exit code 0

# Tests
pytest tests/integration/test_product_api.py -v
# Expected: all pass

cd dashboard && npx playwright test tests/e2e/products.spec.ts
# Expected: all pass
```

### Final Checklist
- [ ] All 6 database tables exist with indexes
- [ ] All domain models with validation working
- [ ] All repository CRUD operations working
- [ ] All API endpoints returning correct data
- [ ] Image upload + optimization working
- [ ] CSV import/export with validation working
- [ ] CS engine product lookup working
- [ ] Dashboard product management UI working
- [ ] All tests passing
- [ ] All evidence files captured
