# update-patron-address-type
Python 3Update Alma users' primary address to include a home address type. User records are changed based on Analytics data. Enables personal delivery requesting for Primo users. 

This program is a derrivative work of the "alma-add-home-address-type-to-preferred-master" program created by Christina Hennessey at CSU Northridge. 

# CONFIGURATION:
Update the global variables section at the top of the program

urlbase = "URLBASE TO ANALYTICS REPORT"

apikey = "ALMA USER DATA READ API KEY"

reportpath = "ANALYTICS REPORT PATH"

# PYTHON ENVIRONMENT:
Requires Python version: 3.8.5 or later

# RUNNING THE PROGRAM FROM COMMAND LINE:
The program can be run from a command line/terminal on systems where Python is installed using the syntax:

python3 update-users.py

# CRONTAB AUTOMATION:
On a UNIX/LINUX system you can automate running the program by adding a line in your root crontab such as:

0 6 * * * python3 /<PROGRAM PATH>/update-users.py 2>&1 | mail -s "<EMAIL SUBJECT>" <EMAIL ADDRESS>
  
Replace <PROGRAM PATH> with your program insall path structure
Replace <EMAIL SUBJECT> with the a desired subject
Replace <EMAIL ADDRESS> with the address to receive the program output report
  



