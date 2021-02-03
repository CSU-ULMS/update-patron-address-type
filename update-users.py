# 
# Example file for parsing and processing XML from Alma Analytics
#
import urllib.request
import requests
import xmltodict
import xml.dom.minidom
import math
# import smtplib
# from email.message import EmailMessage
# import datetime

# Global Variable
urlbase = "URLBASE TO ANALYTICS REPORT"
apikey = "ALMA USER DATA READ API KEY"
reportpath = "ANALYTICS REPORT PATH"
reportlimit = "1000"
col_names = "false"
reporttolken = ""
rate = 41   # Number of records processed per a minute

def main():
  # Create url and request results
  URL = urlbase+"?path="+urllib.parse.quote(reportpath, safe='/', encoding=None, errors=None)+"&limit="+reportlimit+"&col_names="+col_names+"&apikey="+apikey
  report_string = requests.get(URL)
  
  # Process sucessful url request
  if (report_string.status_code == 200):
    # Parse the request text and assign to new dict
    report_dict = xmltodict.parse(report_string.text,dict_constructor=dict)

    # Get the request tolken and IsFinished value 
    token = report_dict['report']['QueryResult']['ResumptionToken']
    finished = report_dict['report']['QueryResult']['IsFinished']

    rows = report_dict['report']['QueryResult']['ResultXml']['rowset']['Row']

    if finished == 'false':
      print("Retrieving PrimaryID list from analytics")

    while finished == 'false':
      print('.', end ="", flush=True)
      url = urlbase + "?token=" + token + "&limit="+reportlimit+"&col_names="+col_names+"&apikey="+apikey
      r = requests.get(url)
      r.close()
    
      # Parse the request text and append to the report_dict
      next_report_dict = xmltodict.parse(r.text,dict_constructor=dict)
      finished = next_report_dict['report']['QueryResult']['IsFinished']
      next_rows = next_report_dict['report']['QueryResult']['ResultXml']['rowset']['Row']
      rows = rows + next_rows
      
    else:
      # The primary id report is finished
      # Use resulting data to update users
    
      # Setup internal count varables
      rcount = 0
      percentcomplete = 0
      recordcount = len(rows)
      eta = math.floor(recordcount / rate)
      updatedrecords = 0
      unchangedrecords = 0

      if (recordcount == 0):
        print("No records to process")
        
      
      print("\nRetrieving", str(len(rows)), "user records...")
      if eta == 0:
        print("Estimated Processing Time: less than a minute\n")
      elif eta == 1:
        print("Estimated Processing Time: ", str(eta), " minute\n")
      else:
        print("Estimated Processing Time: ", str(eta), " minutes\n")
      

      # Get the rows of the report and extract primary id from Column1
      # Process recrods according to the functions needed
      for k in rows:
        rcount = rcount + 1
        percentcomplete = round((rcount / recordcount) * 100, 1)
        primary_id = k['Column1']

        # Get user record
        ur = requests.get("https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/"+primary_id+"?user_id_type=all_unique&status=ACTIVE&apikey="+apikey)
        
        if (ur.status_code == 200):

          # Parse user record. 
          user_dict = xmltodict.parse(ur.text,dict_constructor=dict)
          primaryID = primary_id
          firstname = user_dict['user']['first_name']
          lastname = user_dict['user']['last_name']
          contact_info_base = user_dict['user']['contact_info']

          # Print user info
          print("Percent Complete: " + str(percentcomplete) + "%")
          print("Record: " + str(rcount))
          print("Primary ID: " + primaryID)
          print("Name: " + firstname + " " + lastname)

          # Get address and update home address type if needed
          # Keep track if there is nothing to update in this record so we don't write when we don't need to
          nothing_to_update = True
            
          if contact_info_base == None:
            print("There was no contact info in this one\n")
          else:
            print("Retrieving contact info...")
            addresses_base = user_dict['user']['contact_info']['addresses']
            if addresses_base == None:
              print("There was no addresses info in this one\n")
            else:
              print("Retrieving addresses info..")
              eachaddressbase = user_dict['user']['contact_info']['addresses']['address']

              # If eachaddressbase is one address, the type will be dict, if it is several, the type will be a list
              if type(eachaddressbase) == dict:
                # only update the preferred address?
                preferred_address = eachaddressbase['@preferred']

                # COPY THIS SECTION FOR MULTIPLE ADDRESSES   

                eachaddresstypesbase = eachaddressbase['address_types']

                # If this is one type of address, the type will be dict, if it is several, the type will be a list
                if type(eachaddresstypesbase['address_type']) == dict:
                  print("Only one address type in this record")

                  if eachaddresstypesbase['address_type']['@desc'] == "Home":
                    print("This record already has a home address type - no changes needed\n")
                    unchangedrecords = unchangedrecords + 1
                  else:
                    # Append the home checkbox here
                    add_home_address_type = []
                    add_home_address_type.append(eachaddresstypesbase['address_type'])
                    new_address_type_text = {'@desc': 'Home', '#text': 'home'}
                    add_home_address_type.append(new_address_type_text)
                    nothing_to_update = False
                    updatedrecords = updatedrecords + 1
                    print("Home address type added")
                else:
                    add_home_address_type = []
                    home_address = False
                    ind_address_type_base = eachaddresstypesbase['address_type']
                    # First determine if any of the address types are home
                    atcount = 0
                    for k in ind_address_type_base:
                      atcount = atcount + 1
                      type_of_address = k['@desc']
                      if (type_of_address == "Home"):
                        print("This record already has a home address type - no changes needed\n")
                        unchangedrecords = unchangedrecords + 1
                        add_home_address_type = eachaddresstypesbase
                        home_address = True
                        break
                    if home_address == False:
                      # Append the home checkbox here
                      add_home_address_type = eachaddresstypesbase['address_type']
                      new_address_type_text = {'@desc': 'Home', '#text': 'home'}
                      add_home_address_type.append(new_address_type_text)
                      nothing_to_update = False
                      updatedrecords = updatedrecords + 1
                      print("Home address type added")

                # END OF SECTION TO COPY

              else:         
                # This record has several addresses and is a list
                print("Processing more than one address...")
                home_address = False

                # Loop through addresses until we get to the preferred one and use that
                # Only update the preferred address
                # Start with -1 on count so we get the right number for getting this record later
                count_addresses = -1
                for k in eachaddressbase:
                  count_addresses = count_addresses + 1
                  preferred_address = k['@preferred']
                  # preferred address
                  if (preferred_address == "true"):
                    # COPIED FROM THE EARLIER SECTION
                    eachaddresstypesbase = k['address_types']
                    # if this is one type of address, the type will be dict, if it is several, the type will be a list
                    if type(eachaddresstypesbase['address_type']) == dict:
                      if eachaddresstypesbase['address_type']['@desc'] == "Home":
                        print("This preferred record already has a home address type - no changes needed\n")
                        unchangedrecords = unchangedrecords + 1
                      else:
                        # Append the home checkbox here
                        add_home_address_type = []
                        add_home_address_type.append(eachaddresstypesbase['address_type'])
                        new_address_type_text = {'@desc': 'Home', '#text': 'home'}
                        add_home_address_type.append(new_address_type_text)
                        nothing_to_update = False
                        updatedrecords = updatedrecords + 1
                        print("Home address type added")
                        break
                    else:
                      # More than one address type in the preferred record
                      print("Processing more than one address...")
                      add_home_address_type = []
                      home_address = False
                      ind_address_type_base = eachaddresstypesbase['address_type']
                      # First determine if any of the address types are home
                      atcount = 0
                      for q in ind_address_type_base:
                        atcount = atcount + 1
                        type_of_address = q['@desc']
                        if (type_of_address == "Home"):
                          print("This record already has a home address type in the preferred address - no changes needed\n")
                          unchangedrecords = unchangedrecords + 1
                          add_home_address_type = eachaddresstypesbase
                          home_address = True
                          break

                      if home_address == False:
                        # Append the home checkbox here
                        print("This record needs the home address type added\n")
                        add_home_address_type = eachaddresstypesbase['address_type']
                        new_address_type_text = {'@desc': 'Home', '#text': 'home'}
                        add_home_address_type.append(new_address_type_text)
                        nothing_to_update = False
                        updatedrecords = updatedrecords + 1
                        print("Home address type added")
                        break

              # Put the code here to copy the new address info into the XML
              if nothing_to_update == False:
                print("Updating address information...")
                if type(eachaddressbase) == dict:
                  user_dict['user']['contact_info']['addresses']['address']['address_types']['address_type']= add_home_address_type
                else:
                  user_dict['user']['contact_info']['addresses']['address'][count_addresses]['address_types']['address_type']= add_home_address_type

                # Remake the XML
                print("Updating user record...")
                new_user_xml = xmltodict.unparse(user_dict)
                # Comment out the next line if you don't want to save anything to the user record
                r = putXML("https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/"+primary_id+"?user_id_type=all_unique&apikey="+apikey, new_user_xml)
                print("User record updated\n")
        else:
          # There was an error with the request
          print("Error retrieving user data")

      # Display summary
      print("Processing complete")
      print("Total Records Prcessed: ", str(recordcount))
      print("Total Changed Records: ", str(updatedrecords))
      print("Total Unchanged Records: ", str(unchangedrecords))

  else:
    # There was an error with the request
    print("Error retrieving analytics data: check report path or API key")
# end of main here

# functions ###################################################################
def putXML(url, xml):
	headers = {'Content-Type': 'application/xml', 'charset':'UTF-8'}
	r = requests.put(url, data=xml.encode('utf-8'), headers=headers)
	return r

if __name__ == "__main__":
  main()