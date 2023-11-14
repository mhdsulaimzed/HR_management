import csv
import os
import sys


def parse_data(filename):
    datalist = []
    with open(filename, "r") as data:
        detail = csv.reader(data)
        for i in detail:
            print(i)
            datalist.append(i)
    return datalist


def generate_vcard_content(lname, fname, designation, email, phone):
    return f"""BEGIN:VCARD 
               VERSION:2.1 
               N:{lname};{fname} 
               FN:{fname} {lname} 
               ORG:Authors, Inc. 
               TITLE:{designation} 
               TEL;WORK;VOICE:{phone} 
               ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America 
               EMAIL;PREF;INTERNET:{email} 
               REV:20150922T195243Z 
               END:VCARD 
               """


def generate__vcards(data):
    os.mkdir("vcards")
    for i in data:
        lname, fname, designation, email, phone = i
        with open(f"vcards/{lname}.vcf", "w") as d:
            d.write(generate_vcard_content(lname, fname, designation, email, phone))


if __name__ == "__main__":
    data = parse_data(sys.argv[1])
    generate__vcards(data)
