import os
import config
import wcwidth
from tabulate import tabulate
from bplus import bplustree, leaf
from catalog import catalog_manager, tables as cat_tables, indices

# store the record file, with pre-created index
ind_tables = {}

class index_manager():
    global ind_tables

    def __init__(self):
        if not os.path.exists(config.index_path):
            os.makedirs(config.index_path)


    def create_table(self, _table):
        ind_tables[_table] = bplustree(_table + "rec")
        # print(ind_tables[_table])
    
    def drop_table(self, _table):
        # clear all the records
        self.delete_rec(_table)
        # delete rec files
        os.remove(config.index_path + _table + "rec.json")
        ind_tables.pop(_table)

    def insert_rec(self, _table, _values):
        self.__load__(_table)

        for i, col in enumerate(cat_tables[_table].attributes):
            if col.d_type == 'i':
                _values[i] = int(_values[i])
            elif col.d_type == 'c':
                _values[i] = _values[i].strip().replace("'", '')
            else:
                _values[i] = float(_values[i])
            # check for unique
            if col.is_unique:
                self.check_unique(_table, i, _values[i])

        record_tree = ind_tables[_table]
        prim_key = cat_tables[_table].primary

        record_tree.insert(_values[prim_key], _values)
        
        print('Successfully insert into table {}\n'.format(_table), end='')
    
    def delete_rec(self, _table, conditions=[]):
        self.__load__(_table)

        if len(conditions) == 0:
            ind_tables[_table] = bplustree(_table + "rec")

            print("Successfully delete all entrys from table '{}'".format(_table))

        # WHERE
        else:
            cons, primary = self.convert_conditions(_table, conditions)
            
            leaves = self.find_leaf_condition(_table, cons[primary]) if primary else self.find_leaf_condition(_table, cons[0])
            
            results = [ val  for _leaf in leaves for val in _leaf.pt if self.check_conditions(val, cons) ]
            
            for rec in results:
                ind_tables[_table].delete(rec[cat_tables[_table].primary])
            
            print("Successfully delete {} entrys from table '{}'".format(len(results), _table))

    def select_rec(self, _table, conditions, atts):
        self.__load__(_table)

        results = []
        
        # WHERE
        # there is WHERE clause
        if conditions != '':
            cons, primary = self.convert_conditions(_table, conditions)
            
            leaves = self.find_leaf_condition(_table, cons[primary]) if primary else self.find_leaf_condition(_table, cons[0])

            results = [ val  for _leaf in leaves for val in _leaf.pt if self.check_conditions(val, cons) ]
        # there is no condition
        else: 
            first_leaf = ind_tables[_table].root
            while type(first_leaf) is not leaf:
                first_leaf = first_leaf.pt[0]
            while first_leaf != "none":
                for rec in first_leaf.pt:
                    results.append(rec)
                
                first_leaf = first_leaf.nt
        
        # PROJECT
        # print(cat_tables)
        att_info = [att.name for att in cat_tables[_table].attributes]
        att_names = att_info

        if atts != '*':
            att_names = [i.strip() for i in atts.split(',')]
            att_index = [att_info.index(i) for i in att_names]

            # project the wanted attributes of records
            results = [ [att for i, att in enumerate(rec) if i in att_index ] for rec in results]
        
        print(tabulate(results, headers=att_names, tablefmt='fancy_grid'))
        print("\n {} records selected".format(len(results)))

    def check_conditions(self, _values, conditions):
        # check given records satisfy passed in conditions
        for con in conditions:
            _value = _values[con[0]]
            if con[1] == '<':
                if not (_value < con[2]):
                    return False
            elif con[1] == '<=':
                if not (_value <= con[2]):
                    return False
            elif con[1] == '>':
                if not (_value > con[2]):
                    return False
            elif con[1] == '>=':
                if not (_value >= con[2]):
                    return False
            elif con[1] == '<>':
                if not (_value != con[2]):
                    return False
            elif con[1] == '=':
                if not (_value == con[2]):
                    return False
            else:
                raise SyntaxError(config.index_where_fail)
        return True

    def convert_conditions(self, _table, conditions):
        # parameters: "a = 8 and b = c and a <> c" 
        # return: [('a', '=', '8'), ('b', '=', 'c'), ('a', '<>', 'c')], primary
        # primary == false, if there is no primary in the conditions, 
        #                   else primary = index of the conditions
        lists = [x for x in conditions.strip().split(' ') if  x!= "and"]
        cons = []
        primary = False
        for i in range(int(len(lists)/3)):
            col_name = lists[3 * i]
            col_index = cat_tables[_table].get_index(col_name)
            
            d_type = cat_tables[_table].attributes[col_index].d_type
            val = lists[3 * i + 2]

            if d_type == 'i':
                val = int(val)
            elif d_type == 'f':
                val = float(val)
            else:
                val.replace("'", '')
            
            if col_index == cat_tables[_table].primary:
                primary = i

            cons.append((col_index, lists[3 * i + 1], val))

        return cons, primary

    def find_leaf_condition(self, _table, con):
        column, condition, value = con[0], con[1], con[2]
        primary_key = cat_tables[_table].primary
        first_leaf =  ind_tables[_table].root

        while type(first_leaf) is not leaf:
            first_leaf = first_leaf.pt[0]

        nodes = []
        if primary_key == column and condition != '<>':
            # kernel: the leaf that satisfy the value
            kernel = ind_tables[_table].find_leaf(value) 

            if condition == '=':
                for val in kernel.pt:
                    if val[column] == value:
                        nodes.append(kernel)
                        break
            elif condition == '<=':
                cur_node = first_leaf
                while cur_node != kernel:
                    nodes.append(cur_node)
                    cur_node = cur_node.nt
                   
                for val in kernel.pt:
                    if val[column] <= value:
                        nodes.append(kernel)
                        break
            elif condition == '<':
                cur_node = first_leaf
                while cur_node != kernel:
                    nodes.append(cur_node)
                    cur_node = cur_node.nt

                for val in kernel.pt:
                    if val[column] < value:
                        nodes.append(kernel)
                        break
            elif condition == '>':
                for val in kernel.pt:
                    if val[column] > value:
                        nodes.append(kernel)
                        break
                while kernel.nt != "none":
                    kernel = kernel.nt
                    nodes.append(kernel)
                    
            elif condition == '>=':
                for val in kernel.pt:
                    if val[column] >= value:
                        nodes.append(kernel)
                        break
                while kernel.nt != "none":
                    kernel = kernel.nt
                    nodes.append(kernel)
            else:
                raise SyntaxError(config.index_where_fail)

        else:
            while first_leaf != "none":
                # linear scan
                for val in first_leaf.pt:
                    if self.check_conditions(val, [con]):
                        nodes.append(first_leaf)
                        break
                
                first_leaf = first_leaf.nt
        return nodes

    def __store__(self):
        for _table in ind_tables.values():
            _table.__store__()

    def check_unique(self, _table, column, value):
        att = cat_tables[_table].attributes

        n = self.find_leaf_condition(_table, [column, '=', value])
        if len(n):
            raise ValueError("Index Module : column '{}' does not satisfy unique constrains.".format(att[column].name))
                                
    def __load__(self, t_name):
        if t_name not in ind_tables.keys():
            print("Loading Table", t_name)
            tree = bplustree(t_name + "rec")
            bplustree.__load__(t_name + "rec", tree)
            ind_tables[t_name] = tree

    def __finalize__(self):
        self.__store__()

if __name__ == "__main__":

    i = index_manager()

    i.create_table("test")
    print(ind_tables)
