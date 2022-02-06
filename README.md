# Penn Labs Backend Challenge

## Documentation

Fill out this section as you complete the challenge!

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipenv`
   - `pip install --user --upgrade pipenv`
4. Install packages using `pipenv install`.

## File Structure

- `app.py`: Main file. Has configuration and setup at the top. Add your [URL routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing) to this file!
- `models.py`: Model definitions for SQLAlchemy database models. Check out documentation on [declaring models](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) as well as the [SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart) for guidance
- `bootstrap.py`: Code for creating and populating your local database. You will be adding code in this file to load the provided `clubs.json` file into a database.

## Developing

0. Determine how to model the data contained within `clubs.json` and then complete `bootstrap.py`
1. Run `pipenv run python bootstrap.py` to create the database and populate it.
2. Use `pipenv run flask run` to run the project.
3. Follow the instructions [here](https://www.notion.so/pennlabs/Backend-Challenge-Fall-20-31461f3d91ad4f46adb844b1e112b100).
4. Document your work in this `README.md` file.

## Submitting

Follow the instructions on the Technical Challenge page for submission.

## Installing Additional Packages

Use any tools you think are relevant to the challenge! To install additional packages
run `pipenv install <package_name>` within the directory. Make sure to document your additions.

## Database Models Reasoning

- Club Model:
  - Fields:
    - code (String)
    - name (String)
    - description (String)
    - tags (Relationship Table)
      - When querying a club, very likely all of its tags needed
    - users (Relationship Table)
      - When 
    - each entry has a locally unique ID (Integer)
- Tag Model:
  - Fields:
    - Tag Name (String)
    - each entry has a locally unique ID (Integer)

- User Model:
  - Fields:
    - name (String)
    - username (String)
    - email (String)
      - For communication from clubs to users
    - clubs (Relationship Table)
      - When querying a user, very likely all of their clubs are needed
    - each entry has a locally unique ID (Integer)

- Tags Model & Clubs Model association table:
  - Fields:
    - Tag ID (Integer)
    - Club ID (Integer)
  - New row for every club's tags (allows repeated tags & clubs)
  - Tags repeat between clubs and clubs have multiple tags
  - Many-To-Many Relationship b/w Tags & Clubs

- Users Model & Clubs Model association table:
  - Fields:
    - User ID (Integer)
    - Club ID (Integer)
  - New row for every club's users (allows repeated users & clubs)
  - Users repeat between clubs and clubs have multiple users
  - Many-To-Many Relationship b/w Users & Clubs