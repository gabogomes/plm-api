# Starting the Application

Firstly, complete the steps below:

- Create Clerk Application / Contact Gabriel Gomes to get credentials values for using in the Front-End .env.local file
- Create E-mail Address for Alarms and Notifications / Contact Gabriel Gomes to use external standard e-mail address for sending notifications and alarms 

To start the application, make sure you have Docker and Docker Compose installed, as well as proper Internet connection. The command to start the multi-container application locally is:

`docker compose --profile migration up`

Note: The command above with the profile option should only be used if you are either starting the application for the first time in your local machine, or if you want to make some sort of Database Schema change, that would require a flyway migration task to be triggered. For an "ordinary" start of the application that does not fit into one of those categories, you can use

`docker compose up`

You can optionally put a `-d` option at the end, to detach the terminal from the running containers (that might not be ideal since you won't be able to see API responses and database interactions among the corresponding containers).

# Other useful commands

Sometimes, you may have problems shutting down the database and API containers. In such case, directly go to the container Terminal and kill the main process. The commands are as follows:

`docker compose exec plm_db bash`

`kill -s SIGINT 1`

`docker compose exec plm_api bash`

`kill -s SIGINT 1`

To remove all the containers you have (running or stopped), the corresponding images of the stack and the volume associated to the database, execute the `clean_stack.sh` script.