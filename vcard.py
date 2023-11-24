import psycopg2
from psycopg2.extensions import AsIs

import argparse
import csv
import datetime
import logging
import os
import requests
from colorama import Back, Style


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
        prog="vcard.py",
        description="""

        """,
        epilog="use these options to do specific fuctions as  written above",
    )

    parser.add_argument(
        "-v", "--verbose", help="print out detailed logs", action="store_true"
    )

    subparser = parser.add_subparsers(dest="subcommand", help="subcommand help")
    """subcommand for createdb"""
    parser_createbd = subparser.add_parser("createdb", help="create a database")
    parser_createbd.add_argument(
        "-b",
        "--db",
        help=" Specify database name give a name for a new database",
        type=str,
    )

    parser_load = subparser.add_parser(
        "loadcsv", help="load csv file and employee leaves into database"
    )
    parser_load.add_argument(
        "-l",
        "--load",
        help="Specifies the file name to be loaded (for the 'loadcsv' action)",
        type=str,
    )
    parser_load.add_argument(
        "-b",
        "--db",
        help=" Specify database name give a name for a new database",
        type=str,
    )
    parser_load.add_argument(
        "-d",
        "--address",
        help="Add new address",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )

    parser_vcard = subparser.add_parser("vcard", help="generate vcard")
    parser_vcard.add_argument("-b", "--db", help="Specify database name ", type=str)

    parser_qrcode = subparser.add_parser("qrcode", help="generate qr  code")
    parser_qrcode.add_argument("-b", "--db", help="Specify database name ", type=str)
    parser_qrcode.add_argument(
        "-s",
        "--size",
        help="Specifies a custom size between 100 and 500 (for the 'qrcode' action)",
        default=300,
    )

    parser_employee = subparser.add_parser("leavemp", help="load leaves of employees")

    parser_employee.add_argument(
        "-b", "--db", help="Specify database name ", type=str, default="hr1"
    )
    parser_employee.add_argument("-e", "--empid", help="Specify employee id ", type=str)
    parser_employee.add_argument(
        "-d", "--date", help="Specify date ", type=str, default=todays_date
    )
    parser_employee.add_argument(
        "-r",
        "--reason",
        help="Specify reason of leave ",
        type=str,
        default="Not mentioned",
    )
    parser_export = subparser.add_parser("export", help="Get the employee detail")



    args = parser.parse_args()
    return args


def employee_exist(args, user):
    connection = psycopg2.connect(f"dbname={args.db} user={user}")
    curs = connection.cursor()
    query = "SELECT EXISTS (SELECT 1 FROM employees WHERE s_no = %s)"
    curs.execute(query, (args.empid,))
    exist = curs.fetchone()[0]
    if not exist:
        logger.error(f"No employee with id {args.empid}")
        exit()
    print(exist)

    curs.close()
    connection.close()


def parse_data(args):
    filename = args.load
    datalist = []
    with open(filename, "r") as data:
        detail = csv.reader(data)
        for i in detail:
            datalist.append(i)

    return datalist


def fetch_from_db(dbname, user):
    try:
        connection = psycopg2.connect(f"dbname={dbname} user={user}")
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
        logger.info(f"Fetched all datas from employees table in {dbname} database")
        return data
    except psycopg2.Error as e:
        logger.error(f"Error {e}")


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


def create_qrcode_images(data, dimension):
    os.mkdir("qrcode")
    print(type(dimension))

    for i in data:
        with open(f"qrcode/{i[0]}.qr.png", "wb") as Q:
            qr_code = generate_qrcode(dimension, i)
            Q.write(qr_code.content)
        logger.debug("Created QRcode for %s", i[0])
    logger.info("Created QRs for all")


def create_database(dbname, user):
    connection = psycopg2.connect(database="postgres", user=user)
    curs = connection.cursor()
    curs.execute("commit")
    curs.execute("create database %s ;", (AsIs(dbname),))
    curs.close()
    connection.close()
    logger.info("Database created")


def create_tables(args, user):
    dbname = args.db
    connnection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connnection.cursor()
    query = open("tables.sql", "r")
    curs.execute(query.read())
    connnection.commit()
    curs.close()
    connnection.close()
    logger.info(f"Table employees created in {dbname} database")


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
        logger.debug(f" Inserted datas of {fname} into table employees ")

    except psycopg2.errors.DuplicateTable as e:
        logger.error(f"Table already exists: {e}")

    except psycopg2.Error as e:
        logger.error(f"Error {e}")


def load_leave_employee(args, user):
    try:
        connection = psycopg2.connect(f"dbname={args.db} user={user}")
        curs = connection.cursor()
        curs.execute(
            "SELECT designation FROM employees WHERE s_no = %s ", ((args.empid,))
        )
        designation = curs.fetchone()
        print(designation)
        if designation is not None:
            designation = designation[0]

            curs.execute(
                "SELECT total_leaves FROM designation WHERE id = %s ", ((designation,))
            )
            total_leave = curs.fetchone()
            if total_leave is not None:
                total_leave = total_leave[0]

                curs.execute(
                    "SELECT count(leave_date) FROM leave_table WHERE employee_id = %s ",
                    ((args.empid,)),
                )
                leave_count = curs.fetchone()
                if leave_count is not None:
                    leave_count = leave_count[0]

                    if leave_count < total_leave:
                        curs.execute(
                            "INSERT INTO leave_table (leave_date, employee_id,reason) VALUES (%s,%s,%s)",
                            (args.date, args.empid, args.reason),
                        )
                        logger.info("Leave added")
                    else:
                        logger.warning("Maximum leave attained")
                else:
                    logger.error("Error while fetching leave count")
            else:
                logger.error("Error while fetching total_leave")
        else:
            logger.error("Error while fetching designation")
        connection.commit()
        curs.close()
        connection.close()

    except psycopg2.Error as e:
        logger.error(f"Error {e}")


def join_tables(args,user):
    try:
        connection = psycopg2.connect(f"dbname={args.dbname} user={user}")
        curs = connection.cursor()
        curs.execute(
            f"""  """
        )
        data = curs.fetchall()
        connection.commit()
        curs.close()
        connection.close()
        logger.info(f"Joined")
        return data
    except psycopg2.Error as e:
        logger.error(f"Error {e}")


def export_employee_details(data):
        pass
    


def main():
    args = parse_args()
    user = os.getenv("USERNAME")

    configure_logger(args)

    if args.subcommand == "createdb":
        dbname = args.db

        create_database(dbname, user)

    if args.subcommand == "loadcsv":
        datas = parse_data(args)
        create_tables(args, user)

        for i in range(len(datas)):
            load_csv_into_db(args, datas[i], user)
        logger.info(f"Loaded all datas into database")

    if args.subcommand == "vcard":
        print(user)
        dbname = args.db

        data = fetch_from_db(dbname, user)
        create_vcards(data)

    if args.subcommand == "qrcode":
        dbname = args.db

        dimension = args.size

        if type(dimension) != int or int(dimension) > 500:
            logger.error("size must be an integer between 100 - 500")
        else:
            data = fetch_from_db(dbname, user)
            create_qrcode_images(data, dimension)

    if args.subcommand == "leavemp":
        load_leave_employee(args, user)
    
    
    if args.subcommand == "export":



if __name__ == "__main__":
    main()
