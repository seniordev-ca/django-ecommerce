# Django Project Setup

This repository contains a Django project built with Django Rest Framework (DRF). Follow the instructions below to set up the project locally.

## Prerequisites

- Python (version 3.9.X)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/seniordev-ca/django-ecommerce.git
   ```
2. Navigate to the project directory:

   ```bash
   cd django-ecommerce
   ```
3. Create a virtual environment:
   ```bash
   python -m venv env
   ```
4. Activate the virtual environment:
- On Windows:
   ```bash
  env\Scripts\activate
   ```
- On macOS and Linux:
   ```bash
   source env/bin/activate
   ```
5. Install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Set up the database:
   ```bash
   python manage.py migrate
   ```
   
## Usage
1. Run the development server:
   ```bash
   python manage.py runserver
   ```
2. Create superuser if you want to create new products and see it on [front-end](https://github.com/seniordev-ca/next-ecommerce)
   ```bash
   python manage.py createsuperuser
   ```
4. Open your web browser and visit http://localhost:8000 to access the application.
