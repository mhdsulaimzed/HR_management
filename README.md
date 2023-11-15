# HR Management

This Python script provides functions for processing employee data from a CSV file, generating vCard files for each employee, and generating QR codes containing their information.

## Usage

python vcard.py <filename>

Replace `<filename>` with the actual filename of the CSV file containing employee data.

## Functions

The script includes the following functions:

* `parse_data()`: Parses the CSV file and returns a list of employee data.
* `generate_vcard_content()`: Generates the vCard content for a single employee.
* `generate__vcards()`: Generates vCards for all employees in the provided data list.
* `generate_qr_code()`: Generates QR codes containing the email addresses of all employees in the provided data list.



This will create directories named `vcards` and `qrcode` and save the generated vCards and QR codes in these directories.
