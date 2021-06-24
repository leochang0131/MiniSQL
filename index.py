import os
import config
import wcwidth
from tabulate import tabulate
from bplus import bplustree, leaf
from catalog import catalog_manager, tables as cat_tables, indices as cat_indices

# store the record file, with pre-created index
ind_tables = {}

class index_manager():
    global ind_tables

    def __init__(self):
        pass
        # if not os.path.exists(config.index_path):
        #     os.makedirs(config.index_path)

    def create_table(self, _table):
        ind_tables[_table] = bplustree(_table + "rec")
    
    def drop_table(self, _table):
        # clear all the records
        self.delete_rec(_table)
        # delete rec file
        os.remove(config.index_path + _table + "rec.json")
        ind_tables.pop(_table)

    def create_index(self, _index, _table):
        # value of index would be the primary key of the table
        ind_tables[_index] = bplustree("{}_{}".format(_index, _table))

        recs = self.get_all_rec(_table)

        col = cat_indices[_index]["column"]

        for rec in recs:
            ind_tables[_index].insert(rec[col], rec[int(cat_tables[_table].primary)])  


    def drop_index(self, _index, _table):
        # delete index file
        os.remove(config.index_path + "{}_{}".format(_index, _table)+ ".json")
        ind_tables.pop(_index)

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

        # insert into record file
        record_tree.insert(_values[prim_key], _values)

        # insert into index file
        for _index in cat_indices.items():
            if _index[1]["table"] == _table:
                ind_tables[_index[0]].insert(_values[_index[1]["column"]], _values[prim_key]) 
        
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

                for _index in cat_indices.items():
                    if _index[1]["table"] == _table:
                        ind_tables[_index[0]].delete(rec[_index[1]["column"]]) 
            
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
            results = self.get_all_rec(_table)
        
        # PROJECT
        # print(cat_tables)
        att_info = [att.name for att in cat_tables[_table].attributes]
        att_names = att_info

        if atts != '*':
            att_names = [i.strip() for i in atts.split(',')]
            att_index = [att_info.index(i) for i in att_names]

            # project the wanted attributes of records
            results = [ [ att for i, att in enumerate(rec) if i in att_index ] for rec in results]
        
        print(tabulate(results, headers=att_names, tablefmt='fancy_grid'))
        print("\n {} records selected".format(len(results)))

    def chech_user(self, user, pswd):
        self.__load__("sys")
        cons = [(0 , '=', user), (1, '=', pswd)]
        leaves = self.find_leaf_condition("sys", cons[0]) 
        
        results = [ val  for _leaf in leaves for val in _leaf.pt if self.check_conditions(val, cons) ]

        return True if len(results) != 0 else False


    def __load_i__(self, t_name):
    # load index
    for _index in cat_indices.items():
        if _index[1]["table"] == t_name:
            ind_tree = bplustree("{}_{}".format(_index[0], t_name))
            bplustree.__load__("{}_{}".format(_index[0], t_name), ind_tree)
            ind_tables[_index[0]] = ind_tree

    def __load__(self, t_name):
        if t_name not in ind_tables.keys():
            # load table rec
            print("Loading Table", t_name)
            tree = bplustree(t_name + "rec")
            bplustree.__load__(t_name + "rec", tree)
            ind_tables[t_name] = tree

            
    def __store__(self):
        for _table in ind_tables.values():
            _table.__store__()

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

    def check_conditions(self, _values, conditions):
        # check each records in the given leaves with conditions
        # return the list of satisfied records
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

    def check_unique(self, _table, column, value):
        att = cat_tables[_table].attributes

        n = self.find_leaf_condition(_table, [column, '=', value])
        if len(n):
            raise ValueError("Index Module : column '{}' does not satisfy unique constrains.".format(att[column].name))

    def get_all_rec(self, _table):
        self.__load__(_table)

        first_leaf = ind_tables[_table].root
        results = []
        while type(first_leaf) is not leaf:
            first_leaf = first_leaf.pt[0]
        while first_leaf != "none":
            for rec in first_leaf.pt:
                results.append(rec)
            
            first_leaf = first_leaf.nt
        
        return results

    def __finalize__(self):
        self.__store__()

if __name__ == "__main__":

    i = index_manager()

    i.create_table("test")
    print(ind_tables)
