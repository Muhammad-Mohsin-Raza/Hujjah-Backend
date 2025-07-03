# 🧠 Hujjah Backend

This is the backend for the **Hujjah** platform — a Django-based API for legal case and client management.

## 🚀 Quick Setup (All-in-One)

```bash
# Clone the repository
git clone https://github.com/your-username/hujjah.git
cd hujjah

# Create and activate a virtual environment
python3 -m venv py-venv
source py-venv/bin/activate   # Windows: py-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp example.env .env
# Edit the .env file with your database credentials and other settings

# Change to backend directory
cd hujjah_backend

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Run the development server
python manage.py runserver
```

## 🔐 Environment Variables

The application uses environment variables for configuration. Copy the `example.env` file to `.env` and update the values:

```
# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Django Secret Key
SECRET_KEY=your-secret-key-here

# Debug Mode
DEBUG=True
```

🤝 Developer
Muhammad Mohsin Raza
