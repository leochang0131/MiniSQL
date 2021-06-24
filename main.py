import os
import cmd
import api
import sys
import time
import index
import config
import catalog

time_prompt = "time elapsed (s) : "
class miniSQL(cmd.Cmd):
    global time_prompt
    intro = 'Welcome to the MiniSQL database server.\nType help or ? to list commands.\n'

    def do_show(self, args):
        api.show_tables()

    def do_select(self,args):
        # api.select(args.replace(';', ''))
        try:
            print(time_prompt, api.select(args.replace(';','')))
        except Exception as e:
            print(str(e))

    def do_create(self,args):
        try:
            print(time_prompt, api.create(args.replace(';','')))
        except Exception as e:
            print(str(e))

        # api.create(args.replace(';',''))
    def do_drop(self,args):
        try:
            print(time_prompt, api.drop(args.replace(';','')))
        except Exception as e:
            print(str(e))

    def do_insert(self,args):
        try:
            print(time_prompt, api.insert(args.replace(';','')))
        except Exception as e:
            print(str(e))
        # api.insert(args.replace(';',''))

    def do_delete(self,args):
        try:
            print(time_prompt, api.delete(args.replace(';','')))
        except Exception as e:
            print(str(e))

    def do_commit(self,args):
        time_start = time.time()
        api.__finalize__()
        time_end = time.time()
        print('Modifications has been commited to local files')
        print("time elapsed : %fs." % (time_end - time_start))

    def do_quit(self,args):
        api.__finalize__()
        print('Goodbye.')
        sys.exit()

    def emptyline(self):
        # none
        pass

    def default(self, line):
        print('Unrecognized command.\nNo such symbol : %s' % line)

    def help_commit(self):
        print()
        text = "To reduce file transfer's time, this SQL server is designed to "+\
        "'lasy' write changes to local files, which means it will not store changes "+\
        "until you type 'quit' to normally exit the server. if this server exit "+\
        "unnormally, all changes will be lost. If you want to write changes to "+\
        "local files immediately, please use 'commit' command.\n"
        print(text)

    def help_quit(self):
        print()
        print('Quit the program and write changes to local file.')

    def help_select(self):
        print()
        print("select * from student;")
        print("select num from student where num >= 2 and num < 10 and gender = 'male';")

    def help_create(self):
        print()
        print("create table student (ID int, name char(10),gender char(10)"
              ",enroll_date char(10),primary key(ID));")

    def help_drop(self):
        print()
        print("drop table student;")

    def help_insert(self):
        print('''
                insert into student values ( 1,'Alan','male','2017.9.1');
                insert into student values ( 2,'rose','female','2016.9.1');
                insert into student values ( 3,'Robert','male','2016.9.1');
                insert into student values ( 4,'jack','male','2015.9.1');
                insert into student values ( 5,'jason','male','2015.9.1');
                insert into student values ( 6,'Hans','female','2015.9.1');
                insert into student values ( 7,'rosa','male','2014.9.1');
                insert into student values ( 8,'messi','female','2013.9.1');
                insert into student values ( 9,'Neymar','male','2013.9.1');
                insert into student values ( 10,'Christ','male','2011.9.1');
                insert into student values ( 11,'shaw','female','2010.9.1');
            ''')

    def help_delete(self):
        print()
        print("delete from students")
        print("delete from student where sno = '88888888';")

def exec_from_file(filename):
    start = time.time()
    with open(filename, "r") as f:
        lines = f.readlines()

    commands = [line.strip().replace('\n','')[:-1] for line in lines]
    for cmd in commands:
        if cmd == '':
            continue
        if cmd[0] == '#':
            continue
        if cmd.split(' ')[0] == 'insert':
            try:
                api.insert(cmd[6:])
            except Exception as e:
                print(str(e))
            # api.insert(cmd[6:])
        elif cmd.split(' ')[0] == 'select':
            try:
                api.select(cmd[6:])
            except Exception as e:
                print(str(e))
        elif cmd.split(' ')[0] == 'delete':
            try:
                api.delete(cmd[6:])
            except Exception as e:
                print(str(e))
        elif cmd.split(' ')[0] == 'drop':
            try:
                api.drop(cmd[4:])
            except Exception as e:
                print(str(e))
        elif cmd.split(' ')[0] == 'create':
            try:
                api.create(cmd[6:])
            except Exception as e:
                print(str(e))
    end = time.time()
    print(time_prompt, end-start)
    api.__finalize__()




if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('ERROR : Unsupported syntax, please login.\n', config.errortext)
        sys.exit()

    if sys.argv[1] != '-u' or sys.argv[3] != '-p':
        print('ERROR : Unsupported syntax, please login.\n', config.errortext)
        sys.exit()


    if sys.argv[2] == config.root_user and sys.argv[4] == config.root_pswd:
        api.__root = True
    # elif IndexManager.index.exist_user(username=sys.argv[2],password=sys.argv[4]):
    #     api.__root = False
    else:
        print('Error : username or password is not correct.\n', config.errortext)
        sys.exit()

    if len(sys.argv) > 5:
        if sys.argv[5] != "-execfile":
            print('ERROR : Unsupported syntax.\n', config.errortext)

        exec_from_file(sys.argv[6])
        sys.exit()

    print(config.banner)

    miniSQL.prompt = "<{}> {}".format(sys.argv[2], config.prompt)
    miniSQL().cmdloop()

