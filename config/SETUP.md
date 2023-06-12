### Installation

1. Clone the repository to your local machine:

   ```
   $ git clone https://github.com/yash22arora/ticc_portal_client
   ```

2. Navigate to the project directory and change into the backend directory:

   ```
   $ cd ticc_portal_client
   $ cd config
   ```

3. Create and activate a virtual environment (optional but recommended):

   ```
   $ pipenv shell
   ```

4. Install the required dependencies:

   ```
   $ pip install -r requirements.txt
   ```

5. Set up the database:

   ```
   $ python manage.py makemigrations
   $ python manage.py migrate
   ```

6. (Optional) Create a superuser to access the admin interface:

   ```
   $ python manage.py createsuperuser
   ```

7. Start the development server:

   ```
   $ python manage.py runserver
   ```

8. Open your web browser and visit [http://localhost:8000/](http://localhost:8000/) to see the project in action.

### Configuration

- Modify the project settings in `settings.py` as needed, such as database settings, static files, etc.

### Testing

- Run the tests to make sure everything is working correctly:

   ```
   $ python manage.py test
   ```

### Management Commands 

- To populate Database with test users present in test_users.csv, run the following command:

   ```
   $ python manage.py populate_users
   ```

- To populate Data with test slots 

    ```
    $ python manage.py create_slots
    ```

### Deployment

- Refer to the official Django documentation for instructions on deploying Django projects to production environments.
