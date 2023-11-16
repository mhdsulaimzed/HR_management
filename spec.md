# OBJECTIVE :
 Python script that converts data from a CSV file into vCard Virtual Visiting Card files. 
 
 
 
# Purpose:

The actuall purpose of this code is to read informations of employees from csv file and make a virtual visiting card files for each person,Parse command-line arguments for the vcard.py program.


# Input :

inputs a csv file containing information of employees through commandline
`python3 vcard.py <filename>`
filename (required): The name of the CSV file to process.
-`-v, --verbose` (optional): Whether to print verbose logs.
-`-a, --all` (optional): Whether to generate both QR and vCard files.
-`-s, --size` (optional): The size of the QR code to generate (default: 300).
-`-ad, --address` (optional): For adding custom address  for the vcard and default value can be set as given.

# Output : 

This will create directories named `vcards` and `qrcode` and save the generated vCards and QR codes in these directories
and the files will be having lastname of the employee in vcf and png format

# Usage :

This script should be executed through command line by passing csv-filename as an argument and returns files with 


