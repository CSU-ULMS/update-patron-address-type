# update-patron-address-type
Update Alma users' primary address to include a home address type. User records are changed based on Analytics data. Enables personal delivery requesting for Primo users. 

This program is a derrivative work of the "alma-add-home-address-type-to-preferred-master" program created by Christina Hennessey at CSU Northridge. 

CSU patron data is updated automatically by a PeopleSoft patron update process. During the automatic update patron address information is overwritten regardless of any changes in the address information. As a result, any home address type that was manually added to patron records in Alma will be overwritten the next time the patron load process sends updated users. This program updates the changed users and adds home addresses type back to their primary address.

# alma analytics configuration
The program uses analytics data to determine what user records need to be updated with the home address type. Before configuring and running the program you must create the following Alma Analytics report:
  
  1. Create a new User analysis in Design Analytics (see analytics_report screenshot)
  2. Add Primary Identifier to the selected columns
  3. Add filters for CREATION DATE and MODIFICATION DATE, each with an SQL Expression value of: TIMESTAMPADD(SQL_TSI_DAY,-1,CURRENT_DATE)
  4. Group CREATION DATE and MODIFICATION DATE with an OR operator
  5. Outside the group, add a filter for MODIFIED BY with the value: SIS
  6. Test the results and save the report as Patron Load Changes
  6. From the listing of reports, locate the newly created report properties and note the file path and name of the report (used for program configuration) 

# python environment
Requires Python version: 3.8.5 or later

# configuration
Before configuring the program, ensure you have created an Alma User Read Access API Key and the Analytics Patron Load Changes report. 

Update the global variables section at the top of the program:

urlbase = "URLBASE TO ANALYTICS REPORT"
  
  ex: "https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports"

reportpath = "ANALYTICS REPORT PATH (location + file name)" 
  
  ex: "/shared/California State University - Sacramento/Reports/Users/Patron Load Changes"

apikey = "ALMA USER DATA READ API KEY"

# running the program from a command line
The program can be run from a command line/terminal on systems where Python is installed using the syntax:

python3 update-users.py

# crontab automation
On a UNIX/LINUX system you can automate running the program by adding a line in your root crontab such as:

0 6 * * * python3 /PROGRAM_PATH/update-users.py 2>&1 | mail -s "EMAIL_SUBJECT" EMAIL_ADDRESS
  
- Replace PROGRAM_PATH with your program install path
  
- Replace EMAIL_SUBJECT with a desired subject

- Replace EMAIL_ADDRESS with the address to receive the program output report





