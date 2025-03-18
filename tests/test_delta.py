# tests/test_compare.py
import io
import os
import unittest
import pandas as pd
from pandas import DataFrame

import pyDeltafile.delta as pc


OLD_FILE_CSV = 'output/test_file1.csv'
NEW_FILE_CSV = 'output/test_file2.csv'
OUTPUT_FILE_CSV = 'output/output_file.csv'
DELTA_FILE_CSV = 'output/delta_file.csv'
DELTA_FILE2_CSV = 'output/delta_file2.csv'

OLD_FILE_JSON = 'output/test_file1.json'
NEW_FILE_JSON = 'output/test_file2.json'
DELTA_FILE_JSON = 'output/delta_file.json'
DELTA_FILE2_JSON = 'output/delta_file2.json'

class TestCompare(unittest.TestCase):

    def _write_file(self, file_path:str, data:str):
        f = open(file_path, "w")
        f.write(data)
        f.close()

    def setUp(self):
        # Crea file CSV di esempio per i test
        self.file1 = OLD_FILE_CSV
        self.file2 = NEW_FILE_CSV
        old_data = """
id,first_name,last_name,email,gender,ip_address
1,Leonard,Gerran,lgerran0@meetup.com,Male,142.106.215.156
2,Josepha,Checklin,jchecklin1@wiley.com,Female,45.0.210.191
3,Flemming,Dursley,fdursley2@yahoo.com,Male,239.238.145.163
4,Park,Bowkley,pbowkley3@google.ca,Male,96.119.231.172
5,Raoul,Boreland,rboreland4@sbwire.com,Male,89.227.7.140
6,Glynnis,Cotilard,gcotilard5@ed.gov,Female,14.169.23.61
7,Maure,Gerhartz,mgerhartz6@cbsnews.com,Female,211.144.32.239
8,Jameson,Klesel,jklesel7@oaic.gov.au,Male,182.253.243.211
9,Maxim,Sambrok,msambrok8@e-recht24.de,Male,204.141.194.90
10,Stella,Grossman,sgrossman9@infoseek.co.jp,Female,235.130.153.140
        """
        new_data = """
id,first_name,last_name,email,gender,ip_address
1,Leonard,Gerran,lgerran0@meetup.com,Male,142.106.215.156
3,Flemming,Dursley,fdursley2@yahoo.com,Male,239.238.145.163
5,Raoul,Boreland,rboreland4@sbwire.com,Male,89.227.7.140
7,Maure,Gerhartz,mgerhartz6@cbsnews.com,Female,211.144.32.239
9,Maxim,Sambrok,msambrok8@e-recht24.de,Male,204.141.194.90
11,Christi,Braben,cbrabena@npr.org,Female,165.49.144.201
13,Gabby,Gladdin,ggladdinc@virginia.edu,Male,153.56.64.234
15,Mill,Chadwell,mchadwelle@archive.org,Male,15.126.32.220
17,Egbert,Normavell,enormavellg@cisco.com,Male,235.130.153.140
        """
        self._write_file(self.file1, old_data)
        self._write_file(self.file2, new_data)

        # Crea file JSON di esempio per i test
        self.file_json1 = OLD_FILE_JSON
        self.file_json2 = NEW_FILE_JSON
        old_json_data = """
            [{"id":1,"first_name":"Leonard","last_name":"Gerran","email":"lgerran0@meetup.com","gender":"Male","ip_address":"142.106.215.156"},{"id":2,"first_name":"Josepha","last_name":"Checklin","email":"jchecklin1@wiley.com","gender":"Female","ip_address":"45.0.210.191"},{"id":3,"first_name":"Flemming","last_name":"Dursley","email":"fdursley2@yahoo.com","gender":"Male","ip_address":"239.238.145.163"},{"id":4,"first_name":"Park","last_name":"Bowkley","email":"pbowkley3@google.ca","gender":"Male","ip_address":"96.119.231.172"},{"id":5,"first_name":"Raoul","last_name":"Boreland","email":"rboreland4@sbwire.com","gender":"Male","ip_address":"89.227.7.140"},{"id":6,"first_name":"Glynnis","last_name":"Cotilard","email":"gcotilard5@ed.gov","gender":"Female","ip_address":"14.169.23.61"},{"id":7,"first_name":"Maure","last_name":"Gerhartz","email":"mgerhartz6@cbsnews.com","gender":"Female","ip_address":"211.144.32.239"},{"id":8,"first_name":"Jameson","last_name":"Klesel","email":"jklesel7@oaic.gov.au","gender":"Male","ip_address":"182.253.243.211"},{"id":9,"first_name":"Maxim","last_name":"Sambrok","email":"msambrok8@e-recht24.de","gender":"Male","ip_address":"204.141.194.90"},{"id":10,"first_name":"Stella","last_name":"Grossman","email":"sgrossman9@infoseek.co.jp","gender":"Female","ip_address":"235.130.153.140"}]
        """
        new_json_data = """
            [{"id":1,"first_name":"Leonard","last_name":"Gerran","email":"lgerran0@meetup.com","gender":"Male","ip_address":"142.106.215.156"},{"id":3,"first_name":"Flemming","last_name":"Dursley","email":"fdursley2@yahoo.com","gender":"Male","ip_address":"239.238.145.163"},{"id":5,"first_name":"Raoul","last_name":"Boreland","email":"rboreland4@sbwire.com","gender":"Male","ip_address":"89.227.7.140"},{"id":7,"first_name":"Maure","last_name":"Gerhartz","email":"mgerhartz6@cbsnews.com","gender":"Female","ip_address":"211.144.32.239"},{"id":9,"first_name":"Maxim","last_name":"Sambrok","email":"msambrok8@e-recht24.de","gender":"Male","ip_address":"204.141.194.90"},{"id":11,"first_name":"Christi","last_name":"Braben","email":"cbrabena@npr.org","gender":"Female","ip_address":"165.49.144.201"},{"id":13,"first_name":"Gabby","last_name":"Gladdin","email":"ggladdinc@virginia.edu","gender":"Male","ip_address":"153.56.64.234"},{"id":15,"first_name":"Mill","last_name":"Chadwell","email":"mchadwelle@archive.org","gender":"Male","ip_address":"15.126.32.220"},{"id":17,"first_name":"Egbert","last_name":"Normavell","email":"enormavellg@cisco.com","gender":"Male","ip_address":"235.130.153.140"}]
        """
        self._write_file(self.file_json1, old_json_data)
        self._write_file(self.file_json2, new_json_data)
        # set key_columns
        self.keys_columns = ['ip_address']
        self.keys_columns_alternative = ['email', 'gender', 'ip_address']

    def test__read_file_csv(self):
        df = pc._read_file_csv(OLD_FILE_CSV,  self.keys_columns,0)
        # assertions
        self.assertIsNotNone(df)
        self.assertIn(pc.HASH_ALL_COLUMNS_KEY, df.columns)
        self.assertIn(pc.HASH_KEY_COLUMNS_KEY, df.columns)

    def test__calculate_uid(self):
        df = pc._read_file_csv(OLD_FILE_CSV,  self.keys_columns, 0)
        # assertions
        self.assertEqual(df.loc[0][pc.HASH_ALL_COLUMNS_KEY],'a10d7912da9315665884fe6defa8b95f')

    def test__calculate_rid(self):
        df1 = pc._read_file_csv(OLD_FILE_CSV,  self.keys_columns, 0)
        df2 = pc._read_file_csv(OLD_FILE_CSV, self.keys_columns_alternative, 0)
        # assertions
        self.assertEqual(df1.loc[0][pc.HASH_KEY_COLUMNS_KEY], 'a8948369d352f6c74a94c1598f264e39')
        self.assertEqual(df2.loc[0][pc.HASH_KEY_COLUMNS_KEY], 'c65495af670783e6cd5343defca6effa')

    def test__add_hash_all_columns(self):
        df = pc._read_file_csv(OLD_FILE_CSV,  self.keys_columns, 0)
        # assertions
        self.assertIn(pc.HASH_ALL_COLUMNS_KEY, df.columns)

    def test__add_hash_key_columns(self):
        df = pc._read_file_csv(OLD_FILE_CSV,  self.keys_columns, 0)
        # assertions
        self.assertIn(pc.HASH_KEY_COLUMNS_KEY, df.columns)

    def test__get_line_to_delete(self):
        old_data = pc._read_file_csv(OLD_FILE_CSV,  self.keys_columns, 0)
        new_data = pc._read_file_csv(NEW_FILE_CSV,  self.keys_columns, 0)
        to_delete = pc._get_line_to_delete(old_data, new_data,  self.keys_columns)
        # assertions
        ids = to_delete['id'].tolist()
        self.assertEqual(len(ids), 4)
        self.assertIn(2, ids)
        self.assertIn(4, ids)
        self.assertIn(6, ids)
        self.assertIn(8, ids)
        #self.assertIn(10, ids)

    def test__get_line_to_add(self):
        old_data = pc._read_file_csv(OLD_FILE_CSV, self.keys_columns, 0)
        new_data = pc._read_file_csv(NEW_FILE_CSV, self.keys_columns, 0)
        to_add = pc._get_line_to_add(old_data, new_data, self.keys_columns)
        # assertions
        ids = to_add['id'].tolist()
        self.assertEqual(len(to_add), 3)
        self.assertIn(11, ids)
        self.assertIn(13, ids)
        self.assertIn(15, ids)

    def test__save_dataframe(self):
        old_data = pc._read_file_csv(OLD_FILE_CSV, self.keys_columns, 0)
        pc._save_dataframe(OUTPUT_FILE_CSV, old_data)
        # assertions
        self.assertTrue( os.path.isfile(OUTPUT_FILE_CSV) )

    def test__delta_csv(self):
        # *** test 1
        pc.delta_csv(OLD_FILE_CSV, NEW_FILE_CSV, DELTA_FILE_CSV, self.keys_columns, 0)
        # assertions
        self.assertTrue( os.path.isfile(DELTA_FILE_CSV) )

        # *** test 2
        def delete_callback(dataframe: DataFrame) -> DataFrame:
            df = dataframe.copy()  # Create a copy to avoid SettingWithCopyWarning
            df['Delete'] = 1
            return df
        def upsert_callback(dataframe:DataFrame) -> DataFrame:
            df = dataframe.copy()  # Create a copy to avoid SettingWithCopyWarning
            df['Delete'] = 0
            return df
        pc.delta_csv(OLD_FILE_CSV, NEW_FILE_CSV, DELTA_FILE2_CSV, self.keys_columns, 0, delete_callback, upsert_callback, upsert_callback)
        # assertions
        self.assertTrue(os.path.isfile(DELTA_FILE2_CSV))

    def test__delta_json(self):
        # *** test 1
        pc.delta_json(OLD_FILE_JSON, NEW_FILE_JSON, DELTA_FILE_JSON, self.keys_columns)
        # assertions
        self.assertTrue( os.path.isfile(DELTA_FILE_JSON) )
        # *** test 2
        def delete_callback(dataframe: DataFrame) -> DataFrame:
            df = dataframe.copy()  # Create a copy to avoid SettingWithCopyWarning
            df['Delete'] = 1
            return df
        def upsert_callback(dataframe:DataFrame) -> DataFrame:
            df = dataframe.copy()  # Create a copy to avoid SettingWithCopyWarning
            df['Delete'] = 0
            return df
        pc.delta_json(OLD_FILE_JSON, NEW_FILE_JSON, DELTA_FILE2_JSON, self.keys_columns, delete_callback, upsert_callback, upsert_callback)
        # assertions
        self.assertTrue(os.path.isfile(DELTA_FILE2_JSON))

    def test_tearDown(self):
        # Pulisce i file di test
        import os
        # generic
        os.remove(OUTPUT_FILE_CSV)
        # csv
        os.remove(OLD_FILE_CSV)
        os.remove(NEW_FILE_CSV)
        os.remove(DELTA_FILE_CSV)
        os.remove(DELTA_FILE2_CSV)
        # json
        os.remove(OLD_FILE_JSON)
        os.remove(NEW_FILE_JSON)
        os.remove(DELTA_FILE_JSON)
        os.remove(DELTA_FILE2_JSON)

if __name__ == '__main__':
    unittest.main()