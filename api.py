import re
import catalog
import index
import time

__root = True

catalog_manager = catalog.catalog_manager()
index_manager = index.index_manager()

def show_tables():
    for _table in catalog.tables.values():
        print(_table)

def select(args):
    time_start = time.time()

    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    start_from = re.search("from", args).start()
    end_from = start_from + 4

    columns = args[0 : start_from].strip()

    if re.search('where', args):
        start_where = re.search('where', args).start()
        end_where = start_where + 4
        table = args[end_from : start_where].strip()
        conditions = args[end_where + 1 : ].strip()
    else:
        table = args[end_from + 1 : ].strip()
        conditions = ''

    catalog_manager.exist_table(table, False)
    catalog_manager.select_check(table, conditions, columns)

    index_manager.select_rec(table, conditions, columns)

    time_end = time.time()
    return time_end - time_start

def create(args):
    time_start = time.time()

    args = re.sub(r' +', ' ', args).strip().replace('\u200b', '')
    lists = args.split(' ')
    if lists[0] == "table":
        start_on = re.search('table', args).end()
        start = re.search('\(', args).start()
        table = args[start_on : start].strip()

        catalog_manager.exist_table(table, True)
        catalog_manager.create_table(table, args)
        index_manager.create_table(table)
        print("Successfully create table '{}'".format(table))

    elif lists[0] == "index":
        index_name = lists[1]

        if lists[2] != 'on':
            raise SyntaxError("API Module : Unrecoginze arguments for command 'create index'.")
        
        start_on = re.search('on',args).start()
        start = re.search('\(', args).start()
        end = find_last(args, ')')
        table = args[start_on : start].strip()
        column = args[start + 1 : end].strip()
        
        catalog_manager.exist_index(index_name, True)
        catalog_manager.create_index(index_name, table, column)
        # IndexManager.index.create_index(index_name,table,column)
        print("Successfully create index '{}'".format(index_name))

    else:
        raise SyntaxError("API Module : Unrecoginze arguments for command 'create', it should be 'table' or 'index'.")
    
    time_end = time.time()
    return time_end - time_start 

def drop(args):
    time_start = time.time()
    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')

    if args[0 : 5] == "table":
        table = args[6 : ].strip()
        if table == "sys":
            raise ValueError("ERROR : Can't delete 'sys' table.")

        catalog_manager.exist_table(table, False)
        catalog_manager.drop_table(table)
        index_manager.drop_table(table)
        print("Successfully delete table '{}'.".format(table))
        

    elif args[0:5] == "index":
        index = args[6:].strip()
        catalog_manager.exist_index(index, False)
        catalog_manager.drop_index(index)
        print("Successfully delete index '{}'.".format(index))

    else:
        raise SyntaxError("API Module : Unrecoginze symbol for command 'drop',it should be 'table' or 'index'.")
    
    time_end = time.time()
    return time_end - time_start

def insert(args):
    time_start = time.time()

    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    args = re.sub('[()\',]', '', args)
    lists = args.split(' ')
    
    if lists[0] != "into":
        raise SyntaxError("API Module : Unrecoginze symbol for command 'insert',it should be 'into'.")

    table = lists[1]
    if table == "sys" and __root:
        raise ValueError("ERROR : Can't modify 'sys' table, you don't have root permission.")

    if lists[2] != "values":
        raise SyntaxError("API Module : Unrecoginze symbol for command 'insert',it should be 'values'.")
    
    catalog_manager.exist_table(table, False)
    catalog_manager.insert_check(table, lists[3 : ])
    index_manager.insert_rec(table, lists[3 : ])

    time_end = time.time()
    return time_end - time_start

def delete(args):
    time_start = time.time()

    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    lists = args.split(' ')
    if lists[0] != "from":
        raise SyntaxError("API Module : Unrecoginze symbol for command 'delete', it should be 'from'.")
    
    table = lists[1]
    if table == "sys" and __root:
        raise ValueError("ERROR : Can't modify 'sys' table, you don't have root permission.")

    catalog_manager.exist_table(table, False)
    index_manager.delete_rec(table) if len(lists) == 2 else index_manager.delete_rec(table, " ".join(lists[3:]))

    time_end = time.time()
    return time_end - time_start

def find_last(string, str):
    last_position = -1
    while True:
        position = string.find(str, last_position+1)
        if position == -1:
            return last_position
        last_position = position

def __finalize__():
    catalog_manager.__finalize__()
    index_manager.__finalize__()

if __name__ == "__main__":
    sct = "asdf asdf from student where a = 8 and b = c"
    print("hi")
    select(sct)