import os
import paramiko

class SSH_SFTP_Client:
    host = None
    ssh = None
    sftp = None
    key = None
    ssh_stdin = []
    ssh_stdout = []
    ssh_stderr = []

    def __init__(self, host, port, username, password, keyfilepath=None, keyfiletype=None):
        print("\nCreating SSH/SFTP Connection to " + host + "...")
        self.host = host;
        self.ssh = None
        self.sftp = None
        self.key = None
        ssh_stdin = []
        ssh_stdout = []
        ssh_stderr = []
        try:
            if keyfilepath is not None:
                # Get private key used to authenticate user.
                if keyfiletype == 'DSA':
                    # The private key is a DSA type key.
                    self.key = paramiko.DSSKey.from_private_key_file(keyfilepath)
                else:
                    # The private key is a RSA type key.
                    self.key = paramiko.RSAKey.from_private_key(keyfilepath)
    
            # Connect SSH client accepting all host keys.
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.host, port, username, password, self.key)
    
            # Using the SSH client, create a SFTP client.
            self.sftp = self.ssh.open_sftp()
            # Keep a reference to the SSH client in the SFTP client as to prevent the former from
            # being garbage collected and the connection from being closed.
            self.sftp.sshclient = self.ssh

            print("Connection established...")

        except Exception as e:
            print('An error occurred creating SFTP client: %s: %s' % (e.__class__, e))
            if self.sftp is not None:
                self.sftp.close()
            if self.ssh is not None:
                self.ssh.close()
            pass

    def send_command(self, cmd):
        self.ssh_stdin, self.ssh_stdout, self.ssh_stderr = [[],[],[]]

        print("Sending command:" + cmd)
        self.ssh_stdin, self.ssh_stdout, self.ssh_stderr = self.sftp.sshclient.exec_command(cmd)
        
        err = self.ssh_stderr.readlines();
        out = self.ssh_stdout.readlines();
        if len(err) > 0:
            print("\n\nERROR:\n")
            for row in err:
                print(row)
        else:
            print("\n\nResponse:\n")
            for row in out:
                print(row.replace("\n", ""))

    def get_file(self, remote_path, local_path='./tmp/'):
        tmp_dir = local_path + self.host + "/";
        if(not os.path.isdir(tmp_dir)):
            print("\nCreating directory " + tmp_dir[:-1] + "...")
            os.mkdir(tmp_dir)

        path = remote_path.split('/')
        filename = path[-1]
        print("\nGetting file from remote server:")
        print("\t Remote file: " + remote_path)
        print("\t Local file: " + tmp_dir + filename)
        self.sftp.get(remote_path, tmp_dir + filename)

    def put_file(self, local_path, remote_path='/tmp/'):
        path = local_path.split('/')
        filename = path[-1]
        print("\nPutting file to remote server")
        print("\t Local file: " + local_path)
        print("\t Remote file: " + remote_path + filename)
        self.sftp.put(local_path, remote_path + filename)

    def clone_file(self, source_filename, target_filename, local_path='./tmp/'):
        print("\nCloning file:")
        print("\tSource file: " + local_path + source_filename)
        print("\tTarget file: " + local_path + target_filename)
        cmd = 'cp -a ' + local_path + source_filename + ' ' + local_path + target_filename
        os.system(cmd)

    def close(self):
        self.sftp.close()
        self.ssh.close()