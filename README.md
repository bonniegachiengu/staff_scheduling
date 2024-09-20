# Staff Scheduling System

## Overview
This Staff Scheduling System is a Django-based web application designed to manage employee schedules for a restaurant or similar business. It allows for efficient scheduling of employees across different roles and shift blocks, taking into account employee preferences and availability.

## Features
- Employee management with role assignments and ratings
- Shift block definition and management
- Automated scheduling using the Hungarian algorithm
- Employee preference setting for shifts and availability
- Admin interface for managing all aspects of the system

## Technologies Used
- Python 3.x
- Django 5.1.1
- PostgreSQL
- HTML/CSS
- JavaScript (if applicable)

## Setup

### Prerequisites
- Python 3.x
- PostgreSQL
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```
   git clone [repository URL]
   cd staff_scheduling
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   - Create a database named `sched_db`
   - Update the database configuration in `staff_scheduling/settings.py` if necessary

5. Apply migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage
- Access the admin interface at `http://localhost:8000/admin/`
- Use the employee preferences page to set availability and preferred shifts
- Access the scheduling interface to generate and view schedules

## Contributing
[Include guidelines for contributing to the project, if applicable]

## License
[Specify the license under which this project is released]

## Contact
[Your Name or Team Name]
[Contact Information or Project Repository URL]