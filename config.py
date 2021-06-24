# Color
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# login
errortext = '''
    MiniSQL -u [username] -p [password] (optional)-execfile [filename]
    \tLogin operators : 
    \t\t-u username\tusername for MiniSQL.
    \t\t-p password\tpassword for MiniSQL.\n
    \tExecute SQL file operators : 
    \t\t-execfile filename\tSQL filename to be executed for MiniSQL.
    '''
banner = "MiniSQL database server, version 1\n" \
         "Copyright 2018 @ ZLQ from ZJU.\n"\
         "These shell commands are defined internally.  Type `help' to see this list.\n"\
         "Type `help cmd' to find out more about the function `cmd'.\n"

# Path
root = "./data/"
catalog_path = root + "catalog/"
index_path = root + "index/"

# System
root_user = "root"
root_pswd = "123456"
prompt = "### "

# Index
index_where_fail = "Index Module : unsupported op."

# Bplus
max_degree = 10  # max degree of bplus tree

nodedis_w = 13 # the node width for bplus tree visualization