from vcard import parse_data,generate_vcard_content

def test_parsed_data():
    file = "test_files/test_sample.csv"
    assert parse_data(file) == [['Campbell', 'Pamela', 'Hydrologist', 'pamel.campb@wilson.com', '001-371-295-6798x4774'],
                               ['Ayers', 'Adam', 'Clinical cytogeneticist', 'adam.ayers@lopez-wu.biz', '+1-407-869-4881']]
                                

