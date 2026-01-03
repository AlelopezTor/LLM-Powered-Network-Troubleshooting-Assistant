# Network AI Agent - Demo Installation Guide


STEP 1) Download the source code by cloning the repository to your local machine:

miriamllopico@MacBook-Air-de-Miriam ~ % git clone https://github.com/AlelopezTor/LLM-Powered-Network-Troubleshooting-Assistant.git  


STEP 2) Navigate into the project's main folder:

miriamllopico@MacBook-Air-de-Miriam ~ % cd LLM-Powered-Network-Troubleshooting-Assistant 

    Here is a representation of its content:
    miriamllopico@MacBook-Air-de-Miriam LLM-Powered-Network-Troubleshooting-Assistant % ls
    Backend		Frontend	README.txt	venv


STEP 3) Install the required Python libraries (Flask, CORS, Requests) using pip3:

miriamllopico@MacBook-Air-de-Miriam LLM-Powered-Network-Troubleshooting-Assistant % pip3 install flask flask-cors requests


STEP 4) 4. Navigate into the backend directory (where the run_demo.py file is found):

This script runs on Port 5001 to avoid conflicts.
miriamllopico@MacBook-Air-de-Miriam LLM-Powered-Network-Troubleshooting-Assistant % cd Backend 


STEP 5) Run the demonstration file run_demo.py. You should see the message: Running on http://127.0.0.1:5001 (port 5001 is used to avoid conflicts).

miriamllopico@MacBook-Air-de-Miriam Backend % python3 run_demo.py 


STEP 6) Launch index.html (don't close the terminal window, the backend server must keep running).
Open a new terminal window and run this command to open the web interface:

miriamllopico@MacBook-Air-de-Miriam ~ % open LLM-Powered-Network-Troubleshooting-Assistant/Frontend/index.html 


Now, the application is ready for evaluation. Thank you for reviewing our Computer Networks project!
