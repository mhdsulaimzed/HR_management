
## HR Operations Management System
- Overview
This  Python program manages HR operations, including creating a database, loading CSV data, generating vCards, managing employee leaves, and exporting employee details.

### Dependencies
    1. Python 
    2. psycopg2
    3. pytest

### Features
-   Database Creation: Creates a PostgreSQL database to store employee information.

-   CSV Data Import: Imports CSV data into the database, populating the employees table.

-   vCard Generation: Generates vCards for all employees, containing their contact details.

-   QR Code Generation: Creates QR codes for each employee's ID,for easy access to there information.

-   Employee Leave Management: Adds leaves taken by employees to the database, maintaining leave limits.

-   Employee Details Export: Exports employee details, including leave information, to a CSV file.



Subcommands:

The script supports various subcommands for specific tasks:

`createdb`: Creates a new PostgreSQL database.

Options:
        - `-b, --db`: Give a name for database name.

`loadcsv`: Loads CSV data into the database.

Options:
   
    - `-b, --db`: Specify the database name.
    - `-l, --load`: Specify the CSV file name/path .
    - `-d, --address` (optional): Add custom address for the vCard; default value can be set.


`vcard`: Generates vCards for all employees.
    
     - `-b, --db`: Specify the database name.

`qrcode`: Generates QR codes for all employees.
    

`leavemp`: Adds leaves for an employee.

`export`: Exports employee details to a CSV file.



## How to Run?

```bash
python3 hr.py <subcommand> <options>

```


