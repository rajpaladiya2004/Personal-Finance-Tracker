# Personal Finance Tracker

A web application for tracking personal finances built with Django.

## Project Overview
This is a university portfolio project for the course "Project Java and Web Development."

## Features
- Track income and expenses
- View financial summaries
- Simple and clean user interface

## Setup Instructions

1. Create virtual environment:
   ```
   python -m venv venv
   ```

2. Activate virtual environment:
   ```
   source venv/Scripts/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run development server:
   ```
   python manage.py runserver
   ```

## Technology Stack
- Python 3.11
- Django 4.2.7
- SQLite Database
- Bootstrap (for UI)

## Project Structure
- `finance_tracker/` - Main project configuration
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and images
- `media/` - User uploaded files
