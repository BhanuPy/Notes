# Notes
This project is to develop a RESTful API for a simple note-taking application. The API should allow users to perform basic CRUD operations (Create, Read, Update, Delete) on notes.

# Project Name

NeoFi Python Backend: Notes

## About the Project

Focus on the backend functionality; the UI is not required. You can use tools like Postman or cURL to test the APIs. (bonus points if testing is automated)
Use appropriate authentication and authorization mechanisms for user registration and login.
Updating an existing shared note needs some thought input. 
Follow Django best practices, such as using Django's built-in user authentication system and using serializers for API data validation.
Implement necessary error handling and provide appropriate responses for different scenarios.


## Setup Instructions

Follow these instructions to set up the project on your local machine.

### Prerequisites

- Python (version 3.x)
- pip (package manager)

### 1. Clone the Repository

git clone https://github.com/BhanuPy/Notes.git
cd Notes

### 1. Clone the Repository

# Install virtualenv if you haven't already
pip install virtualenv

### 2. Create a virtual environment
virtualenv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Run Migration
python manage.py migrate

### 5. Start the Development Server 
python manage.py runserver

goto the browser:
type:
localhost:8000/signup    #inorder to start the project