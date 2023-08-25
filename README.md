# Project brief:
Creating an event management system under the brand POMI, to allow hosts to create and manipulate events, and to allow prospective customers to purchase and join these events; as well as much more!

# Getting the system running:
To setup the system for the first time, please follow the SystemInstallation.pdf in the root directory, or the System Installation/Documentation/Manual in the final report.

After system installation is successful:

We will need **3 terminals**.

**[Terminal 1]** points to the root/**database** directory:
For *Linux* users (restores the database to the default empty state):  

    sh restore_database.sh
  
For *Windows* users (starts the Postgresql service, and restores the database to the default empty state):  

    sudo service postgresql start
    dropdb COMP3900 && createdb COMP3900
    psql COMP3900 -f load_database.sql

**[Terminal 2]** points to the root/**backend** directory:  
(Starts the server)  

    python3 -m src.server

**[Terminal 3]** points to root/**frontend** directory:  
(Starts the React app)  

    npm start
