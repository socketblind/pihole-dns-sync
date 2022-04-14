import shutil
from datetime import datetime
from config import format_exception

class PiholeDNSHandler:
    overwrite = None
    conf_files = {}
    new_records = {}
    cname_records = []
    a_records = []
    final_cname_records = []
    final_a_records = []

    def __init__(self, conf_files, new_records, overwrite=False):
        self.overwrite = overwrite
        self.conf_files = conf_files
        self.new_records = new_records
        self.cname_records = []
        self.a_records = []
        self.final_cname_records = []
        self.final_a_records = []

    # Starting handler processes
    # ---
    def start(self):
        if(self.backup()):
            self.parse_dns_files()
            return self.merge_records()
        else:
            raise Exception('Backup failed!!!')

    # Creating backup files
    def backup(self):
        dt = datetime.now()
        for file in self.conf_files:
            try:
                source = self.conf_files[file]
                source_path = source[:source.rfind('/')+1]
                filename = source[source.rfind('/')+1:]
                target = source_path + filename + "." + (dt.strftime('%Y_%m_%d_%H_%M_%S') + ".bak")
                shutil.copy(source, target)
                print()
                print('DNS config file backups has been created successfully.')
                return True
            except Exception as e:
                print(format_exception(e))
                return False

    # Parsing old DNS files
    # ---
    def parse_dns_files(self):
        with open(self.conf_files['cname_records'], 'r') as file:
            data = file.readlines()
            if len(data) > 0 and data[0] != '\n':
                for line in data:
                    record = line.replace('cname=','').replace('\n','').split(',')
                    self.cname_records.append({
                        'domain': record[0],
                        'target': record[1],
                    })
                self.cname_records = sorted(self.cname_records, key=lambda x: x['domain'])
        
        with open(self.conf_files['a_records'], 'r') as file:
            data = file.readlines()
            if len(data) > 0 and data[0] != '\n':
                for line in data:
                    record = line.replace('\n','').split(' ')
                    self.a_records.append({
                        'domain': record[1],
                        'ip': record[0],
                    })
                self.a_records = sorted(self.a_records, key=lambda x: x['domain'])

    # Merging old and new records together
    # ---
    def merge_records(self):
        if(self.overwrite):
            for record in self.new_records['cname_records']:
                self.final_cname_records.append(record)
            for record in self.new_records['a_records']:
                self.final_a_records.append(record)
        else:
            for record in self.cname_records:
                self.final_cname_records.append(record)
            for record in self.a_records:
                self.final_a_records.append(record)

            for record in self.new_records['cname_records']:
                if(not record['domain'] in self.get_existing_cname_records()):
                    self.final_cname_records.append(record)
            for record in self.new_records['a_records']:
                if(not record['domain'] in self.get_existing_a_records()):
                    self.final_a_records.append(record)

        return self.write_records_to_file(self.final_cname_records, self.final_a_records)

    # Writing data out to config files
    # ---
    def write_records_to_file(self, cname_records, a_records):
        try:
            with open(self.conf_files['cname_records'], 'w') as file:
                data = ''
                for record in cname_records:
                    data += 'cname=' + record['domain'] + ',' + record['target'] + '\n'
                file.write(data)

            with open(self.conf_files['a_records'], 'w') as file:
                data = ''
                for record in a_records:
                    data += record['ip'] + ' ' + record['domain'] + '\n'
                file.write(data)
                print()
                print("New DNS config files has been written successfully.")
                return True
        except Exception as e:
            print(format_exception(e))
            return False

    # Getters
    # ---
    def get_existing_cname_records(self):
        cname_records = []
        for record in self.final_cname_records:
            cname_records.append(record['domain'])
        return cname_records

    def get_existing_a_records(self):
        a_records = []
        for record in self.final_a_records:
            a_records.append(record['domain'])
        return a_records

    def get_cname_records(self):
        return self.cname_records

    def get_a_records(self):
        return self.a_records