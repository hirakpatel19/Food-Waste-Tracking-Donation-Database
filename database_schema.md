# Database Schema Design

## Entity Relationship Diagram (ERD)

### Tables Overview

1. **users** - Stores user accounts for both Donors and NGOs
2. **food_donations** - Stores food donation records
3. **claims** - Tracks which NGO claimed which donation
4. **categories** - Food categories for better organization

## Table Structures

### 1. Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('donor', 'ngo') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    organization_name VARCHAR(100), -- For NGOs only
    registration_number VARCHAR(50), -- For NGOs only
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Food Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Food Donations Table
```sql
CREATE TABLE food_donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    unit VARCHAR(20) NOT NULL, -- kg, pieces, liters, etc.
    expiry_date DATE NOT NULL,
    pickup_address TEXT NOT NULL,
    pickup_city VARCHAR(50) NOT NULL,
    pickup_instructions TEXT,
    status ENUM('available', 'claimed', 'completed', 'expired') DEFAULT 'available',
    is_perishable BOOLEAN DEFAULT TRUE,
    dietary_info VARCHAR(100), -- vegetarian, vegan, gluten-free, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

### 4. Claims Table
```sql
CREATE TABLE claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donation_id INTEGER NOT NULL,
    ngo_id INTEGER NOT NULL,
    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pickup_scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    status ENUM('claimed', 'scheduled', 'picked_up', 'completed', 'cancelled') DEFAULT 'claimed',
    notes TEXT,
    FOREIGN KEY (donation_id) REFERENCES food_donations(id) ON DELETE CASCADE,
    FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(donation_id) -- One donation can only be claimed by one NGO
);
```

## Relationships

1. **Users (1) → Food Donations (Many)**
   - One donor can have multiple food donations
   
2. **Categories (1) → Food Donations (Many)**
   - One category can have multiple food donations
   
3. **Food Donations (1) → Claims (1)**
   - One food donation can have at most one claim
   
4. **Users/NGO (1) → Claims (Many)**
   - One NGO can claim multiple donations

## Sample Data

### Categories
```sql
INSERT INTO categories (name, description) VALUES 
('Fruits & Vegetables', 'Fresh produce, fruits, and vegetables'),
('Bakery Items', 'Bread, pastries, and baked goods'),
('Dairy Products', 'Milk, cheese, yogurt, and dairy items'),
('Meat & Seafood', 'Fresh and cooked meat, poultry, and seafood'),
('Prepared Meals', 'Ready-to-eat meals and cooked food'),
('Dry Goods', 'Rice, pasta, cereals, and non-perishable items'),
('Beverages', 'Juices, soft drinks, and other beverages'),
('Other', 'Miscellaneous food items');
```

## Indexes for Performance

```sql
-- Indexes for better query performance
CREATE INDEX idx_food_donations_status ON food_donations(status);
CREATE INDEX idx_food_donations_expiry ON food_donations(expiry_date);
CREATE INDEX idx_food_donations_city ON food_donations(pickup_city);
CREATE INDEX idx_food_donations_donor ON food_donations(donor_id);
CREATE INDEX idx_claims_ngo ON claims(ngo_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_email ON users(email);
```

## Business Rules

1. Only users with `user_type='donor'` can create food donations
2. Only users with `user_type='ngo'` can claim donations
3. Food donations automatically expire when `expiry_date < CURRENT_DATE`
4. A donation can only be claimed once (enforced by UNIQUE constraint)
5. NGO users must have `organization_name` and `registration_number`
6. Donors can edit/delete their donations only if status is 'available'
7. Claims can be cancelled by either the NGO or the donor