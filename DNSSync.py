
from PiholeGravityHandler import PiholeGravityHandler
from ZoneParser import ZoneParser
from SSH_SFTP_Client import SSH_SFTP_Client
from PiholeDNSHandler import PiholeDNSHandler
from config import *

class DNSSync:
    zone_records = None
    def __init__(self):
        pass

    def parse_local_zones(self):
        zp = ZoneParser()
        zp.export_dns_zones()
        zp.parse_zone_files()
        zp.sort_zones()
        # zp.print_result()
        self.zone_records = zp.get_records()

    def sync_hosts(self):
        for host in target_hosts:
            self.sync_host(host)

    def sync_host(self, host):
        conn = None
        host_tmp_path = "./tmp/" + host + "/"
        dnsmasq_file_name = dnsmasq_file_path.split('/')[-1]
        custom_dns_file_name = custom_dns_file_path.split('/')[-1]
        gravitydb_file_name = gravitydb_file_path.split('/')[-1]
        try:
            # Initiate Connection
            conn = SSH_SFTP_Client(host, 22, credentials[0], credentials[1])

            # Setting permissions to correct local access (NOPASSWD: sudo option necessary)
            conn.send_command("sudo touch " + dnsmasq_file_path)
            conn.send_command("sudo touch " + custom_dns_file_path)
            conn.send_command("sudo touch " + gravitydb_file_path)
            conn.send_command(pihole_file_permission_command + dnsmasq_file_path)
            conn.send_command(pihole_file_permission_command + custom_dns_file_path)
            conn.send_command(pihole_file_permission_command + gravitydb_file_path)

            # Getting files from remote server
            conn.get_file(dnsmasq_file_path)
            conn.get_file(custom_dns_file_path)
            conn.get_file(gravitydb_file_path)

            # Initiate DNS merging
            dns_handler = PiholeDNSHandler({
                    "cname_records": host_tmp_path + dnsmasq_file_name,
                    "a_records": host_tmp_path + custom_dns_file_name
                },
                self.zone_records,
                overwrite_dns_files)
            dns_handler.start()
            print()

            # Initiate Adlist & Domain list modification
            gravity_handler = PiholeGravityHandler(host_tmp_path + gravitydb_file_name, overwrite_gravity)
            gravity_handler.start()
            print()

            # Disable Pi-Hole services (just in case)
            conn.send_command(pihole_disable_command)

            # Copying over files to the actual host (overwrite)
            conn.put_file(host_tmp_path + dnsmasq_file_name, dnsmasq_file_path.replace(dnsmasq_file_name,''))
            conn.put_file(host_tmp_path + custom_dns_file_name, custom_dns_file_path.replace(custom_dns_file_name,''))
            conn.put_file(host_tmp_path + gravitydb_file_name, gravitydb_file_path.replace(gravitydb_file_name,''))

            # Restart DNS server to parse new files
            conn.send_command(pihole_restart_dnsmasq_command)

            # Update gravity to parse new adlists
            conn.send_command(pihole_update_gravity_command)

            # Re-Enabling Pi-Hole services
            conn.send_command(pihole_enable_command)

            print()
            print('Host syncing was successful: ' + host)

            conn.close();
            return True
        except Exception as e:
            print(format_exception(e))
            return False

    def start(self):
        self.parse_local_zones()
        self.sync_hosts()

dns_sync = DNSSync()
dns_sync.start()
print()

