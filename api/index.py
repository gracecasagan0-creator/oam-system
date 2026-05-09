import os
import uuid
from datetime import datetime
from abc import ABC, abstractmethod
from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# =========================
# OOP CLASSES
# =========================

class User(ABC):
    def __init__(self, user_id, name, password):
        self._user_id = user_id
        self._name = name
        self._password = password

    @property
    def user_id(self):
        return self._user_id

    @property
    def name(self):
        return self._name

    @property
    def password(self):
        return self._password

    @abstractmethod
    def login(self, username_or_id, password):
        pass

    @abstractmethod
    def get_dashboard_data(self):
        pass

class Admin(User):
    def __init__(self, user_id, name, password):
        super().__init__(user_id, name, password)

    def login(self, username, password):
        return username == "Admin" and password == "1234"

    def get_dashboard_data(self):
        return {
            "type": "admin",
            "assets": AssetManager.get_all_assets(),
            "employees": UserManager.get_all_employees(),
            "asset_requests": RequestManager.get_all_requests(),
            "maintenance_requests": MaintenanceManager.get_all_requests(),
            "depreciations": DepreciationManager.get_all_depreciations()
        }

class Employee(User):
    def __init__(self, user_id, name, password, department, position):
        super().__init__(user_id, name, password)
        self._department = department
        self._position = position

    @property
    def department(self):
        return self._department

    @property
    def position(self):
        return self._position

    def login(self, employee_id, password):
        return self._user_id == employee_id and self._password == password

    def get_dashboard_data(self):
        emp_id = self._user_id
        assigned = len([a for a in AssetManager.get_all_assets() if a.get("borrowed_by") == emp_id and a["status"] != "Maintenance"])
        available = len([a for a in AssetManager.get_all_assets() if a["status"] == "Available"])
        pending_requests = len([r for r in RequestManager.get_all_requests() if r.get("employee") == emp_id and r.get("status") == "Pending"])
        issues = len([a for a in AssetManager.get_all_assets() if a.get("borrowed_by") == emp_id and a["status"] == "Maintenance"])
        return {
            "type": "employee",
            "assigned": assigned,
            "requests": pending_requests,
            "available": available,
            "issues": issues
        }

    def to_dict(self):
        return {
            "id": self._user_id,
            "name": self._name,
            "department": self._department,
            "position": self._position,
            "password": self._password
        }

class Asset:
    def __init__(self, asset_id, name, status="Available", condition="Good", borrowed_by=None, borrow_date=None, return_date=None):
        self._asset_id = asset_id
        self._name = name
        self._status = status
        self._condition = condition
        self._borrowed_by = borrowed_by
        self._borrow_date = borrow_date
        self._return_date = return_date

    @property
    def asset_id(self):
        return self._asset_id

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, value):
        self._condition = value

    @property
    def borrowed_by(self):
        return self._borrowed_by

    @borrowed_by.setter
    def borrowed_by(self, value):
        self._borrowed_by = value

    @property
    def borrow_date(self):
        return self._borrow_date

    @borrow_date.setter
    def borrow_date(self, value):
        self._borrow_date = value

    @property
    def return_date(self):
        return self._return_date

    @return_date.setter
    def return_date(self, value):
        self._return_date = value

    def to_dict(self):
        return {
            "id": self._asset_id,
            "name": self._name,
            "status": self._status,
            "condition": self._condition,
            "borrowed_by": self._borrowed_by,
            "borrow_date": self._borrow_date,
            "return_date": self._return_date
        }

class Request:
    def __init__(self, request_id, asset_id, asset_type, quantity, reason, employee, status="Pending", date=None):
        self._request_id = request_id
        self._asset_id = asset_id
        self._asset_type = asset_type
        self._quantity = quantity
        self._reason = reason
        self._employee = employee
        self._status = status
        self._date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def request_id(self):
        return self._request_id

    @property
    def asset_id(self):
        return self._asset_id

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def to_dict(self):
        return {
            "id": self._request_id,
            "asset_id": self._asset_id,
            "asset_type": self._asset_type,
            "quantity": self._quantity,
            "reason": self._reason,
            "employee": self._employee,
            "status": self._status,
            "date": self._date
        }

class MaintenanceRequest:
    def __init__(self, asset_id, employee, issue_type, description, status="Reported", date=None):
        self._asset_id = asset_id
        self._employee = employee
        self._issue_type = issue_type
        self._description = description
        self._status = status
        self._date = date or datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "asset_id": self._asset_id,
            "employee": self._employee,
            "issue_type": self._issue_type,
            "description": self._description,
            "status": self._status,
            "date": self._date
        }

class Depreciation:
    def __init__(self, name, cost, salvage, life):
        self._name = name
        self._cost = cost
        self._salvage = salvage
        self._life = life
        self._dep = (cost - salvage) / life
        self._value = cost - self._dep

    def to_dict(self):
        return {
            "name": self._name,
            "cost": self._cost,
            "salvage": self._salvage,
            "life": self._life,
            "dep": self._dep,
            "value": self._value
        }

# =========================
# MANAGER CLASSES (Encapsulation)
# =========================

class AssetManager:
    _assets = [
        Asset("A001", "Laptop"),
        Asset("A002", "Printer")
    ]

    @classmethod
    def get_all_assets(cls):
        return [asset.to_dict() for asset in cls._assets]

    @classmethod
    def get_asset_by_id(cls, asset_id):
        return next((asset for asset in cls._assets if asset.asset_id == asset_id), None)

    @classmethod
    def add_asset(cls, asset_id, name, condition="Good"):
        if any(a.asset_id == asset_id for a in cls._assets):
            return False
        cls._assets.append(Asset(asset_id, name, condition=condition))
        return True

    @classmethod
    def update_asset(cls, asset_id, name, condition):
        asset = cls.get_asset_by_id(asset_id)
        if asset:
            asset.name = name
            asset.condition = condition
            return True
        return False

    @classmethod
    def delete_asset(cls, asset_id):
        asset = cls.get_asset_by_id(asset_id)
        if asset:
            cls._assets.remove(asset)
            return True
        return False

    @classmethod
    def assign_asset(cls, asset_id, employee_id):
        asset = cls.get_asset_by_id(asset_id)
        if asset and asset.status == "Available":
            asset.status = "Assigned"
            asset.borrowed_by = employee_id
            asset.borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        return False

    @classmethod
    def return_asset(cls, asset_id, emp_id):
        asset = cls.get_asset_by_id(asset_id)
        if asset and asset.borrowed_by == emp_id:
            asset.status = "Available"
            asset.borrowed_by = None
            asset.return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        return False

    @classmethod
    def report_issue(cls, asset_id, emp_id):
        asset = cls.get_asset_by_id(asset_id)
        if asset and asset.borrowed_by == emp_id:
            asset.status = "Maintenance"
            return True
        return False

class UserManager:
    _employees = [
        Employee("emp001", "Charm", "password123", "IT", "Developer")
    ]

    @classmethod
    def get_all_employees(cls):
        return [emp.to_dict() for emp in cls._employees]

    @classmethod
    def get_employee_by_id(cls, emp_id):
        return next((emp for emp in cls._employees if emp.user_id == emp_id), None)

    @classmethod
    def add_employee(cls, emp_id, name, department, position, password):
        if any(e.user_id == emp_id for e in cls._employees):
            return False
        cls._employees.append(Employee(emp_id, name, password, department, position))
        return True

    @classmethod
    def authenticate_employee(cls, emp_id, password):
        emp = cls.get_employee_by_id(emp_id)
        return emp.login(emp_id, password) if emp else False

class RequestManager:
    _requests = []

    @classmethod
    def get_all_requests(cls):
        return [req.to_dict() for req in cls._requests]

    @classmethod
    def add_request(cls, asset_id, asset_type, quantity, reason, employee):
        request_id = uuid.uuid4().hex[:8]
        cls._requests.append(Request(request_id, asset_id, asset_type, quantity, reason, employee))
        return True

    @classmethod
    def approve_request(cls, request_id):
        req = next((r for r in cls._requests if r.request_id == request_id), None)
        if req and req.status == "Pending":
            req.status = "Approved"
            AssetManager.assign_asset(req.asset_id, req._employee)
            return True
        return False

    @classmethod
    def reject_request(cls, request_id):
        req = next((r for r in cls._requests if r.request_id == request_id), None)
        if req:
            req.status = "Rejected"
            return True
        return False

class MaintenanceManager:
    _requests = []

    @classmethod
    def get_all_requests(cls):
        return [req.to_dict() for req in cls._requests]

    @classmethod
    def add_request(cls, asset_id, employee, issue_type, description):
        cls._requests.append(MaintenanceRequest(asset_id, employee, issue_type, description))
        AssetManager.report_issue(asset_id, employee)
        return True

class DepreciationManager:
    _depreciations = []

    @classmethod
    def get_all_depreciations(cls):
        return [dep.to_dict() for dep in cls._depreciations]

    @classmethod
    def add_depreciation(cls, name, cost, salvage, life):
        try:
            cost = float(cost)
            salvage = float(salvage)
            life = int(life)
            if cost <= salvage or life <= 0:
                return False
            cls._depreciations.append(Depreciation(name, cost, salvage, life))
            return True
        except ValueError:
            return False

# =========================
# FLASK APP
# =========================

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates")
)

app.secret_key = "secret123"

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return redirect(url_for("portal"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/portal")
def portal():
    return render_template("portal.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        admin = Admin("admin", "Admin", "1234")
        if admin.login(username, password):
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid Admin Login")
    return render_template("login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    data = Admin("admin", "Admin", "1234").get_dashboard_data()
    return render_template("admin_dashboard.html", **data)

@app.route("/add-asset", methods=["POST"])
def add_asset():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    asset_id = request.form.get("id")
    name = request.form.get("name")
    condition = request.form.get("condition")
    if not asset_id or not name:
        flash("Asset ID and Name are required")
        return redirect(url_for("admin_dashboard"))
    if not AssetManager.add_asset(asset_id, name, condition):
        flash("Asset ID already exists")
    else:
        flash("Asset added successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/update-asset", methods=["POST"])
def update_asset():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    asset_id = request.form.get("asset_id")
    name = request.form.get("name")
    condition = request.form.get("condition")
    if not asset_id or not name:
        flash("Asset ID and Name are required")
        return redirect(url_for("admin_dashboard"))
    if not AssetManager.update_asset(asset_id, name, condition):
        flash("Asset not found")
    else:
        flash("Asset updated successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/delete-asset", methods=["POST"])
def delete_asset():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    asset_id = request.form.get("asset_id")
    if not AssetManager.delete_asset(asset_id):
        flash("Asset not found")
    else:
        flash("Asset deleted successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin-request-action", methods=["POST"])
def admin_request_action():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    request_id = request.form.get("request_id")
    action = request.form.get("action")
    if not request_id or action not in {"approve", "reject"}:
        flash("Invalid request action")
        return redirect(url_for("admin_dashboard"))
    req = next((r for r in RequestManager.get_all_requests() if r.get("id") == request_id), None)
    if not req:
        flash("Request not found")
        return redirect(url_for("admin_dashboard"))
    if req.get("status") != "Pending":
        flash("This request has already been processed")
        return redirect(url_for("admin_dashboard"))
    if action == "approve":
        if RequestManager.approve_request(request_id):
            flash("Request approved and the asset was assigned.")
        else:
            flash("Request approved, but the selected asset is no longer available.")
    else:
        RequestManager.reject_request(request_id)
        flash("Request rejected.")
    return redirect(url_for("admin_dashboard"))

@app.route("/add-employee", methods=["POST"])
def add_employee():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    employee_id = request.form.get("id")
    name = request.form.get("name")
    department = request.form.get("department")
    position = request.form.get("position")
    password = request.form.get("password")
    if not employee_id or not name or not password:
        flash("Employee ID, Name, and Password are required")
        return redirect(url_for("admin_dashboard"))
    if not UserManager.add_employee(employee_id, name, department, position, password):
        flash("Employee ID already exists")
    else:
        flash("Employee added successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin-assign-asset", methods=["POST"])
def admin_assign_asset():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    asset_id = request.form.get("asset_id")
    employee_id = request.form.get("employee_id")
    if not asset_id or not employee_id:
        flash("Asset ID and Employee ID are required")
        return redirect(url_for("admin_dashboard"))
    if not AssetManager.assign_asset(asset_id, employee_id):
        flash("Asset is not available for assignment")
    else:
        flash("Asset assigned successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/add-maintenance", methods=["POST"])
def add_maintenance():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    asset_id = request.form.get("asset_id")
    issue = request.form.get("issue")
    description = request.form.get("description")
    if not asset_id or not issue:
        flash("Asset ID and Issue are required")
        return redirect(url_for("admin_dashboard"))
    MaintenanceManager.add_request(asset_id, "admin", issue, description)
    flash("Maintenance request added successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/add-depreciation", methods=["POST"])
def add_depreciation():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    name = request.form.get("name")
    cost = request.form.get("cost")
    salvage = request.form.get("salvage")
    life = request.form.get("life")
    if not DepreciationManager.add_depreciation(name, cost, salvage, life):
        flash("Invalid depreciation parameters")
    else:
        flash("Depreciation record added successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/employee-login", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "")
        password = request.form.get("password", "")
        if UserManager.authenticate_employee(employee_id, password):
            session.clear()
            session["employee"] = employee_id
            emp = UserManager.get_employee_by_id(employee_id)
            session["employee_name"] = emp.name
            return redirect(url_for("employee_dashboard"))
        flash("Invalid Employee Login")
    return render_template("employee_login.html")

@app.route("/employee-dashboard")
def employee_dashboard():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    emp = UserManager.get_employee_by_id(session["employee"])
    data = emp.get_dashboard_data()
    return render_template("employee_dashboard.html", **data)

@app.route("/request-asset", methods=["GET", "POST"])
def request_asset():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    if request.method == "POST":
        selected_asset_id = request.form.get("asset_id")
        selected_asset = AssetManager.get_asset_by_id(selected_asset_id)
        if not selected_asset or selected_asset.status != "Available":
            flash("The selected asset is no longer available.")
            return redirect(url_for("request_asset"))
        RequestManager.add_request(selected_asset_id, selected_asset.name, request.form.get("quantity"), request.form.get("reason"), session["employee"])
        return redirect(url_for("employee_dashboard"))
    available_assets = [a for a in AssetManager.get_all_assets() if a["status"] == "Available"]
    return render_template("request_asset.html", assets=available_assets)

@app.route("/report-issue", methods=["GET", "POST"])
def report_issue():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        issue_type = request.form.get("issue_type")
        description = request.form.get("description")
        MaintenanceManager.add_request(asset_id, session["employee"], issue_type, description)
        return redirect(url_for("employee_dashboard"))
    return render_template("report_issue.html", assets=AssetManager.get_all_assets())

@app.route("/assign-asset", methods=["GET", "POST"])
def assign_asset_page():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        emp_id = request.form.get("employee_id")
        AssetManager.assign_asset(asset_id, emp_id)
        return redirect(url_for("admin_dashboard"))
    return render_template("assign_asset.html", assets=AssetManager.get_all_assets(), employees=UserManager.get_all_employees())

@app.route("/view-assets")
def view_assets():
    if not session.get("admin") and not session.get("employee"):
        return redirect(url_for("portal"))
    return render_template("view_assets.html", assets=AssetManager.get_all_assets())

@app.route("/assigned-assets")
def assigned_assets():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    emp_id = session["employee"]
    user_assets = [a for a in AssetManager.get_all_assets() if a.get("borrowed_by") == emp_id]
    return render_template("assigned_assets.html", assets=user_assets)

@app.route("/return-asset", methods=["POST"])
def return_asset():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    asset_id = request.form.get("asset_id")
    emp_id = session["employee"]
    if not AssetManager.return_asset(asset_id, emp_id):
        flash("Asset not found or not assigned to you")
    else:
        flash("Asset returned successfully")
    return redirect(url_for("assigned_assets"))

@app.route("/update-profile", methods=["GET", "POST"])
def update_profile():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        department = request.form.get("department")
        contact = request.form.get("contact")
        if fullname:
            session["employee_name"] = fullname
        emp = UserManager.get_employee_by_id(session["employee"])
        if emp:
            emp._name = fullname or emp._name
            emp._department = department or emp._department
    return render_template("update_profile.html")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        emp = UserManager.get_employee_by_id(session["employee"])
        if emp.password != current_password:
            flash("Current password is incorrect")
        elif new_password != confirm_password:
            flash("New passwords do not match")
        else:
            emp._password = new_password
            flash("Password changed successfully")
            return redirect(url_for("employee_dashboard"))
    return render_template("change_password.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("portal"))

try:
    from serverless_wsgi import handle_request
    def handler(event, context):
        return handle_request(app, event, context)
except ImportError:
    if __name__ == "__main__":
        app.run()