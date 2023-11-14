import csv
import os
import sys


def get_vcard(filename):
    with open(filename, "r") as data:
        detail = csv.reader(data)
        os.mkdir("vcards")
        for i in detail:
            lname, fname, designation, email, phone = i
            
            with open(f"vcards/{lname}.txt", "w") as d:
                d.write(
                    f"""
                        BEGIN:VCARD
                     
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
                                        )
            

if __name__ == "__main__":
    f = sys.argv[1]
    get_vcard(f)