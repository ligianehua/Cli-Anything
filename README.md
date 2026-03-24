# VeraPOS CLI

Command-line interface for the [VeraPOS](https://github.com/aljayvee/pos-system) Point of Sale system.

Manage products, sales, inventory, customers, cash register, reports and more — all from your terminal.

## Installation

```bash
git clone https://github.com/ligianehua/PR.git
cd PR
pip install -e .
```

## Quick Start

```bash
# 1. Point to your POS server
pos set-url http://localhost:8000

# 2. Login
pos login -e admin@example.com -p yourpassword

# 3. Start using
pos products list
pos sales new -i '[{"product_id":1,"quantity":2}]' -p cash
pos reports dashboard
```

## Commands

### Authentication
```bash
pos login                          # Login to POS system
pos logout                         # Logout
pos set-url <url>                  # Set server URL
pos auth-status                    # Check connection status
```

### Products
```bash
pos products list                  # List all products
pos products list -s "rice"        # Search products
pos products show 1                # Show product details
pos products create --name "Coffee" --sku "CFE001" --price 120
pos products update 1 --price 150  # Update price
pos products delete 1              # Soft delete
pos products import data.csv       # Bulk import
```

### Categories
```bash
pos categories list                # List categories
pos categories create -n "Drinks"  # Create category
```

### Inventory
```bash
pos inventory list                 # View stock levels
pos inventory list --low-stock     # Low stock alerts
pos inventory adjust -p 1 -q -5 -t spoilage  # Adjust stock
pos inventory history              # Adjustment history
pos inventory export -o stock.csv  # Export inventory
```

### Sales & Transactions
```bash
pos sales new -i '[{"product_id":1,"quantity":3}]' -p cash -a 500
pos sales list                     # Recent transactions
pos sales list -d 2025-01-15       # Filter by date
pos sales show 42                  # Receipt details
pos sales return 42 -r "defective" # Process return
```

### Customers
```bash
pos customers list                 # List customers
pos customers create -n "Juan" -p "09171234567"
pos customers show 1               # Customer details
```

### Credits (Utang)
```bash
pos credits list                   # Outstanding credits
pos credits list --status overdue  # Overdue debts
pos credits pay 1 -a 500           # Record payment
pos credits history                # Payment history
pos credits export                 # Export credit data
```

### Cash Register
```bash
pos register open -b 5000          # Open with ₱5,000 float
pos register status                # Check current session
pos register close -c 12500        # Close & count cash
pos register reading x             # X reading (midday)
pos register reading z             # Z reading (end of day)
```

### Reports & Analytics
```bash
pos reports dashboard              # Today's summary
pos reports sales --from 2025-01-01 --to 2025-01-31
pos reports inventory              # Stock report
pos reports forecast               # Sales forecast
pos reports export -t sales -f pdf -o report.pdf
```

### Users
```bash
pos users list                     # List all users
pos users toggle 3                 # Enable/disable user
pos users restore 5                # Restore archived user
pos users delete 5                 # Permanent delete
```

### Suppliers & Purchases
```bash
pos suppliers list                 # List suppliers
pos suppliers create -n "ABC Trading" -c "09171234567"
pos purchases list                 # Purchase orders
```

### System Settings
```bash
pos settings show                  # View settings
pos settings update -k store_name -v "My Store"
pos settings backup -o backup.sql  # Download backup
pos settings restore backup.sql    # Restore from backup
pos settings logs                  # View activity logs
```

## Configuration

Config is stored in `~/.pos-cli/config.json`. You can also use environment variables:

```bash
export POS_URL=http://myserver:8000
```

## Requirements

- Python 3.9+
- A running [VeraPOS](https://github.com/aljayvee/pos-system) instance

## Tech Stack

- [click](https://click.palletsprojects.com/) — CLI framework
- [requests](https://requests.readthedocs.io/) — HTTP client
- [rich](https://rich.readthedocs.io/) — Terminal formatting & tables

## License

MIT
