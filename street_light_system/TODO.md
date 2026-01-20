Street Light Complaint System

1. Install requirements:
   pip install -r requirements.txt

2. Run migrations:
   python manage.py migrate

3. Create admin:
   python manage.py createsuperuser
   Username: kseb_admin
   Password: kseb@123

4. Run server:
   python manage.py runserver

Admin Login: http://127.0.0.1:8000/kseb-login/
User Flow: Register → Report Complaint → My Complaints
