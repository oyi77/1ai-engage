"""Abstract repository interfaces for Product data access."""

from typing import List, Optional, Protocol

from oneai_reach.domain.models.product import (
    Product,
    ProductVariant,
    Inventory,
    ProductOverride,
)


class ProductRepository(Protocol):
    """Abstract repository for Product data access.

    Defines the contract for all product persistence operations.
    Implementations must handle SQLite or other storage backends.
    """

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID.

        Args:
            product_id: Unique product identifier

        Returns:
            Product object if found, None otherwise
        """
        ...

    def get_all(self, wa_number_id: str) -> List[Product]:
        """Get all products for a WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            List of all Product objects for this WA number
        """
        ...

    def save(self, product: Product) -> Product:
        """Save new product.

        Args:
            product: Product object to save (should not have ID set)

        Returns:
            Saved Product object with ID assigned

        Raises:
            ValueError: If product already has an ID
        """
        ...

    def update(self, product: Product) -> Product:
        """Update existing product.

        Args:
            product: Product object with ID set and updated fields

        Returns:
            Updated Product object

        Raises:
            ValueError: If product ID not found
        """
        ...

    def delete(self, product_id: str) -> bool:
        """Delete product by ID.

        Args:
            product_id: Unique product identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def search(
        self, wa_number_id: str, query: str, limit: int = 10
    ) -> List[Product]:
        """Search products by name or description.

        Args:
            wa_number_id: WhatsApp number ID
            query: Search query string
            limit: Maximum number of results (default: 10)

        Returns:
            List of matching Product objects ranked by relevance
        """
        ...

    def get_effective_product(
        self, wa_number_id: str, product_id: str
    ) -> Optional[Product]:
        """Get product with overrides merged for multi-tenancy.

        Retrieves the base product and applies any ProductOverride
        entries for the given WA number, returning the merged result.

        Args:
            wa_number_id: WhatsApp number ID
            product_id: Unique product identifier

        Returns:
            Product object with overrides applied if found, None otherwise
        """
        ...


class ProductVariantRepository(Protocol):
    """Abstract repository for ProductVariant data access.

    Defines the contract for all product variant persistence operations.
    Implementations must handle SQLite or other storage backends.
    """

    def get_by_id(self, variant_id: str) -> Optional[ProductVariant]:
        """Get product variant by ID.

        Args:
            variant_id: Unique variant identifier

        Returns:
            ProductVariant object if found, None otherwise
        """
        ...

    def get_all(self, product_id: str) -> List[ProductVariant]:
        """Get all variants for a product.

        Args:
            product_id: Product ID to filter by

        Returns:
            List of all ProductVariant objects for this product
        """
        ...

    def save(self, variant: ProductVariant) -> ProductVariant:
        """Save new product variant.

        Args:
            variant: ProductVariant object to save (should not have ID set)

        Returns:
            Saved ProductVariant object with ID assigned

        Raises:
            ValueError: If variant already has an ID
        """
        ...

    def update(self, variant: ProductVariant) -> ProductVariant:
        """Update existing product variant.

        Args:
            variant: ProductVariant object with ID set and updated fields

        Returns:
            Updated ProductVariant object

        Raises:
            ValueError: If variant ID not found
        """
        ...

    def delete(self, variant_id: str) -> bool:
        """Delete product variant by ID.

        Args:
            variant_id: Unique variant identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def search(
        self, product_id: str, query: str, limit: int = 10
    ) -> List[ProductVariant]:
        """Search variants within a product.

        Args:
            product_id: Product ID to search within
            query: Search query string
            limit: Maximum number of results (default: 10)

        Returns:
            List of matching ProductVariant objects
        """
        ...


class InventoryRepository(Protocol):
    """Abstract repository for Inventory data access.

    Defines the contract for all inventory persistence operations.
    Implementations must handle SQLite or other storage backends.
    """

    def get_by_id(self, inventory_id: str) -> Optional[Inventory]:
        """Get inventory record by ID.

        Args:
            inventory_id: Unique inventory identifier

        Returns:
            Inventory object if found, None otherwise
        """
        ...

    def get_all(self, wa_number_id: str) -> List[Inventory]:
        """Get all inventory records for a WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            List of all Inventory objects for this WA number
        """
        ...

    def save(self, inventory: Inventory) -> Inventory:
        """Save new inventory record.

        Args:
            inventory: Inventory object to save (should not have ID set)

        Returns:
            Saved Inventory object with ID assigned

        Raises:
            ValueError: If inventory already has an ID
        """
        ...

    def update(self, inventory: Inventory) -> Inventory:
        """Update existing inventory record.

        Args:
            inventory: Inventory object with ID set and updated fields

        Returns:
            Updated Inventory object

        Raises:
            ValueError: If inventory ID not found
        """
        ...

    def delete(self, inventory_id: str) -> bool:
        """Delete inventory record by ID.

        Args:
            inventory_id: Unique inventory identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def get_by_variant(self, variant_id: str) -> Optional[Inventory]:
        """Get inventory record for a product variant.

        Args:
            variant_id: Product variant ID

        Returns:
            Inventory object if found, None otherwise
        """
        ...

    def search(
        self, wa_number_id: str, query: str, limit: int = 10
    ) -> List[Inventory]:
        """Search inventory records by product name or SKU.

        Args:
            wa_number_id: WhatsApp number ID
            query: Search query string
            limit: Maximum number of results (default: 10)

        Returns:
            List of matching Inventory objects
        """
        ...


class ProductOverrideRepository(Protocol):
    """Abstract repository for ProductOverride data access.

    Defines the contract for all product override persistence operations.
    Overrides allow multi-tenancy customization of base products per WA number.
    Implementations must handle SQLite or other storage backends.
    """

    def get_by_id(self, override_id: str) -> Optional[ProductOverride]:
        """Get product override by ID.

        Args:
            override_id: Unique override identifier

        Returns:
            ProductOverride object if found, None otherwise
        """
        ...

    def get_all(self, wa_number_id: str) -> List[ProductOverride]:
        """Get all product overrides for a WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            List of all ProductOverride objects for this WA number
        """
        ...

    def save(self, override: ProductOverride) -> ProductOverride:
        """Save new product override.

        Args:
            override: ProductOverride object to save (should not have ID set)

        Returns:
            Saved ProductOverride object with ID assigned

        Raises:
            ValueError: If override already has an ID
        """
        ...

    def update(self, override: ProductOverride) -> ProductOverride:
        """Update existing product override.

        Args:
            override: ProductOverride object with ID set and updated fields

        Returns:
            Updated ProductOverride object

        Raises:
            ValueError: If override ID not found
        """
        ...

    def delete(self, override_id: str) -> bool:
        """Delete product override by ID.

        Args:
            override_id: Unique override identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def get_by_product(
        self, wa_number_id: str, product_id: str
    ) -> Optional[ProductOverride]:
        """Get override for a specific product and WA number.

        Args:
            wa_number_id: WhatsApp number ID
            product_id: Product ID

        Returns:
            ProductOverride object if found, None otherwise
        """
        ...

    def search(
        self, wa_number_id: str, query: str, limit: int = 10
    ) -> List[ProductOverride]:
        """Search product overrides by product name or override fields.

        Args:
            wa_number_id: WhatsApp number ID
            query: Search query string
            limit: Maximum number of results (default: 10)

        Returns:
            List of matching ProductOverride objects
        """
        ...
