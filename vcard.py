import argparse
import csv
import logging
import os
import requests


logger = None


def setup_logging(log_level):
    global logger
    logger = logging.getLogger("SheetGen")
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    fhandler.setLevel(logging.DEBUG)
    handler.setLevel(log_level)
    handler.setFormatter(
        logging.Formatter(
            "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
        )
    )
    fhandler.setFormatter(
        logging.Formatter(
            "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
        )
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="vcard.py",
        description="Generates Vcards and Qr codes for employees in csv files as vcf and png format respectively",
        epilog="use these options to doto specific fuctions as  written below",
    )
    parser.add_argument("filename")
    parser.add_argument("-v", "--verbose", help="print out detailed logs", action="store_true")
    parser.add_argument( "-a", "--all" , help ="Print both qr and vcard file" ,action="store_true" ,default=False)
    parser.add_argument("-s","--size", help="Add custom size between 100 and 500" ,type=int ,default=300)
    parser.add_argument("-ad","--address",help="Add new address",type=str, default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America")


    args = parser.parse_args()
    return args


def parse_data(filename):
    datalist = []
    with open(filename, "r") as data:
        detail = csv.reader(data)
        for i in detail:
            datalist.append(i)

    return datalist


def generate_vcard_content(lname, fname, designation,email, phone,address):
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


def generate__vcards(data,address):
    os.mkdir("vcards")
    for i in data:
        lname, fname, designation, email, phone = i
        with open(f"vcards/{lname}.vcf", "w") as d:
            d.write(generate_vcard_content(lname, fname, designation, email, phone,address))
        logger.debug("Created vcard for %s ", lname)
    logger.info("Created all vcards")


def generate_qr_code(data,dimension):
    os.mkdir("qrcode")
    
    for i in data:
        qr_code = requests.get(f"https://chart.googleapis.com/chart?cht=qr&chs={dimension}x{dimension}&chl={i}")

        with open(f"qrcode/{i[0]}.qr.png", "wb") as Q:
            Q.write(qr_code.content)
        logger.debug("Created QRcode for %s", i[0])
    logger.info("Created QRs for all")


def main():
    args = parse_args()
    dimension=args.size
    address=args.address
    if args.verbose:
    
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)

    file = args.filename
    data = parse_data(file)
    
    generate__vcards(data,address)
    if args.all:
        generate_qr_code(data,dimension)

    

    
if __name__ == "__main__":
    main()


