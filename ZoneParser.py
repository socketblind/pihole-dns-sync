import os
import dns.zone
import dns.ipv4
import os.path
from config import *

class ZoneParser:
    a_records = []
    cname_records = []

    # Export DNS zone files
    def export_dns_zones(self):
        for zone in zones:
            print()
            cmd = 'pwsh -File .\export_dns_zone.ps1 ' + zone + ' ' + zone_files_path
            os.system(cmd)
        print()

    def parse_zone_files(self):
        for zone in zones:
            self.parse_zone_file(zone)

    def parse_zone_file(self,zonefile):
        filename = "tmp\\"+zonefile+".txt"
        zone = dns.zone.from_file(filename, os.path.basename(filename), relativize=False)
        
        for z in zone.iterate_rdatas('A'):
            name = str(z[0])[0:-5].lower()
            ip = str(z[2])
            if(name not in zones_excluded and
                not name.startswith('domaindnszones') and
                not name.startswith('forestdnszones')):
                self.a_records.append({'domain': name, 'ip': ip})

        for z in zone.iterate_rdatas('CNAME'):
            name = str(z[0])[0:-5].lower()
            target = str(z[2])[0:-1]
            if(name not in zones_excluded and
                not name.startswith('domaindnszones') and
                not name.startswith('forestdnszones')):
                self.cname_records.append({'domain': name, 'target': target})

    def sort_zones(self):
        self.a_records = sorted(self.a_records, key=lambda x: x['domain'])
        self.cname_records = sorted(self.cname_records, key=lambda x: x['domain'])

    def get_records(self):
        return {
            'a_records': self.a_records,
            'cname_records': self.cname_records
        }

    def print_result(self):
        print('RESULT')
        print("'A' records:")
        pp.pprint(self.a_records)
        print("'CNAME' records:")
        pp.pprint(self.cname_records)