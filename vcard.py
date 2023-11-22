import psycopg2
from psycopg2.extensions import AsIs

import argparse
import csv
import logging
import os
import requests
from colorama import Back,Style



logger = None


def configure_logger(log_level):
    global logger
    formatter = "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    handler.setLevel(log_level)
    fhandler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(formatter))
    fhandler.setFormatter(logging.Formatter(formatter))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="vcard.py",
        description="""
        
        """,
        epilog="use these options to do specific fuctions as  written above",
    )
    
    parser.add_argument("-v", "--verbose", help="print out detailed logs", action="store_true")

    
    subparser = parser.add_subparsers(dest='subcommand',help='subcommand help')
    """subcommand for createdb"""
    parser_createbd = subparser.add_parser("createdb", help="create a database")
    parser_createbd.add_argument("-b", "--db", help=" Specify database name give a name for a new database", type=str)
    
    
    
    parser_load = subparser.add_parser("loadcsv", help="load csv file and employee leaves into database") 
    parser_load.add_argument("-l", "--load", help="Specifies the file name to be loaded (for the 'loadcsv' action)", type=str)
    parser_load.add_argument("-b", "--db", help=" Specify database name give a name for a new database", type=str)
    parser_load.add_argument(
        "-d",
        "--address",
        help="Add new address",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )


    parser_vcard = subparser.add_parser("vcard",help="generate vcard")
    parser_vcard.add_argument("-b", "--db", help="Specify database name ", type=str)



    parser_qrcode = subparser.add_parser("qrcode",help="generate qr  code")
    parser_qrcode.add_argument("-b", "--db", help="Specify database name ", type=str)
    parser_qrcode.add_argument(
        "-s", "--size", help= "Specifies a custom size between 100 and 500 (for the 'qrcode' action)", default=300
    )

    

    parser_employee = subparser.add_parser("employee",help = "Get the employee detail")

    parser_employee.add_argument("-e", "--employee", help=" specifies the employee id", type=int)
    parser_employee.add_argument("-b", "--db", help="Specify database name ", type=str)

    args = parser.parse_args()
    return args


def parse_data(filename):
    datalist = []
    with open(filename, "r") as data:
        detail = csv.reader(data)
        for i in detail:
            datalist.append(i)

    return datalist


def fetch_from_db(dbname,user):
    
    connection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connection.cursor()
    curs.execute(
        f"""SELECT first_name,last_name,designation,email,phone,company_address 
                     FROM
                     employees """
    )
    tup_datas = curs.fetchall()
    data = []
    for i in tup_datas:
        data.append(list(i))

    connection.commit()
    curs.close()
    connection.close()
    logger.info(f"Fetched all datas from employees table in {dbname} database")
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


def create_database(dbname,user):
    connection = psycopg2.connect(database="postgres", user=user)
    curs = connection.cursor()
    curs.execute("commit")
    curs.execute("create database %s ;",(AsIs(dbname),))
    curs.close()
    connection.close()
    logger.info("Database created")


def create_table(dbname,user):
    
    connnection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connnection.cursor()
    curs.execute(
        """CREATE TABLE employees(
                       s_no BIGSERIAL PRIMARY KEY,
                       first_name VARCHAR(50),
                       last_name VARCHAR(50) ,
                       designation VARCHAR(50), 
                       email VARCHAR(50),
                        phone VARCHAR(50), 
                       company_address VARCHAR(100) );"""
    )

    connnection.commit()
    curs.close()
    connnection.close()
    logger.info(f"Table employees created in {dbname} database")


def load_csv_into_db(dbname, data, address,user):
    connection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connection.cursor()
    fname, lname, designation, email, phone = data
    curs.execute(
        f"""INSERT
                     INTO 
                     employees(first_name, last_name, designation, email, phone, company_address)
                      VALUES(%s,%s,%s,%s,%s,%s)""",
        (fname, lname, designation, email, phone, address),
    )

    connection.commit()
    curs.close()
    connection.close()
    logger.debug(f" Inserted datas of {fname} into table employees ")

def create_leave_table(dbname,user):
    connnection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connnection.cursor()
    curs.execute(
        f"""CREATE TABLE leave_table(
                       s_no BIGSERIAL PRIMARY KEY,
                       leave_date DATE,
                       employee_id INTEGER REFERENCES employees(s_no) );"""
    )

    connnection.commit()
    curs.close()
    connnection.close()
    logger.info(f"Leave Table created in {dbname} database")

def load_leave_employee(dbname,user):
    connection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connection.cursor()
    load_file=open('leave_insert.sql','r')
    curs.execute(load_file.read())
    connection.commit()
    curs.close()
    connection.close()
    logger.info(" Inserted leaves into table leave_employee")

def fetch_employee_details(dbname,user,emp_id):
    connection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connection.cursor()
    curs.execute(
         """SELECT count(leave_date)
            FROM leave_table
            WHERE employee_id = %s ;""",((emp_id),)
    )
    leaves_counts = curs.fetchall()
    
    curs.execute(
        """ SELECT * FROM employees WHERE s_no = %s
""",((emp_id),))
    

    tup_datas = curs.fetchall()
    l_data = []
    
    for i in tup_datas:
       l_data.append(list(i))

    connection.commit()
    curs.close()
    connection.close()
    logger.info(f"Fetched all datas from employees table in {dbname} database")

    total_leaves = 5
    laeve_count = list(leaves_counts[0])
    leave_remaining = total_leaves - leaves_counts[0]
    return leave_remaining,l_data[0]


def main():
    args = parse_args()
    user = os.getenv("USERNAME")

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)
    if args.subcommand == "createdb":
        dbname = args.db
        
        create_database(dbname,user)

    if args.subcommand == "loadcsv":
        if args.load:
            address = args.address
            dbname = args.db
            file = args.load
            datas = parse_data(file)
            create_table(dbname, user)
            create_leave_table(dbname,user)
            print(len(datas))

            for i in range(len(datas)):
                data = datas[i]
                load_csv_into_db(dbname, data, address ,user)
                
            logger.info(f"Loaded all datas into database")
            load_leave_employee(dbname,user)

    if args.subcommand == "vcard":
        print(user)
        dbname = args.db
        
        data = fetch_from_db(dbname ,user)
        create_vcards(data)

    if args.subcommand == "qrcode":
        dbname = args.db
        
        dimension = args.size

        if type(dimension) != int or int(dimension) > 500:
            logger.error("size must be an integer between 100 - 500")
        else:
            data = fetch_from_db(dbname,user)
            create_qrcode_images(data, dimension)

    if args.subcommand == "employee":
        dbname = args.db
        emp_id = args.employee
        
        leave_remaining,details = fetch_employee_details(dbname,user,emp_id)
        
       # print("---------------------------------------------------------------------------------------------")
        print(Back.GREEN+f"""Employee's id : {details[0]} \n
              Employee's name: {details[1]} {details[2]} \n
              Designation : {details[3]} \n
              email: {details[4]} \n
              phone : {details[5]} \n
              Company address : {details[6]} \n
              Leaves Remaining : {leave_remaining}\n""")
        print(Style.RESET_ALL)
        

        
    
        



if __name__ == "__main__":
    main()

