# 🧾 Django POS System

## 📌 Project Overview

The **Django POS System** is a complete web-based **Point of Sale (POS)** application developed using **Python and Django**.
This system is designed to help shops and retail businesses manage their **products, sales transactions, staff, and reports** efficiently.

The system provides **role-based dashboards** for **SuperAdmin, ShopAdmin, and Cashiers**, allowing each user type to perform specific operations based on their permissions.

It is designed to streamline shop operations by enabling fast billing, product management, and real-time sales tracking.

---

## 🎯 Main Objectives

* Provide a **fast and efficient billing system**
* Manage shop products and inventory
* Generate **sales reports with date filters**
* Support **barcode scanning for quick checkout**
* Provide **role-based access control**
* Allow shop owners to monitor business performance

---

## 👥 User Roles

### 🔹 SuperAdmin

The **SuperAdmin** manages the overall system.

Features:

* Manage all shops
* Manage users and permissions
* Monitor system activity
* View overall reports

---

### 🔹 ShopAdmin

The **ShopAdmin** manages the operations of a specific shop.

Features:

* Add, update, and delete products
* Manage shop inventory
* View sales reports
* Manage shop staff (cashiers)

---

### 🔹 Cashier

The **Cashier** handles customer transactions.

Features:

* Process sales and billing
* Scan product barcodes
* Generate receipts
* View daily sales

---

## 🚀 Key Features

* 🔐 User Authentication System
* 👤 Role-Based Access Control
* 🛒 Sales & Billing System
* 📦 Product & Inventory Management
* 📷 Barcode Scanner Integration
* 📊 Sales Reports with Date Filtering
* 📁 Excel Report Export
* 📧 Email Notifications
* ⚡ Fast and responsive dashboard UI

---

## 🛠️ Technology Stack

### Backend

* Python
* Django

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript

### Database

* PostgreSQL

### Additional Services

* Firebase (Email verification / authentication)
* SMTP Email System
* Excel export for reports

---

## 📂 Project Structure

```
djangoPos/
│
├── README.md
├── requirements.txt
├── .gitignore
├── manage.py
│
|
├── cashierDashboard/
│   ├── __init__.py
│   ├── templates
│   ├── static
│   ├── migrations
│   ├── admin.py
│   ├── app.py
│   └── model.py
│   ├── test.py
│   ├── url.py
│   └── views.py
|
├── media/
|
├── pos_system/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── shopAdmin/
│   ├── __init__.py
|   |── templates
│   ├── static
│   ├── migrations
│   ├── admin.py
│   ├── app.py
│   └── model.py
│   └── context_processors.py
│   ├── test.py
│   ├── url.py
│   └── views.py
|
├── superAdmin/
│   ├── __init__.py
|   |── templates
│   ├── static
│   ├── migrations
│   ├── admin.py
│   ├── app.py
│   └── model.py
│   ├── test.py
│   ├── url.py
│   └── views.py
|
├── userAuth/
│   ├── __init__.py
|   |── templates
│   ├── static
│   ├── migrations
│   ├── admin.py
│   ├── app.py
│   └── model.py
│   ├── test.py
│   ├── url.py
│   └── views.py







## ⚙️ Installation Guide

Clone the repository:

```
git clone https://github.com/SyedMuhammadJunaid10/pos-system.git
```

Navigate to project directory:

```
cd pos-system
```

Create virtual environment:

```
python -m venv .venv
```

Activate environment:

```
.venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Apply migrations:

```
python manage.py migrate
```

Run the development server:

```
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000
```

---



## 👨‍💻 Author

**Syed Muhammad Junaid**

Full Stack Developer
Skills: Django, Python, JavaScript, React, PostgreSQL, Data Science

---

## 📜 License

This project is created for **learning and portfolio purposes**.
