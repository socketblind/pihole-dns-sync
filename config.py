import pprint
import traceback
import sys

# ZoneParser config
# ---

pp = pprint.PrettyPrinter(indent=4)
zones = [
    'home.lab',
    'raspberry.lan',
]
zones_excluded = ['home.lab'] # For removing junk records from the main Forest
zone_files_path = "D:\Scripts\\DNSSync\\tmp"

# SSH/SFTP Client config
# ---

# Source Host
source_host = "localhost"
# Target hosts
target_hosts = [
    'server1.home.lab',
    'server2.home.lab',
    'raspberry.lan'
]

credentials = [
    'remote_user',
    'remote_password'
]

# Pi-Hole Config
# ---

# Pi-Hole Commands
pihole_file_permission_command = 'sudo chown ' + credentials[0] + ':' + credentials[0] + ' '
pihole_disable_command = 'docker exec pihole pihole disable'
pihole_enable_command = 'docker exec pihole pihole enable'
pihole_restart_dnsmasq_command = 'docker exec pihole pihole restartdns'
pihole_update_gravity_command = 'docker exec pihole pihole -g'

# Behavior options
overwrite_dns_files = True
overwrite_gravity = {
    'adlist': True,
    'domainlist': True
}

# Database filepaths
gravitydb_file_path = "/opt/pihole/etc/gravity.db"
piholeftl_file_path = "/opt/pihole/etc/pihole-FTL.db"
custom_dns_file_path = '/opt/pihole/etc/custom.list'
dnsmasq_file_path = '/opt/pihole/dnsmasq.d/05-pihole-custom-cname.conf'

# Default config for adlists and domainlists (will be merged or overwritten on top of remote records)
adlist_config = [
    {
        'address': 'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
        'enabled': True,
        'comment': 'Migrated from /etc/pihole/adlists.list',
        'status': 2
    },
    {
        'address': 'https://blocklistproject.github.io/Lists/ads.txt',
        'enabled': True,
        'comment': 'Ads',
        'status': 2
    },
    {
        'address': 'https://blocklistproject.github.io/Lists/tracking.txt',
        'enabled': True,
        'comment': 'Trackings',
        'status': 2
    },
    {
        'address': 'https://blocklistproject.github.io/Lists/phishing.txt',
        'enabled': True,
        'comment': 'Phisings',
        'status': 2
    },
    {
        'address': 'https://blocklistproject.github.io/Lists/everything.txt',
        'enabled': False,
        'comment': 'Everything',
        'status': 0
    },
    {
        'address': 'https://blocklistproject.github.io/Lists/malware.txt',
        'enabled': True,
        'comment': 'Malware',
        'status': 2
    },
    {
        'address': 'https://blocklistproject.github.io/Lists/ransomware.txt',
        'enabled': True,
        'comment': 'Ransomware',
        'status': 2
    }
]

domainlist_config = [
    {
        'domain': 'analytics.google.com',
        'type': 0,
        'enabled': True,
        'comment': ''
    },
    {
        'domain': 'facebook.com',
        'type': 0,
        'enabled': False,
        'comment': ''
    },
    {
        'domain': 'instagram.com',
        'type': 0,
        'enabled': False,
        'comment': ''
    },
    {
        'domain': '(\.|^)facebook\.com$',
        'type': 2,
        'enabled': False,
        'comment': ''
    },
    {
        'domain': 'www.facebook.com',
        'type': 0,
        'enabled': False,
        'comment': ''
    },
    {
        'domain': 'www.instagram.com',
        'type': 0,
        'enabled': False,
        'comment': ''
    },
    {
        'domain': 'static.xx.fbcdn.net',
        'type': 0,
        'enabled': False,
        'comment': 'Facebook assets'
    },
]

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str