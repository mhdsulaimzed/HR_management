import psycopg2

import argparse
import csv
import logging
import os
import requests


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
        ---------------------------------------------------------------------------------------------------
        This Program is designed to do HR management operations like 
        -initialise a database in postgres SQL
        -load data from csv file  
        -generate vcard 
        -generate qrcode 

        ---------------------------------------------------------------------------------------------------
        """,
        epilog="use these options to do specific fuctions as  written above",
    )
    parser.add_argument(
        "action",
        help="Operations to be performed Choose from above ",
        choices=[ "createdb","loadcsv", "vcard", "qrcode"],
    )
    parser.add_argument("-b", "--db", help="Specify database name / give a name for a new database", type=str)
    parser.add_argument(
        "-l", "--load", help="Specifies the file name to be loaded (for the 'loadcsv' action)", type=str
    )
    parser.add_argument(
        "-t", "--table", help=" Specifies the table name (default is 'employees')", type=str, default="employees"
    )
    parser.add_argument(
        "-v", "--verbose", help="print out detailed logs", action="store_true"
    )
   
    
    parser.add_argument(
        "-s", "--size", help= "Specifies a custom size between 100 and 500 (for the 'qrcode' action)", default=300
    )
    parser.add_argument(
        "-d",
        "--address",
        help="Add new address",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )

    args = parser.parse_args()
    return args


def parse_data(filename):
    datalist = []
    with open(filename, "r") as data:
        detail = csv.reader(data)
        for i in detail:
            datalist.append(i)

    return datalist


def fetch_from_db(dbname, tname ,user):
    print(dbname, tname)
    connection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connection.cursor()
    curs.execute(
        f"""SELECT first_name,last_name,designation,email,phone,company_address 
                     FROM
                     {tname} """
    )
    tup_datas = curs.fetchall()
    data = []
    for i in tup_datas:
        data.append(list(i))

    connection.commit()
    curs.close()
    connection.close()
    logger.info(f"Fetched all datas from {tname} table in {dbname} database")
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


def create__vcards(data):
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
    curs.execute(f"create database {dbname}")
    curs.close()
    connection.close()
    logger.info("Database created")


def create_table(dbname, tname,user):
    print(dbname, tname)
    connnection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connnection.cursor()
    curs.execute(
        f"""CREATE TABLE {tname}(
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
    logger.info(f"Table {tname} created in {dbname} database")


def load_csv_into_db(dbname, tname, data, address,user):
    connection = psycopg2.connect(f"dbname={dbname} user={user}")
    curs = connection.cursor()
    fname, lname, designation, email, phone = data
    curs.execute(
        f"""INSERT
                     INTO 
                     {tname}(first_name, last_name, designation, email, phone, company_address)
                      VALUES(%s,%s,%s,%s,%s,%s)""",
        (fname, lname, designation, email, phone, address),
    )

    connection.commit()
    curs.close()
    connection.close()
    logger.debug(f" Inserted datas of {fname} into table{tname} ")


def main():
    args = parse_args()
    user = os.getenv("USERNAME")

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)
    if args.action == "createdb":
        dbname = args.db
        print(args.action)
        create_database(dbname,user)

    if args.action == "loadcsv":
        if args.load:
            address = args.address
            dbname = args.db
            file = args.load
            tname = args.table
            datas = parse_data(file)
            create_table(dbname, tname, user)
            print(len(datas))

            for i in range(len(datas)):
                data = datas[i]
                load_csv_into_db(dbname, tname, data, address ,user)
            logger.info(f"Loaded all datas into database")

    if args.action == "vcard":
        print(user)
        dbname = args.db
        tname = args.table
        data = fetch_from_db(dbname, tname ,user)
        create__vcards(data)

    if args.action == "qrcode":
        dbname = args.db
        tname = args.table
        dimension = args.size

        if type(dimension) != int or int(dimension) > 500:
            logger.error("size must be an integer between 100 - 500")
        else:
            data = fetch_from_db(dbname,tname,user)
            create_qrcode_images(data, dimension)
   
        
    
        


if __name__ == "__main__":
    main()
