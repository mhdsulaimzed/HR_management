# OBJECTIVE :
 Python script that converts data from a CSV file into vCard Virtual Visiting Card files. 
 
 
 
Certainly! Below is an improved version of your `spec.md` with some formatting enhancements:

```markdown
# Objective

Create a Python script that converts data from a CSV file into vCard Virtual Visiting Card files.

## Purpose

The purpose of this code is to:

1. Read employee information from a CSV file.
2. Create a database in PostgreSQL.
3. Load the employee details into the database.
4. Generate virtual visiting cards and QR code image files for each person.

## Input

The script is invoked using the following command-line format:

```bash
python3 vcard.py <action> [options]
```

Available actions:

- `createdb`: Create a PostgreSQL database.
- `load`: Load CSV file data into the database.
- `vcard`: Generate virtual visiting cards.
- `qrcode`: Generate QR codes.

Options:

- `-b, --db`: Specify the database name.
- `-l, --load`: Specify the CSV file (only with the `load` action).
- `-t, --table`: Specify the table name (only with `load`, `vcard`, and `qrcode` actions).
- `-v, --verbose` (optional): Print verbose logs.
- `-s, --size` (optional): Size of the QR code to generate (default: 300, only with the `qrcode` action).
- `-d, --address` (optional): Add custom address for the vCard; default value can be set (only with the `load` action).

## Output

### `createdb` and `load` Actions

Create a PostgreSQL database and load the CSV file into the database with a user-input table name.

### `vcard` and `qrcode` Actions

Create directories named `vcards` and `qrcode` and save the generated vCards and QR codes in these directories. Files will be named with the employee's last name in VCF and PNG formats.

## Usage

Run the script through the command line by choosing one of the actions: `createdb`, `load`, `vcard`, or `qrcode`. Perform tasks such as creating a database, loading data from the employee's CSV file into the database, and generating vCards and QR codes.




