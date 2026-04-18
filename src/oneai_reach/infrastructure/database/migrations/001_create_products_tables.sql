-- Product Catalog Schema Migration
-- Wave 1: Core product management tables with inventory tracking

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Prerequisite: wa_numbers table (if not exists)
-- This table is used by multiple systems (KB, conversations, products)
CREATE TABLE IF NOT EXISTS wa_numbers (
    id TEXT PRIMARY KEY,
    session_name TEXT UNIQUE NOT NULL,
    phone TEXT,
    label TEXT,
    mode TEXT DEFAULT 'cs',
    kb_enabled INTEGER DEFAULT 1,
    auto_reply INTEGER DEFAULT 1,
    persona TEXT,
    status TEXT DEFAULT 'inactive',
    webhook_url TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Master product catalog (global, shared across all WA numbers)
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    base_price_cents INTEGER NOT NULL,
    currency TEXT DEFAULT 'IDR',
    sku TEXT UNIQUE,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Product variants (size, color, configuration combinations)
CREATE TABLE IF NOT EXISTS product_variants (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    sku TEXT UNIQUE,
    variant_name TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    weight_grams INTEGER,
    dimensions_json TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Inventory tracking per variant
CREATE TABLE IF NOT EXISTS inventory (
    id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL UNIQUE,
    quantity_available INTEGER DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    quantity_sold INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    last_restocked_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE
);

-- Per-WA-number pricing and stock overrides
CREATE TABLE IF NOT EXISTS product_overrides (
    id TEXT PRIMARY KEY,
    wa_number_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    override_price_cents INTEGER,
    override_stock_quantity INTEGER,
    is_hidden INTEGER DEFAULT 0,
    custom_name TEXT,
    custom_description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(wa_number_id, product_id)
);

-- Product images (multiple per product)
CREATE TABLE IF NOT EXISTS product_images (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    image_url TEXT NOT NULL,
    alt_text TEXT,
    display_order INTEGER DEFAULT 0,
    is_primary INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Variant options (size/color/material choices)
CREATE TABLE IF NOT EXISTS variant_options (
    id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL,
    option_name TEXT NOT NULL,
    option_value TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_sku ON product_variants(sku);
CREATE INDEX IF NOT EXISTS idx_inventory_variant ON inventory(variant_id);
CREATE INDEX IF NOT EXISTS idx_overrides_tenant_product ON product_overrides(wa_number_id, product_id);
CREATE INDEX IF NOT EXISTS idx_images_product ON product_images(product_id);
