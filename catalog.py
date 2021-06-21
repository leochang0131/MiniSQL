import re
import os
import json
import bplus
import config
from basic_class import table, column

tables = {}
indices = {}

class catalog_manager():

    def __initialize__(self):
        if not os.path.exists(config.catalog_path):
            os.makedirs(config.catalog_path)

            tables["sys"] = table('sys', 0)
            indexs["sys_default_index"] = {'table':'sys', 'column':'username'}
            columns = []
            columns.append(column('username',True))
            columns.append(column('password', False))
            tables["sys"].attributes = columns
            __store__()

        __load__()

    def create_table(self, statement):
        # find primary key
        pri_st = re.search('primary key *\(',statement).end()
        pri_ed = re.search('\)',statement[pri_st:]).start()
        primary_key = statement[pri_st:][:pri_ed].strip()

        # replace multiple spaces with single one 
        statement = re.sub(' +', ' ', statement)

        # getting attributes info
        atts = [x.strip().split(' ') for x in statement.split(',')]
        t_name = atts[0][2]
        atts[0][:] = atts[0][4:]
        
        colu = []
        for attr in atts[:-1]:
            u = False
            name = attr[0]
            length = 0
            d_type = 'c'

            if "unique" in attr:
                u = True

            if "int" in attr[1]:
                d_type = 'i'
            elif "float" in attr[1]:
                d_type = 'f'
            elif "char"  in attr[1]:
                d_type = 'c'
                length = int(attr[1][5:-1])
            else:
                raise NameError("Catalog Module : Unknow datatype ", attr[1])
            
            colu.append(column(name, u, d_type, length))
        
        primary = -1
        for i, col in enumerate(colu):
            if primary_key == col.name:
                primary = i
                break
        
        if primary == -1:
            raise ValueError("Catalog Module : Primary Key, no such attribute ", primary_key)
        else:
            global tables
            tables[t_name] = table(t_name, colu, primary)

    def drop_table(self, table):
        tables.pop(table)

    def create_index(self, index_name, table, column):
        indices[index_name] = { "table": table, "column": column }

    def drop_index(self, index):
        indices.pop(index)

    def __store__(self):
        _tables = {}
        for t in tables.items():
            _def = {}
            _def["pri_k"] = t[1].primary
            _columns = {}
            for i in t[1].attributes:
                _columns[i.name] = (i.is_unique, i.d_type, i.length)
            
            _def["columns"] = _columns
            _tables[t[0]] = _def
        
        with open(config.catalog_path + "tables.json", "w") as f:
            f.writelines(json.dumps(_tables, indent=2))

        with open(config.catalog_path + "indices.json", "w") as f:
            global indices
            f.writelines(json.dumps(indices, indent=2))

    @staticmethod
    def __load__():
        with open(config.catalog_path + "tables.json", "r") as f:
            t = json.load(f)
            for tab in t.items():
                _table = table(tab[0], tab[1]["pri_k"])

                colu = []
                for _column in tab[1]["columns"].items():
                    colu.append(column(_column[0], _column[1][0], _column[1][1], _column[1][2]))
                                        
                _table.attributes = colu
                tables[tab[0]] = _table

        with open(config.catalog_path + "indices.json", "r") as f:
            global indices
            indices = json.load(f)

    def select_check(self, _table, conditions, cols):
        # Check the attributes in SELECT clause 
        # Where
        columns = [c.name for c in tables[_table].attributes]
        if conditions != '':
            lists = re.sub('and|or', ',', conditions).split(',')
            for i in lists:
                col_name = i.strip().split(' ')[0]
                if col_name not in columns:
                    raise AttributeError("Catalog Module : no such column {}".format(col_name))
        
        # Project
        if cols != '*':
            for i in cols.split(','):
                if i.strip() not in columns:
                    raise AttributeError("Catalog Module : no such column {}".format(col_name))

    def insert_check(self, _table, values):
        tab = tables[_table]
        if len(tab.attributes) != len(values):
            raise ValueError("Catalog Module : table '%s' has %d atts" % (_table, len(tab.attributes)))
                            
        for i, att in enumerate(tab.attributes):
            
            if att.d_type == 'c' and len(values[i]) > att.length:
                raise ValueError("Catalog Module : table '{}' : column '{}' 's length "
                                 "can't be longer than {}.".format(_table, att.name, att.length)) 

            if att.is_unique:
                if att.d_type == 'i': value = int(values[i])
                    
                elif att.d_type == 'f': value = float(values[i])
                    
                else: value = values[i]
                    
                IndexManager.index.check_unique(_table, i, value)

    def exist_table(self, _table, t):
        # check whether the table exists, and raise error according to 't'
        # t = True: check table duplication
        # t = False: check table existence
        global tables
        if _table in tables.keys() and t:
            raise ValueError("Catalog Module : table {} already exists".format(_table))
        
        elif _table not in tables.keys() and not t:
            raise ValueError("Catalog Module : table {} not exists".format(_table))

    def exist_index(self, _index, t):
        # check whether the table exists, and raise error according to 't'
        # t = True: check table duplication
        # t = False: check table existence
        global indices
        if _index in indices.keys() and t:
            raise ValueError("Catalog Module : index {} already exists".format(_index))
        
        elif _index not in indices.keys() and not t:
            raise ValueError("Catalog Module : index {} not exists".format(_index))




statement = "create table student (\
             sno char(8),\
             sname char(16) unique,\
             sage int,\
             sgender char(1),\
             primary key(sno)\
            );"


a = catalog_manager()
# a.create_table(statement)
# a.create_index("student_test", "student", "primary")
a.__load__()



# a.__store__()