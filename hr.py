import argparse
import csv
from configparser import ConfigParser
import datetime
import logging
import models
import os
import requests
import sys
import shutil

import psycopg2
import sqlalchemy as sa


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


def set_db_config(dbname):
    config = ConfigParser()
    config.read("init.ini")
    config.set("Database", "dbname", dbname)
    with open("init.ini", "w") as configfile:
        config.write(configfile)


def parse_args():
    config = ConfigParser()
    config.read("init.ini")

    todays_date = str(datetime.date.today())

    parser = argparse.ArgumentParser(
        prog="hr.py",
        description="This a program for managing Hr operations",
        epilog="use these subcommands to do specific operations",
    )

    parser.add_argument(
        "-b",
        "--db",
        help="Database name (Default : %(default)s)",
        action="store_true",
        default=config["Database"]["dbname"],
    )
    parser.add_argument(
        "-v", "--verbose", help="print out detailed logs", action="store_true"
    )

    subparser = parser.add_subparsers(dest="subcommand", help="subcommand help")

    # database command
    parser_createdb = subparser.add_parser("createdb", help="create a database")

    # loading csv into database
    parser_load = subparser.add_parser(
        "loadcsv",
        help="insert data from file into employee table in database ",
        description="Imports list of employees into the database from specified file '-l'",
    )
    parser_load.add_argument(
        "file",
        help="File name ",
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
    parser_vcard.add_argument(
        "-d",
        "--address",
        help="Add a new address",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )

    parser_qrcode = subparser.add_parser("qrcode", help="generate qrcode")
    parser_qrcode.add_argument(
        "-s",
        "--size",
        help="Qr dimension ",
        default=300,
    )

    parser_leave_emp = subparser.add_parser(
        "leave-emp",
        help="add leaves for employees",
        description="Adds leaves taken by the employee",
    )
    parser_leave_emp.add_argument("empid", help="Employee id ", type=str)
    parser_leave_emp.add_argument(
        "-d",
        "--date",
        help="Date 'YYYY-MM-DD' (Default : %(default)s) ",
        type=str,
        default=todays_date,
    )
    parser_leave_emp.add_argument(
        "-r", "--reason", help=" Reason for leave ", type=str, default="Not mentioned"
    )
    parser_export = subparser.add_parser(
        "export",
        help="Get the employee detail as csv file",
        description="Get a detailed summary of all employees in a csv file",
    )
    parser_export.add_argument(
        "-f",
        "--file",
    )

    args = parser.parse_args()
    return args


def fetch_from_db(args):
    db_uri = f"postgresql:///{args.db}"
    session = models.get_session(db_uri)
    qs = sa.select(
        models.Employee.fname,
        models.Employee.lname,
        models.Designation.title,
        models.Employee.email,
        models.Employee.phone,
    ).where(models.Employee.title_id == models.Designation.id)
    data = session.execute(qs).fetchall()
    return data


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


def create_vcards(data, args):
    if os.path.exists("vcard"):
        shutil.rmtree("vcard")
    os.mkdir("vcard")
    for i in data:
        lname, fname, designation, email, phone = i
        vcard = generate_vcard_content(
            lname, fname, designation, email, phone, args.address
        )
        with open(f"vcards/{lname}.vcf", "w") as d:
            d.write(vcard)
        logger.debug("Created vcard for %s ", lname)
    logger.info("Created all vcards")


def create_qrcode_images(data, args):
    if type(args.size) != int or int(args.size) > 500:
        logger.error("size must be an integer between 100 - 500")

    else:
        if os.path.exists("qrcode"):
            shutil.rmtree("qrcode")
        os.mkdir("qrcode")
        logger.info("Wait this may take few minutes...")
        for i in data:
            with open(f"qrcode/{i[0]}.qr.png", "wb") as Q:
                qr_code = generate_qrcode(args.size, i)
                Q.write(qr_code.content)
            logger.debug("Created QRcode for %s", i[0])
        logger.info("Created QRs for all in qrcode folder")


def create_database(args):
    db_uri = f"postgresql:///{args.db}"
    models.create_all(db_uri)
    session = models.get_session(db_uri)
    objects = [
        models.Designation(title="Staff Engineer", max_leaves=20),
        models.Designation(title="Senior Engineer", max_leaves=20),
        models.Designation(title="Junior Engineer", max_leaves=20),
        models.Designation(title="Tech Lead", max_leaves=20),
        models.Designation(title="Project Manager", max_leaves=20),
    ]
    session.add_all(objects)
    session.commit()
    logger.info("Datebase Created ")


def parse_data(args):
    filename = args.file
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


def load_csv_into_db(args, data):
    db_uri = f"postgresql:///{args.db}"
    session = models.get_session(db_uri)
    print(data)
    fname, lname, title, email, phone = data
    s = models.Employee(
        fname=fname, lname=lname, title_id=(title), email=email, phone=phone
    )
    session.add(s)
    session.commit()
    logger.debug(f"Inserted into datase: {fname}")


def load_leave_employee(args):
    db_uri = f"postgresql:///{args.db}"
    session = models.get_session(db_uri)
    qs = sa.select(models.Leave).where(models.Leave.employee_id == args.empid)
    employee_on_leave = session.execute(qs)
    leave_input = models.Leave(
        date=args.date, employee_id=args.empid, reason=args.reason
    )

    session.add(leave_input)
    session.commit()
    logger.info(f"Leave added {args.empid}")


def join_tables(args, user):
    try:
        db_uri = f"postgresql:///{args.dbname}"
        session = models.get_session(db_uri)
        qs = sa.select(
            models.Employee.id,
            models.Employee.fname,
            models.Employee.lname,
            models.Employee.email,
            models.Employee.phone,
        ).where(
            models.Designation.id == models.Employee.title_id,
            models.Leave.employee_id == args.empid,
        )
        pp = session.execute(qs)
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
    logger.info("Exported File as employee_summary.csv ")


def main():
    args = parse_args()
    user = os.getenv("USERNAME")
    configure_logger(args)

    if args.subcommand == "createdb":
        set_db_config(args.db)
        create_database(args)

    if args.subcommand == "loadcsv":
        data = parse_data(args)
        for i in range(len(data)):
            load_csv_into_db(args, data[i])
        logger.info("Inserted all datas into database")

    if args.subcommand == "vcard":
        data = fetch_from_db(args)
        print(data)
        create_vcards(data, args)

    if args.subcommand == "qrcode":
        data = fetch_from_db(args)
        create_qrcode_images(data, args)

    if args.subcommand == "leave-emp":
        load_leave_employee(args)

    if args.subcommand == "export":
        data = join_tables(args, user)
        export_employee_details(data)


if __name__ == "__main__":
    main()
