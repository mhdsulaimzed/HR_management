# OBJECTIVE :
 Python script that converts data from a CSV file into vCard Virtual Visiting Card files. 
 Create a Python script that converts data from a CSV file into vCard Virtual Visiting Card files and fetch data from databases and make an employee sumary

## Purpose

The purpose of this code is to:

1. Read employee information from a CSV file.
2. Create a database in PostgreSQL.
3. Load the employee details into the database.
4. Generate virtual visiting cards and QR code image files for each person
5. Get all details of about employee of particular id 
6. Add leaves for employees and the default date must be today's

## Input

The script is invoked using the following command-line format:

```bash
python3 hr.py <subcommand> [options]
```
### Commmon option

- `-v, --verbose` (optional): Print verbose logs.

### Subcommands:

- `createdb`: Create a PostgreSQL database.
    Options:
        - `-b, --db`: Give a name for database name.

- `loadcsv`: Load CSV file data into the database.
    Options:
   
    - `-b, --db`: Specify the database name.
    - `-l, --load`: Specify the CSV file name/path .
    - `-d, --address` (optional): Add custom address for the vCard; default value can be set.


- `vcard`: Generate virtual visiting cards.
    Options:

    - `-b, --db`: Specify the database name.

- `qrcode`: Generate QR codes.
    Options:

    - `-b, --db`: Specify the database name.
    - `-s, --size` (optional): Size of the QR code to generate (default: 300, only with the `qrcode` action).

- `leavemp` : 
    `-b, --db`: Specify the database name.
    `-e, --empid`: Specify the employee ID.
    `-d, --date`: Specify the leave date (default: today's date).
    `-r, --reason`: Specify the reason for leave (default: "Not mentioned").


- `export`: Get deatailed summary of employees in csv file,
    Options:

    - `-b, --db`: Specify the database name.
    


## Output

### `createdb` and `load` Subcommands

Create a PostgreSQL database and load the CSV file into the database with a user-input table name.

### `vcard` and `qrcode` Subcommands

Create directories named `vcards` and `qrcode` and save the generated vCards and QR codes in these directories. Files will be named with the employee's last name in VCF and PNG formats.


### employee

Retrives employee details and leave remaining of perticular employee with the passed employee id

## Usage

Run the script through the command line by choosing one of the subcommand: `createdb`, `load`, `vcard`,`export`,`qrcode` & `leavemp`. Perform tasks such as creating a database, loading data from the employee's CSV file into the database, and generating vCards and QR codes.




