from sqlite3.dbapi2 import SQLITE_TRANSACTION
from config import *
import sqlite3
import calendar
import time
from datetime import datetime
import shutil
from config import format_exception

class PiholeGravityHandler:
    overwrite = None
    db_file = None
    db = None
    adlist = []
    adlist_groups = []
    domainlist = []
    domainlist_groups = []
    adlist_addresses = []
    domainlist_domains = []
    table_schema = {
        'adlist': None,
        'adlist_by_group': None,
        'domainlist': None,
        'domainlist_by_group': None
    }
    
    def __init__(self, db_file, overwrite = {'adlist': False, 'domainlist': False}):
        self.db_file = db_file
        self.overwrite = overwrite

    def start(self):
        if(self.backup()):
            self.connect_db()
            self.collect_adlist()
            self.collect_domains()
            self.merge_config()
            self.close_db()
        else:
            raise Exception('Backup Failed!!!')

    # Creating backup files
    def backup(self):
        dt = datetime.now()
        try:
            source = self.db_file
            source_path = source[:source.rfind('/')+1]
            filename = source[source.rfind('/')+1:]
            target = source_path + filename + "." + (dt.strftime('%Y_%m_%d_%H_%M_%S') + ".bak")
            shutil.copy(source, target)
            print()
            print('DNS config file backups has been successfully created.')
            return True
        except Exception as e:
            print(format_exception(e))
            return False

    def sqlite_table_schema(self, name):
        cursor = self.db.execute("SELECT sql FROM sqlite_master WHERE tbl_name=? and (type='table' or type='trigger')", [name])
        sql = cursor.fetchall()
        cursor.close()
        return sql

    def connect_db(self):
        try:
            self.db = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_COLNAMES)
            print()
            print('Gravity database connection has been established.')
            print()
        except Exception as e:
            print(format_exception(e))
            return False

    def close_db(self):
        self.db.close()
        print('Gravity database connection has been closed.')

    def collect_adlist(self):
        self.adlist = self.db.execute('select * from adlist').fetchall()
        self.adlist_groups = self.db.execute('select * from adlist_by_group').fetchall()
        for record in self.adlist:
            self.adlist_addresses.append(record[1])

    def collect_domains(self):
        self.domainlist = self.db.execute('select * from domainlist').fetchall()
        self.domainlist_groups = self.db.execute('select * from domainlist_by_group').fetchall()
        for record in self.domainlist:
            self.domainlist_domains.append(record[2])

    def merge_config(self):
        inserted_rows = {
            'adlist': 0,
            'domains': 0
        }
        new_lists = {
            'adlist': [],
            'domainlist': [],
        }

        if(self.overwrite['adlist']):
            # Truncate tables
            self.table_schema['adlist'] = self.sqlite_table_schema('adlist')
            self.table_schema['adlist_by_group'] = self.sqlite_table_schema('adlist_by_group')
            self.table_schema['domainlist'] = self.sqlite_table_schema('domainlist')
            self.table_schema['domainlist_by_group'] = self.sqlite_table_schema('domainlist_by_group')
            self.db.execute('drop table adlist');
            self.db.execute('drop table adlist_by_group');
            self.db.execute('drop table domainlist');
            self.db.execute('drop table domainlist_by_group');

            # Recreate tables & triggers
            for schema in self.table_schema['adlist']:
                self.db.execute(schema[0])
            for schema in self.table_schema['domainlist']:
                self.db.execute(schema[0])
            for schema in self.table_schema['adlist_by_group']:
                self.db.execute(schema[0])
            for schema in self.table_schema['domainlist_by_group']:
                self.db.execute(schema[0])

            # Insert Adlist config
            for record in adlist_config:
                current_GMT = time.gmtime()
                ts = calendar.timegm(current_GMT)
                cursor = self.db.execute("insert into adlist (address, enabled, date_added, date_modified, comment, date_updated, number, invalid_domains, status) values (?,?,?,?,?,?,?,?,?)", (
                        str(record['address']),
                        int(record['enabled']),
                        ts,
                        ts,
                        str(record['comment']),
                        None,
                        0,
                        0,
                        int(record['status'])
                ))
                self.db.commit()
                cursor.close()
                inserted_rows['adlist'] += 1
                new_lists['adlist'].append(record['address'])

            # Insert Domainlist config
            for record in domainlist_config:
                current_GMT = time.gmtime()
                ts = calendar.timegm(current_GMT)
                cursor = self.db.execute("insert into domainlist (type, domain, enabled, date_added, date_modified, comment) values (?,?,?,?,?,?)", (
                        int(record['type']),
                        str(record['domain']),
                        int(record['enabled']),
                        ts,
                        ts,
                        str(record['comment'])
                    ))
                self.db.commit()
                cursor.close()
                inserted_rows['domains'] +=1
                new_lists['domainlist'].append(record['domain'])
        else:
            # Merging Adlist
            for record in adlist_config:
                if(not record['address'] in self.adlist_addresses):
                    current_GMT = time.gmtime()
                    ts = calendar.timegm(current_GMT)
                    cursor = self.db.execute("insert into adlist (address, enabled, date_added, date_modified, comment, date_updated, number, invalid_domains, status) values (?,?,?,?,?,?,?,?,?)", (
                        str(record['address']),
                        int(record['enabled']),
                        ts,
                        ts,
                        str(record['comment']),
                        None,
                        0,
                        0,
                        int(record['status'])
                    ))
                    self.db.commit()
                    cursor.close()
                    inserted_rows['adlist'] += 1
                    new_lists['adlist'].append(record['address'])
                    
            # Merging Domainlist 
            for record in domainlist_config:
                if(not record['domain'] in self.domainlist_domains):
                    current_GMT = time.gmtime()
                    ts = calendar.timegm(current_GMT)
                    cursor = self.db.execute("insert into domainlist (type, domain, enabled, date_added, date_modified, comment) values (?,?,?,?,?,?)", (
                        int(record['type']),
                        str(record['domain']),
                        int(record['enabled']),
                        ts,
                        ts,
                        str(record['comment'])
                    ))
                    self.db.commit()
                    cursor.close()
                    inserted_rows['domains'] +=1
                    new_lists['domainlist'].append(record['domain'])

        print("Number of adlists inserted: " + str(inserted_rows['adlist']))
        print("Number of domains inserted: " + str(inserted_rows['domains']))
        print("New Adlists: " + str(new_lists['adlist']))
        print("New Domains: " + str(new_lists['domainlist']))
        print()