import argparse
import csv
import datetime
import logging
import os
import requests
import sys

import psycopg2
from psycopg2.extensions import AsIs

logger = None


def configure_logger(args):
    global logger
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    formatter = "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    handler.setLevel(level)
    fhandler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(formatter))
    fhandler.setFormatter(logging.Formatter(formatter))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)


def parse_args():
    todays_date = str(datetime.date.today())

    parser = argparse.ArgumentParser(
        description="This a program for managing Hr operations",
        epilog="use these subcommands to do specific operations",
    )

    parser.add_argument(
        "-v", "--verbose", help="print out detailed logs", action="store_true")
    parser.add_argument("--db", help="Name of database to use (Default : %(default)s)", default="hrms", type=str, action="store")

    subparser = parser.add_subparsers(dest="subcommand", help="subcommand help")

    # database command
    parser_createdb = subparser.add_parser("createdb", help="create a database")

    # loading csv into database
    parser_load = subparser.add_parser(
        "loadcsv", help="Imports employees from csv file",description="Imports employees from CSV file"
    )
    parser_load.add_argument(
        "-f",
        "--file",
        help="Specifies the file name to be loaded ",
        type=str,
    )

    parser_load.add_argument(
        "-d",
        "--address",
        help="Add a new address",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )
    # commad for creating vcards
    parser_vcard = subparser.add_parser("vcard", help="generate vcards")

    parser_qrcode = subparser.add_parser("qrcode", help="generate qrcode")
    parser_qrcode.add_argument(
        "-s",
        "--size",
        help="Specifies a custom size between 100 and 500 (for the 'qrcode' command)",
        default=300,
    )

    parser_leave_emp = subparser.add_parser("leavemp", help="add leaves for employees",description="Adds leaves taken by the employee")

    parser_leave_emp.add_argument(
        "-e", "--empid", help="Specify employee id ", type=str
    )
    parser_leave_emp.add_argument(
        "-d", "--date", help="Specify date ", type=str, default=todays_date
    )
    parser_leave_emp.add_argument(
        "-r",
        "--reason",
        help="Specify reason of leave ",
        type=str,
        default="Not mentioned",
    )
    parser_export = subparser.add_parser(
        "export", help="Get the employee detail as csv file",description="Get a detailed summary of all employees in a csv file"
    )
    args = parser.parse_args()
    return args


def parse_data(args):
    filename = args.load
    datalist = []
    try:
        with open(filename, "r") as data:
            detail = csv.reader(data)
            for i in detail:
                datalist.append(i)

        return datalist
    except FileNotFoundError as e:
        logger.error("Error %s", (e,))
        sys.exit(-1)


def fetch_from_db(args, user):
    try:
        connection = psycopg2.connect(f"dbname={args.db} user={user}")
        curs = connection.cursor()
        curs.execute(
            f"""SELECT first_name,last_name,designation,email,phone,company_address
                         FROM
                         employees """
        )
        data = [list(row) for row in curs.fetchall()]
        connection.commit()
        curs.close()
        connection.close()
        logger.info(f"Fetched all data from employees table in {args.db} database")
        return data
    except psycopg2.OperationalError as e:
        logger.error(e)
        sys.exit(-1)


def generate_vcard_content(lname, fname, designation, email, phone, address):
    return f"""BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;{address}
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""


def generate_qrcode(dimension, i):
    qr_code = requests.get(
        f"https://chart.googleapis.com/chart?cht=qr&chs={dimension}x{dimension}&chl={i}"
    )
    return qr_code


def create_vcards(data):
    os.mkdir("vcards")
    for i in data:
        lname, fname, designation, email, phone, address = i
        vcard = generate_vcard_content(lname, fname, designation, email, phone, address)
        with open(f"vcards/{lname}.vcf", "w") as d:
            d.write(vcard)
        logger.debug("Created vcard for %s ", lname)
    logger.info("Created all vcards")


def create_qrcode_images(data, args):
    if type(args.size) != int or int(args.size) > 500:
        logger.error("size must be an integer between 100 - 500")
    else:
        if not os.path.exists("qrcode"):
            os.mkdir("qrcode")
            for i in data:
                with open(f"qrcode/{i[0]}.qr.png", "wb") as Q:
                    qr_code = generate_qrcode(args.size, i)
                    Q.write(qr_code.content)
                logger.debug("Created QRcode for %s", i[0])
            logger.info("Created QRs for all")


def create_database(args, user):
    try:
        connection = psycopg2.connect(database="postgres", user=user)
        curs = connection.cursor()
        curs.execute("commit")
        curs.execute("create database %s ;", (AsIs(args.db),))
        curs.close()
        connection.close()
        logger.info("Database created")
    except psycopg2.errors.DuplicateDatabase as e:
        logger.error("Error %s", e)


def create_tables(args, user):
    try:
        dbname = args.db
        connnection = psycopg2.connect(f"dbname={dbname} user={user}")
        curs = connnection.cursor()
        query = open("queries.sql", "r")
        curs.execute(query.read())
        connnection.commit()
        curs.close()
        connnection.close()
        logger.info(f"Table employees created in {dbname} database")

    except psycopg2.errors.DuplicateTable as e:
        logger.error("Table already exists: %s", e)
        sys.exit(-1)


def load_csv_into_db(args, data, user):
    try:
        connection = psycopg2.connect(f"dbname={args.db} user={user}")
        curs = connection.cursor()
        fname, lname, designation, email, phone = data

        curs.execute(
            f"""INSERT
                         INTO
                         employees(first_name, last_name, designation, email, phone, company_address)
                          VALUES(%s,%s,%s,%s,%s,%s)""",
            (fname, lname, designation, email, phone, args.address),
        )

        connection.commit()
        curs.close()
        connection.close()
        logger.debug(" Inserted datas of %s into table employees ", fname)

    except psycopg2.OperationalError as e:
        logger.error("Error %s", e)
    except psycopg2.errors.ForeignKeyViolation as e:
        logger.warning("Foreign key violation: %s")

    except psycopg2.Error as e:
        logger.error(f"Error {e}")


def load_leave_employee(args, user):
    try:
        with psycopg2.connect(f"dbname={args.db} user={user}") as connection:
            with connection.cursor() as curs:
                try:
                    curs.execute(
                        "SELECT designation FROM employees WHERE s_no = %s ",
                        (args.empid,),
                    )
                    designation = curs.fetchone()[0]
                except (TypeError, IndexError) as e:
                    logger.error(f"Error while fetching designation: %s", (e,))
                    raise  # for exiting the fun'

                try:
                    curs.execute(
                        "SELECT total_leaves FROM designation WHERE id = %s ",
                        (designation,),
                    )
                    total_leave = curs.fetchone()[0]
                except (TypeError, IndexError) as e:
                    logger.error(f"Error while fetching total_leave: %s", (e,))
                    raise

                try:
                    curs.execute(
                        "SELECT count(leave_date) FROM employee_leave WHERE employee_id = %s ",
                        (args.empid,),
                    )
                    leave_count = curs.fetchone()[0]
                except (TypeError, IndexError) as e:
                    logger.error(f"Error while fetching leave count: %s", (e,))
                    raise

                try:
                    if leave_count < total_leave:
                        curs.execute(
                            "INSERT INTO employee_leave(leave_date, employee_id,reason) VALUES (%s,%s,%s)",
                            (args.date, args.empid, args.reason),
                        )
                        logger.info("Leave added")
                    else:
                        logger.warning("Maximum leave attained")
                except psycopg2.Error as e:
                    logger.error("Error while inserting leave data: %s", e)

    except psycopg2.Error as e:
        logger.error("Error: %s", e)


def join_tables(args, user):
    try:
        connection = psycopg2.connect(f"dbname={args.db} user={user}")
        curs = connection.cursor()
        curs.execute(
            """SELECT
  e.s_no,
  e.first_name,
  e.last_name,
  d.title,
  d.total_leaves,
  e.email,
  e.phone,
  e.company_address,
  COUNT(DISTINCT l.leave_date) AS leave_taken,
  d.total_leaves - COUNT(DISTINCT l.leave_date) AS leave_remaining
FROM employees e
JOIN designation d ON e.designation = d.id
LEFT JOIN employee_leave l ON e.s_no = l.employee_id
GROUP BY e.s_no, e.first_name, e.last_name, d.title, d.total_leaves, e.email, e.phone, e.company_address;
"""
        )
        data = curs.fetchall()
        connection.commit()
        curs.close()
        connection.close()
        logger.info(f"Joined tables and data fetched")
        return data
    except psycopg2.Error as e:
        logger.error("Error %s", e)


def export_employee_details(data):
    with open("employees_summary.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Employee ID",
                "First Name",
                "Last Name",
                "Designation",
                "Total Leaves",
                "Email",
                "Phone",
                "Company Address",
                "Leaves Taken",
                "Leaves Remaining",
            ]
        )

        for row in data:
            writer.writerow(row)
            logger.debug("Writed row on csv file")
    logger.info("Exported ")


def main():
    args = parse_args()
    user = os.getenv("USERNAME")
    configure_logger(args)

    if args.subcommand == "createdb":
        create_database(args, user)

    if args.subcommand == "loadcsv":
        data = parse_data(args)
        create_tables(args, user)
        for i in range(len(data)):
            load_csv_into_db(args, data[i], user)

    if args.subcommand == "vcard":
        data = fetch_from_db(args, user)
        create_vcards(data)

    if args.subcommand == "qrcode":
        data = fetch_from_db(args, user)
        create_qrcode_images(data, args)

    if args.subcommand == "leavemp":
        load_leave_employee(args, user)

    if args.subcommand == "export":
        data = join_tables(args, user)
        export_employee_details(data)


if __name__ == "__main__":
    main()
