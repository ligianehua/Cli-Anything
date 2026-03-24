# pos-system Migration Fix

## Problem
Railway deployment crashes with "Duplicate table" errors because migrations
try to create tables that already exist in the database.

## What was fixed
1. Added `if (!Schema::hasTable('...'))` checks to all `create_*` migrations from 12/24-12/26
2. Deleted duplicate stub migration `2025_12_26_113618_create_product_pricing_tiers_table.php`

## Files modified
- `2025_12_24_070331_create_uom_conversions_table.php`
- `2025_12_24_070404_create_suppliers_table.php`
- `2025_12_24_070440_create_purchase_orders_table.php`
- `2025_12_25_031621_create_role_change_requests_table.php`
- `2025_12_26_030231_create_cash_register_sessions_table.php`
- `2025_12_26_030234_create_cash_register_adjustments_table.php`
- `2025_12_26_114044_create_product_pricing_tiers_table.php`

## File deleted
- `2025_12_26_113618_create_product_pricing_tiers_table.php`

## How to apply
Copy these files to your pos-system `database/migrations/` folder, replacing the originals.
Delete `2025_12_26_113618_create_product_pricing_tiers_table.php` from your repo.
Then commit and push.
