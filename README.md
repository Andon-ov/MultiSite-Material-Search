# MultiSite-Material-Search
A web application for searching and aggregating building materials across multiple online stores.


git clone <repo URL>
cd <repo name>

for a linux

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

for a windows

python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver