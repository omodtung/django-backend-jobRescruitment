python3 -m venv env
source env/bin/activate  # Trên Linux/macOS
pip install -r requirements.txt

# Cài đặt PostgreSQL
# Tạo sẵn db trên PostgreSQL
# Sửa đổi password db của ứng dụng

cd ./backend/

# Chạy lần lượt các lệnh sau
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
