import config 

class node():
    def __init__(self, keys, pt, pr):
        self.keys = keys    # keys 
        self.pt = pt        # pointers
        self.pr = pr        # parent

    def __repr__(self):
        return "NODE.. KEYS: {}".format(self.keys)

class leaf(node):
    def __init__(self, keys, pt, pr, values):
        super().__init__(keys, pt, pr)
        self.values = values    # values


    def __repr__(self):
        return "LEAF.. KEYS: {} VAL: {}".format(self.keys, self.values)


class bplustree():
    def __init__(self, name):
        self.name = name                          # index name
        self.root = leaf([], [], "root", [])      # root node
        self.depth = 0                            # depth
        self.max_degree = config.max_degree
        self.min_degree = config.max_degree // 2 


    def find_leaf(self, _key):
        """
        find the leaf node that fits the value range of the passed in value
        """
        cur_node = self.root

        while type(cur_node) is not leaf:
            # print("fk")
            flag = True
            for i, key in enumerate(cur_node.keys):
                if key > _key:
                    cur_node = cur_node.pt[i]
                    flag = False
                    break
            
            # the value passed in is greater than all the keys in this node
            if flag:
                cur_node = cur_node.pt[-1]

        return cur_node

    def find_rec(self, _key):
        """
        find the actual record with the key
        """
        leaf = self.find_leaf(_key)
        try:
            return leaf.values[leaf.keys.index(_key)]
        
        # the key does not exist
        except ValueError:
            return False, "FAIL FINDING RECORD with KEY: {}".format(_key)


    def insert(self, _key, value):
        print("inserting KEY: {}, VAL: {} \n".format(_key, value))
        l = self.find_leaf(_key)

        self.insert_in_leaf(l, _key, value)
        print(f"{config.bcolors.BOLD}leaf: {config.bcolors.ENDC}", l)

        if len(l.keys) >= self.max_degree:
            new_leaf = leaf([], [], l.pr, [])

            for k in range(self.max_degree-self.min_degree-1):
                new_leaf.keys.insert(0, l.keys.pop(self.max_degree-k-1))
                new_leaf.values.insert(0, l.values.pop(self.max_degree-k-1))

            print(f"{config.bcolors.BOLD}l_split: {config.bcolors.ENDC}", l)
            print(f"{config.bcolors.BOLD}newleaf: {config.bcolors.ENDC}", new_leaf)
            
            self.insert_in_parent(l, new_leaf.keys[0], new_leaf)

    def insert_in_leaf(self, _leaf, _key, _value):
        # empty leaf
        if not _leaf.keys:
            _leaf.keys.append(_key)
            _leaf.values.append(_value)
            return 

        if _leaf.keys[-1] < _key:
            _leaf.keys.append(_key)
            _leaf.values.append(_value)
        else:
            for i, key in enumerate(_leaf.keys):
                if key < _key:
                    leaf.keys.insert(i, _key)
                    leaf.values.insert(i, _value)

    def insert_in_parent(self, _node, _key, _node1):
        if _node == self.root:
            self.root = node([_key], [_node, _node1], "root")   # new root
            _node.pr = self.root    # new parent
            _node1.pr = self.root   # new parent
            self.depth += 1
            return

        parent = _node.pr
        for i, key in range(len(parent.keys)):
            if _node.keys[0] < key:
                parent.keys.insert(i, _key)
                parent.pt.insert(i, _node)
                break

        # split node
        if len(parent.keys) >= self.max_degree:
            new_node = node(pr=parent.pr)
            key_ = 0

            for k in range(self.max_degree-self.min_degree-1):
                new_node.pt.insert(0, parent.pt.pop(self.max_degree-k))

                if k == self.max_degree-self.min_degree-1:
                    key_ = parent.keys.pop(self.max_degree-k)
                else:
                    new_node.keys.insert(0, parent.keys.pop(self.max_degree-k))
            
            self.insert_in_parent(parent, key_, new_node)



    def delete(self, __key):
        pass
    
    def __repr__(self):
        que = []
        que.append(self.root)
        print(len(que))
        # print(self.root.pt)
        # while len(que) > 0:
        for i in range(2):
            # if pointers exist
            if que[0].pt:
                for nd in que[0].pt:
                    que.append(nd)

            print(que.pop().pt)
        
        return "DONE \n"
    


# a = node([2, 4, 4])
# b = leaf([2, 4, 4], [2, 4, 7])
# print(b.keys, b.values)

if __name__ == "__main__":

    index = bplustree("test")
    print(index.find_rec(1))

    index.insert(1, "hi")
    print(index)
    index.insert(2, "cys")
    print(index)
    index.insert(3, "freaky")
    print(index)
    index.insert(4, "hi")
    print(index)
