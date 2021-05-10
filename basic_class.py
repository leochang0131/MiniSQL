class table():
    def __init__(self, name, attributes, primary = 0):
        # table_name
        # index of attribute of primary key
        # array of column instances
        self.name = name
        self.primary = primary
        self.attributes = attributes

class column():
    def __init__(self, name, is_unique, d_type, length):
        # column_name
        # is_unique = true or false
        # data_type = 'int', 'float', 'char(n)'
        # length = number of characters
        self.name = name
        self.is_unique = is_unique
        self.d_type = d_type
        self.length = length





if __name__ == "__main__":
    pass
