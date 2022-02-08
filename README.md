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

## What did I do for this challenge (my deliverables):
- Completed the base challenge
  - Custom Routes: 
    - Get all users GET request to (/api/users)
    - Add new user POST request to (/api/users)
- Did 2 bonus challenges:
  - Webscraping
  - Comments
- Documentation:
  - Throughout the code as comments
  - Formatted API Docs with example inputs (PDF also in the github but link is interactive/better): https://documenter.getpostman.com/view/12119059/UVeJKjkG
  - Reasoning for some functionality and model implementation below in this README

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
    - comments relationship to Comment table

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
    - comments relationship to Comment table

- Comment Model:
  - Fields:
    - user_id(integer)
    - club_id(integer)
    - text(string)
    - each entry has a locally unique ID (integer)
  - A comment is related to exactly one club and one user, but a user and a club can both have multiple comments

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

## Additional Packages Installed
requests - used for webscraping, sends HTTP request to website
BeautifulSoup - used to parse/navigate html data

## Webscraping Notes/Reasoning
- Elements all in unique `"box"` class
- Each `"box"` contains elements with class names `club-name`, `tag`, 
and `"em"` tag with description
- Since only one website, synchronous is alright, otherwise maybe async since
  it would be faster to read multiple sites at once (unless overhead of async)
  outweighs the time it would take for sync reading
- Converted all club data to format that could easily reuse add_club function

## General Routes & Functionality Reasoning
- As per my understanding of RESTful APIs & just good programming practices:
  - Whenever a resource was added, altered, or deleted, I returned that resource in JSON format
  - For the same URL (within clubs, comments, and users):
    - POST requests always were used for adding new information/resource
    - PUT requests always were used for modifying existing information/resource
    - GET requests always were used for reading existing information/resource without alteration
  - For comments, I also implemented DELETE:
    - takes a comment_id (all that's necessary) and deletes it from the Comments table
    - cutting off relationships is handled by SQLAlchemy
  - Returned error codes of specific types based upon the error I caught
    - Ex: if resource not found, then error 404, if success, then 200, etc.
    - Did some error-checking (ex: if information is missing or resource not found), but not all implemented (due to time constraints)
      - Meant to show how I might implement error-checking where applicable
  - In all my designing, I took time to think about what the front-end would have access to, what they can easily send and receive, and how I can make the least possible number of queries without making over-complicated code
- Some Route-Specific Reasoning:
  - For the modify_club route:
    - The assumption in the modify club function is that the front end will pull all data, allow the user to modify what is necessary, then send all fields back. Empty fields should be addresed in the front end, but just in case, if None is given back, this system keeps the old values.
  - For the get_all_users route:
    - This route I made return all data about a user, including connections to some clubs
    - I imagined something like this route could be used for migrating user profiles between different versions of an app
  - For the add_favorites route:
    - Here I realized from the front end this function could simply be tied to a favorites button
    - Instead of separate add and remove favorite functions, I made this function simply toggle between having the club marked as a favorite and removing it if it already exists
    - This is just something I feel I would like if I were making the front end of this app
  - General data stuff I did:
    - If a sufficient amount of data wasn't provided, I returned the proper error codes, but wherever possible, I tried to see how old data could be reused to sensibly fill gaps
    - I made sure a resource existed (for the most part) before attempting to act on it