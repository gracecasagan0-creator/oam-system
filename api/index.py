import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates")
)

app.secret_key = "secret123"

# =========================
# ACCOUNTS
# =========================
ADMIN = {"username": "Admin", "password": "1234"}
EMPLOYEE = {"employee_id": "", "password": "1234"}

# =========================
# DATA
# =========================
assets = [
    {"id": "A001", "name": "Laptop", "status": "Available", "borrowed_by": None},
    {"id": "A002", "name": "Printer", "status": "Available", "borrowed_by": None}
]

employees = [
    {"id": "emp001", "name": "Charm", "department": "IT", "position": "Developer", "password": "password123"}
]

asset_requests = []
maintenance_requests = []
depreciations = []

# =========================
# HOME / PORTAL
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

# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN["username"] and password == ADMIN["password"]:
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Invalid Admin Login")
    return render_template("login.html")

# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template(
        "admin_dashboard.html",
        assets=assets,
        employees=employees,
        asset_requests=asset_requests,
        maintenance_requests=maintenance_requests,
        depreciations=depreciations
    )

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

    if any(a["id"] == asset_id for a in assets):
        flash("Asset ID already exists")
        return redirect(url_for("admin_dashboard"))

    assets.append({
        "id": asset_id,
        "name": name,
        "status": "Available",
        "condition": condition or "Good",
        "borrowed_by": None,
        "borrow_date": None,
        "return_date": None
    })

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

    asset = next((a for a in assets if a["id"] == asset_id), None)
    if not asset:
        flash("Asset not found")
        return redirect(url_for("admin_dashboard"))

    asset["name"] = name
    asset["condition"] = condition or asset.get("condition", "Good")

    flash("Asset updated successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/delete-asset", methods=["POST"])
def delete_asset():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    asset_id = request.form.get("asset_id")
    asset = next((a for a in assets if a["id"] == asset_id), None)
    if asset:
        assets.remove(asset)
        flash("Asset deleted successfully")
    else:
        flash("Asset not found")

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

    req = next((r for r in asset_requests if r.get("id") == request_id), None)
    if not req:
        flash("Request not found")
        return redirect(url_for("admin_dashboard"))

    if req.get("status") != "Pending":
        flash("This request has already been processed")
        return redirect(url_for("admin_dashboard"))

    if action == "approve":
        req["status"] = "Approved"
        available_asset = next(
            (a for a in assets if a.get("id") == req.get("asset_id") and a.get("status") == "Available"),
            None
        )
        if available_asset:
            available_asset["borrowed_by"] = req.get("employee")
            available_asset["status"] = "Assigned"
            available_asset["borrow_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            available_asset["return_date"] = None
            flash("Request approved and the asset was assigned.")
        else:
            flash("Request approved, but the selected asset is no longer available.")
    else:
        req["status"] = "Rejected"
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

    if any(e["id"] == employee_id for e in employees):
        flash("Employee ID already exists")
        return redirect(url_for("admin_dashboard"))

    employees.append({
        "id": employee_id,
        "name": name,
        "department": department or "General",
        "position": position or "Staff",
        "password": password
    })

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

    asset = next((a for a in assets if a["id"] == asset_id), None)
    employee = next((e for e in employees if e["id"] == employee_id), None)

    if not asset:
        flash("Asset not found")
        return redirect(url_for("admin_dashboard"))

    if not employee:
        flash("Employee not found")
        return redirect(url_for("admin_dashboard"))

    if asset["status"] != "Available":
        flash("Asset is not available for assignment")
        return redirect(url_for("admin_dashboard"))

    asset["status"] = "Assigned"
    asset["borrowed_by"] = employee_id
    asset["borrow_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    asset["return_date"] = None

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

    asset = next((a for a in assets if a["id"] == asset_id), None)
    if not asset:
        flash("Asset not found")
        return redirect(url_for("admin_dashboard"))

    maintenance_requests.append({
        "id": asset_id,
        "asset_id": asset_id,
        "issue_type": issue,
        "description": description or "",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "Pending"
    })

    asset["status"] = "Maintenance"

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

    try:
        cost = float(cost)
        salvage = float(salvage)
        life = int(life)
    except ValueError:
        flash("Invalid numeric values")
        return redirect(url_for("admin_dashboard"))

    if cost <= salvage or life <= 0:
        flash("Invalid depreciation parameters")
        return redirect(url_for("admin_dashboard"))

    dep = (cost - salvage) / life
    value = cost - dep

    depreciations.append({
        "name": name,
        "cost": cost,
        "salvage": salvage,
        "life": life,
        "dep": dep,
        "value": value
    })

    flash("Depreciation record added successfully")
    return redirect(url_for("admin_dashboard"))

# =========================
# EMPLOYEE LOGIN
# =========================
@app.route("/employee-login", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "")
        password = request.form.get("password", "")

        employee = next((e for e in employees if e["id"] == employee_id and e.get("password") == password), None)
        if employee:
            session.clear()
            session["employee"] = employee_id
            session["employee_name"] = employee["name"]
            return redirect(url_for("employee_dashboard"))

        flash("Invalid Employee Login")

    return render_template("employee_login.html")

# =========================
# EMPLOYEE DASHBOARD
# =========================
@app.route("/employee-dashboard")
def employee_dashboard():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))

    emp_id = session["employee"]

    assigned = len([a for a in assets if a.get("borrowed_by") == emp_id and a["status"] != "Maintenance"])
    available = len([a for a in assets if a["status"] == "Available"])

    pending_requests = len([
        r for r in asset_requests
        if r.get("employee") == emp_id and r.get("status") == "Pending"
    ])

    issues = len([
        a for a in assets
        if a.get("borrowed_by") == emp_id and a["status"] == "Maintenance"
    ])

    return render_template(
        "employee_dashboard.html",
        assigned=assigned,
        requests=pending_requests,
        available=available,
        issues=issues
    )

# =========================
# REQUEST ASSET
# =========================
@app.route("/request-asset", methods=["GET", "POST"])
def request_asset():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))

    if request.method == "POST":
        selected_asset_id = request.form.get("asset_id")
        selected_asset = next((a for a in assets if a["id"] == selected_asset_id and a["status"] == "Available"), None)

        if not selected_asset:
            flash("The selected asset is no longer available.")
            return redirect(url_for("request_asset"))

        asset_requests.append({
            "id": uuid.uuid4().hex[:8],
            "asset_id": selected_asset_id,
            "asset_type": selected_asset["name"],
            "quantity": request.form.get("quantity"),
            "reason": request.form.get("reason"),
            "employee": session["employee"],
            "status": "Pending",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return redirect(url_for("employee_dashboard"))

    available_assets = [a for a in assets if a["status"] == "Available"]
    return render_template("request_asset.html", assets=available_assets)

# =========================
# REPORT ISSUE
# =========================
@app.route("/report-issue", methods=["GET", "POST"])
def report_issue():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        issue_type = request.form.get("issue_type")
        description = request.form.get("description")

        issue_reported = False
        for a in assets:
            if a["id"] == asset_id and a.get("borrowed_by") == session["employee"]:
                a["status"] = "Maintenance"
                issue_reported = True

        if issue_reported:
            maintenance_requests.append({
                "asset_id": asset_id,
                "employee": session["employee"],
                "issue_type": issue_type,
                "description": description,
                "status": "Reported"
            })

        return redirect(url_for("employee_dashboard"))

    return render_template("report_issue.html", assets=assets)

# =========================
# ASSIGN ASSET
# =========================
@app.route("/assign-asset", methods=["GET", "POST"])
def assign_asset_page():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        emp_id = request.form.get("employee_id")

        for a in assets:
            if a["id"] == asset_id:
                a["borrowed_by"] = emp_id
                a["status"] = "Assigned"
                a["borrow_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                a["return_date"] = None

        return redirect(url_for("admin_dashboard"))

    return render_template("assign_asset.html", assets=assets, employees=employees)

# =========================
# VIEW ASSETS
# =========================
@app.route("/view-assets")
def view_assets():
    if not session.get("admin") and not session.get("employee"):
        return redirect(url_for("portal"))

    return render_template("view_assets.html", assets=assets)

# =========================
# ASSIGNED ASSETS
# =========================
@app.route("/assigned-assets")
def assigned_assets():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))

    emp_id = session["employee"]
    user_assets = [a for a in assets if a.get("borrowed_by") == emp_id]

    return render_template("assigned_assets.html", assets=user_assets)

@app.route("/return-asset", methods=["POST"])
def return_asset():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))

    asset_id = request.form.get("asset_id")
    emp_id = session["employee"]

    asset = next((a for a in assets if a["id"] == asset_id and a.get("borrowed_by") == emp_id), None)
    if asset:
        asset["status"] = "Available"
        asset["borrowed_by"] = None
        asset["return_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        flash("Asset returned successfully")
    else:
        flash("Asset not found or not assigned to you")

    return redirect(url_for("assigned_assets"))

# =========================
# UPDATE PROFILE
# =========================
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

        emp = next((e for e in employees if e["id"] == session["employee"]), None)
        if emp:
            emp["name"] = fullname or emp.get("name")
            emp["email"] = email
            emp["department"] = department or emp.get("department")
            emp["contact"] = contact

        return redirect(url_for("employee_dashboard"))

    return render_template("update_profile.html")

# =========================
# CHANGE PASSWORD
# =========================
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if not session.get("employee"):
        return redirect(url_for("employee_login"))

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if current_password != EMPLOYEE["password"]:
            flash("Current password is incorrect")
        elif new_password != confirm_password:
            flash("New passwords do not match")
        else:
            EMPLOYEE["password"] = new_password
            flash("Password changed successfully")
            return redirect(url_for("employee_dashboard"))

    return render_template("change_password.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()

from vercel_wsgi import make_app

handler = make_app(app)
