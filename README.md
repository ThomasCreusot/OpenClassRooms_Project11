# OpenClassRooms_Project11
Improve a Python web application through testing and debugging

## Project presentation
The present project is the eleventh one of the training course *Python Application Developer*, offered by OpenClassrooms and aims to *Improve a Python web application through testing and debugging*.

The main goal is to develop **tests (unit, integration and performance)** for a Flask application wich allows to manage sport competitions.

The gudlift-registration application allows clubs secretaries to book competitions places. Each club can exchange points to register athletes within a competition. Competitions have a limited number of place and each club can register a maximum of 12 athletes per competition.

The project was developped in 2 phases.
-The OpenClassrooms student received phase 1 features which included some bugs which has been solved. 
-The OpenClassrooms student coded the phase 2 feature and the tests for all features.
This, with respect of the Development Guide given par OpenClassrooms for this project.



# gudlift-registration

1. Why

    This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

2. Getting Started

    This project uses the following technologies:

    * Python v3.x+

    * [Flask](https://flask.palletsprojects.com/en/1.1.x/)

        Whereas Django does a lot of things for us out of the box, Flask allows us to add only what we need. 
     
    * [Virtual environment](https://virtualenv.pypa.io/en/stable/installation.html)

        This ensures you'll be able to install the correct packages without interfering with Python on your machine.

        Before you begin, please ensure you have this installed globally. 

3. Installation

    - After cloning, change into the directory and type <code>virtualenv .</code>. This will then set up a virtual python environment within that directory.
        Otherwise, create a virtual environment as follows : write the following command in the console
        >'python -m venv env'

    - Next, type <code>source bin/activate</code>. You should see that your command prompt has changed to the name of the folder. This means that you can install packages in here without affecting affecting files outside. To deactivate, type <code>deactivate</code>

    - Rather than hunting around for the packages you need, you can install in one step. Type <code>pip install -r requirements.txt</code>. This will install all the packages listed in the respective file. If you install a package, make sure others know by updating the requirements.txt file. An easy way to do this is <code>pip freeze > requirements.txt</code>

    - Flask requires that you set an environmental variable to the python file. However you do that, you'll want to set the file to be <code>server.py</code>. Check [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application) for more details
        e.g : 
        >set FLASK_APP=server.py

    - You should now be ready to test the application. In the directory, type either <code>flask run</code> or <code>python -m flask run</code>. The app should respond with an address you should be able to go to using your browser.

4. Current Setup

    The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:
     
    * competitions.json - list of competitions
    * clubs.json - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.

5. Testing

    Type <code>pytest</code> to launch unit et integration tests. You can add <code>-s</code> or <code>-v</code> options for more details.
    For performance tests, you need to open another terminal on tests/performance_tests and type <code>locust</code> before visiting http://localhost:8089/ on an internet browser.

    We like to show how well we're testing, so there's a module called 
    [coverage](https://coverage.readthedocs.io/en/coverage-5.1/) which has been added to the project.
