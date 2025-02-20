# My Django POS Project

This project is a Point of Sale (POS) system built with Django, featuring an authentication system and a user-friendly interface. The application allows users to log in, browse a product catalog, manage a shopping cart, process payments, and generate receipts.

## Features

- **User Authentication**: Secure login and registration system.
- **Product Catalog**: Browse and search for products.
- **Shopping Cart**: Add, remove, and view items in the cart.
- **Payment Processing**: Options for cash, card, and e-wallet payments.
- **Receipt Generation**: Generate and view transaction receipts.
- **Transaction Management**: Keep track of all transactions.

## Technologies Used

- Django: A high-level Python web framework.
- Tailwind CSS: A utility-first CSS framework for styling.
- shadcn/ui: A component library for building user interfaces.

## Project Structure

```
my-django-pos
├── my_django_pos
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
├── authentication
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── templates
│   │   └── authentication
│   │       ├── login.html
│   │       ├── register.html
│   │       └── base.html
├── pos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── templates
│   │   └── pos
│   │       ├── catalog.html
│   │       ├── cart.html
│   │       ├── payment.html
│   │       ├── receipt.html
│   │       └── base.html
├── static
│   ├── css
│   │   └── tailwind.css
│   ├── js
│       └── main.js
├── manage.py
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my-django-pos
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or features you would like to add.