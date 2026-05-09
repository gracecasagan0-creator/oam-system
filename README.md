# Office Asset Management System

## Authors
- Grace Jayne S. Casagan
- Nikki Marie S. Cepada
- Charmele P. Ricablanca
- Jhie Ann N. Siton

## Description
The Office Asset Management System is a computerized application designed to track and manage company assets efficiently. It records asset information, assignment to employees, maintenance activities, and depreciation status. The system helps the organization ensure proper asset accountability, minimize loss or misuse, and support decision-making through organized records and accurate reporting.

## Prerequisites
Before installing and running the Admin Login and Employee Login Dashboard System, the following tools and software must be prepared:

1. Computer or laptop
2. Operating system such as Windows, macOS, or Linux
3. Code editor such as Visual Studio Code
4. Python runtime environment
5. Web browser such as Chrome, Firefox, or Edge
6. Database software such as MySQL or SQLite
7. Local server software if needed (XAMPP, WAMP, etc.)
8. Internet connection (optional) for downloading required libraries

## Installation
1. Install Flask:

```bash
pip install flask
```

2. Clone or download the project files.
3. Navigate to the project folder.
4. Run the Flask application:

```bash
python app.py
```

5. Open your browser and go to:

```text
http://127.0.0.1:5000/
```

## Usage

### For Admin
1. Add new assets to the system
2. View employee information
3. Modify or update asset details
4. Delete asset records when no longer needed
5. View all assets (available and assigned)
6. Generate reports for monitoring and auditing

### For Employees
1. View available and assigned assets
2. Borrow office assets (if allowed)
3. Return borrowed assets
4. Request maintenance for damaged items
5. Update personal profile information
6. Change account password

## Login Process (Admin and Employee)
The login process allows both admin and employee users to access the system using their credentials. The user selects a portal (Admin or Employee), then enters their username/ID and password. If the credentials are correct, the system creates a session and redirects the user to the correct dashboard.

- Admin credentials:
  - Username: `Admin`
  - Password: `1234`

- Employee credentials:
  - Username: `emp001`
  - Password: `1234`

## Modules

### Module 1: Asset Management (Inventory Setup)
This module manages all company assets. It allows the admin to create, view, update, and delete asset records. Each asset contains details such as asset ID, name, status, and condition.

**Functionalities**
- Add new asset
- View asset list
- Update asset information
- Delete asset
- Display detailed asset information

**Rules**
- Asset ID must be unique
- Asset name cannot be empty

### Module 2: Asset Assignment Management
This module handles asset assignments to employees. It tracks which employee is using each asset and records returns.

**Functionalities**
- Assign asset to employee
- Record return of asset
- View assigned assets

**Rules**
- Asset must exist before assignment
- Cannot assign unavailable assets

### Module 3: Maintenance Management
This module allows the admin to record and monitor maintenance activities for company assets.

**Functionalities**
- Record maintenance activity
- View maintenance history
- Update maintenance records

**Rules**
- Maintenance date must be valid
- Asset must exist

### Module 4: Depreciation Status
This module monitors asset depreciation over time and helps determine asset value based on age, usage, and condition.

**Functionalities**
- Calculate asset depreciation
- View depreciation status
- Track asset value over time
- Generate depreciation reports

**Rules**
- Asset must have a valid acquisition date
- Depreciation must follow a defined method (e.g., straight-line)
- Asset condition must be updated regularly

Tap to open:
https://oam-system.vercel.app/