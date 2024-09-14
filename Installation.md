# KU Polls Installation Guide

### 1. Clone the Repository
Begin by cloning the KU Polls repository to your local machine.
``` 
git clone https://github.com/NewOsakA/ku-polls.git
```

### 2. Navigate to the KU Polls Directory
Move into the project's root directory.
``` 
cd ku-polls
```

### 3. Create and activate a Virtual Environment
Set up a virtual environment for the project.
``` 
python -m venv venv
```

* For Linux and macOS:
```
source venv/bin/activate
```
* For Windows:
```
.\venv\Scripts\activate
```

### 4. Install Required Packages
Install the necessary Python packages.
```
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Copy the sample environment file and rename it to .env.
* For Linux and macOS
```
cp sample.env .env
```
* For Windows:
```
copy sample.env .env
```

### 6. Edit the ```.env``` File 
Open the ```.env``` file in a text editor and modify the variables to suit your local setup.

### 7. Apply Database Migrations
Run the migrations to set up the database schema.
```
python manage.py migrate
```

### 8. Run Tests to Verify the Installation
Run the test suite to ensure everything is set up correctly.
```
python manage.py test polls
```

### 9. Load KU Polls Data into the Database
Load the initial data fixtures into the database.
1. For poll questions and choices:
```
python manage.py loaddata data/polls-v4.json
```
2. For user data:
```
python manage.py loaddata data/users.json
```
3. For vote data:
```
python manage.py loaddata data/votes-v4.json
```

Alternatively, load all data files at once:
```
python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
```
> **NOTE:** After completing these steps, refer to [README.md](README.md) for instructions on running the application.