from hr import parse_data,generate_vcard_content

def test_parsed_data():
    file = "test_files/test_sample.csv"
    assert parse_data(file) == [['Campbell', 'Pamela', 'Hydrologist', 'pamel.campb@wilson.com', '001-371-295-6798x4774'],
                               ['Ayers', 'Adam', 'Clinical cytogeneticist', 'adam.ayers@lopez-wu.biz', '+1-407-869-4881']]
                                

def test_getvcard():
    lname, fname, designation, email, phone = ["Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"]
    address = "Hamon technologies"
    assert generate_vcard_content(lname, fname, designation, email, phone ,address) == """BEGIN:VCARD
VERSION:2.1
N:Warren;Tammy
FN:Tammy Warren
ORG:Authors, Inc.
TITLE:Information officer
TEL;WORK;VOICE:(794)913-7421
ADR;WORK:;;Hamon technologies
EMAIL;PREF;INTERNET:tammy.warre@romero.org
REV:20150922T195243Z
END:VCARD
""" 