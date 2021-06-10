import config 
from collections import deque
from random import randrange

class node():
    def __init__(self, keys, pt, pr, nt):
        self.keys = keys    # keys 
        self.pt = pt        # pointers
        self.pr = pr        # parent
        self.nt = nt        # next
    
    def __repr__(self):
        w = len(str(max(self.keys)))   # Get max width
        
        result = [str(i).zfill(w) for i in self.keys]
        
        # return str(result)
        return f"{str(result):<20}"

    # def show_attr(self, arg):
    #     if arg == keys:
    #         print("KEYS:")
    #         for k in self.keys:
    #             print(k)


class leaf(node):
    def __init__(self, keys, pt, pr, nt, values):
        super().__init__(keys, pt, pr, nt)
        self.values = values    # values


    # def __repr__(self):
        # return "| K: {} V: {} |".format(self.keys, self.values)
        # return "| K: {} |".format(self.keys)
        # string = "{}".format(self.keys)
        # return f"{string:<13}"

class bplustree():
    def __init__(self, name):
        self.name = name                                  # index name
        self.root = leaf([], [], "root", "none", [])    # root node
        self.depth = 0                                    # depth
        self.max_degree = config.max_degree
        self.min_degree = config.max_degree // 2 


    def find_leaf(self, _key):
        """
        find the leaf node that fits the value range of the passed in value
        """
        cur_node = self.root

        while type(cur_node) is not leaf:
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

    def find_rec(self, _leaf, _key):
        """
        find the actual record with the key
        """
        try:
            return True, _leaf.values[_leaf.keys.index(_key)]
        
        # the key does not exist
        except ValueError:
            return False, "FAIL FINDING RECORD with KEY: {}".format(_key)

    def find_pos(self, _node, _key):
        """
        find the index of parent's pointers pointing to self or the position for insertion
        _node: parent(self) or node being inserted
        _key:  self.keys[0] or inserted key
        """
        for i, key in enumerate(_node.keys):
            if _key < key:
                return i
        
        return -1

    def insert(self, _key, value):
        print(f"{config.bcolors.BOLD}INSERT {config.bcolors.ENDC}" + "KEY: {}, VAL: {} \n".format(_key, value))

        l = self.find_leaf(_key)

        # check duplicate 
        # print(self.find_rec(_key))
        if self.find_rec(l, _key)[0]:
            print("key already exists")
            return 

        

        self.insert_in_leaf(l, _key, value)
        # print(f"{config.bcolors.BOLD}leaf: {config.bcolors.ENDC}", l)

        # split leaf
        if len(l.keys) >= self.max_degree:
            # print(f"{config.bcolors.BOLD}Split Leaf: {config.bcolors.ENDC}")

            new_leaf = leaf([], [], l.pr, l.nt, [])
            l.nt = new_leaf
            for k in range(self.max_degree-self.min_degree):
                new_leaf.keys.insert(0, l.keys.pop(self.max_degree-k-1))
                new_leaf.values.insert(0, l.values.pop(self.max_degree-k-1))

            # print(f"{config.bcolors.BOLD}l_split: {config.bcolors.ENDC}", l)
            # print(f"{config.bcolors.BOLD}newleaf: {config.bcolors.ENDC}", new_leaf)
            
            self.insert_in_parent(l, new_leaf.keys[0], new_leaf)

    def insert_in_leaf(self, _leaf, _key, _value):
        # empty leaf or is the biggest number
        if (not _leaf.keys) or (_leaf.keys[-1] < _key):
            _leaf.keys.append(_key)
            _leaf.values.append(_value)

        else:
            i = self.find_pos(_leaf, _key)
            _leaf.keys.insert(i, _key)
            _leaf.values.insert(i, _value)

    def insert_in_parent(self, _node, _key, _node1):
        # print(f"{config.bcolors.WARNING}insert in parent: {config.bcolors.ENDC}") 

        if _node == self.root:
            self.root = node([_key], [_node, _node1], "root", "none")   # new root
            _node.pr = self.root    # new parent
            _node1.pr = self.root   # new parent
            self.depth += 1
            print(f"{config.bcolors.BOLD}newroot: {config.bcolors.ENDC}", self.root) 
            return

        parent = _node.pr
        # print(f"{config.bcolors.BOLD}parent_before: {config.bcolors.ENDC}", parent)
        # for k in parent.pt:
        #     print(k.keys)
        # insert into parent node
        if parent.keys[-1] < _key:
            parent.keys.append(_key)
            parent.pt.append(_node1)   
        else:
            # for i, key in enumerate(parent.keys):
            #     if _key < key:
            i = self.find_pos(parent, _key)
            parent.keys.insert(i, _key)
            parent.pt.insert(i+1, _node1)

        # print(f"{config.bcolors.BOLD}parent_after: {config.bcolors.ENDC}", parent) 
        # for k in parent.pt:
        #     print(k.keys)

        # split node
        if len(parent.keys) >= self.max_degree:
            new_node = node([], [], parent.pr, parent.nt)
            parent.nt = new_node
            key_ = 0

            for k in range(self.max_degree-self.min_degree):
                new_node.pt.insert(0, parent.pt.pop(self.max_degree-k))
                new_node.pt[0].pr = new_node

                if k == self.max_degree-self.min_degree-1:
                    key_ = parent.keys.pop(self.max_degree-k-1)
                else:
                    new_node.keys.insert(0, parent.keys.pop(self.max_degree-k-1))

            self.insert_in_parent(parent, key_, new_node)


    def delete(self, __key):
        pass

    def delege_entry(self, _node, _key, _pt):
        _node.keys.remove(_key)
        _node.pt.remove(_pt)
        if (_node == self.root) and (len(_node.pt) == 1):
            # There is only one child remaining, making it the new root
            self.root = _node.pt[0]
        
        elif len(_node.keys) < self.min_degree:
            # Too few items to be a node
            i = self.find_pos(_node.pr, _node.keys[0])     # the index of parents pointer pointing to _node
            np = _node.nt                                  # np: neigbor of _node to be coalesced with
            kp = -node.pr.keys[i]                          # kp: key between pointers of _node and np

            # Finding neigbor with enough space for coalescing 
            if (np == "none") or (len(np.nt.keys) + len(_node.keys) + 1 >= self.max_degree):
                # if there is no next node or it lack of enough space for coalescing
                # then np = predecessor(_node)
                np = _node.pr.pt[i-1]
                kp = _node.pr.keys[i-1]

                if (len(np.nt.keys) + len(_node.keys) + 1 >= self.max_degree): 
                    # still lack of enough space
                    np = False

            # swap order
            # making np.nt == _node 
            if _node.nt == np:
                tmp = np
                np = _node
                _node = tmp

            if np:
            # neigbors have enough space for coalescing
                if type(np) is not leaf:
                    for i in range(len(_node.keys)):
                        np.keys.append(_node.keys[i])
                        np.values.append(_node.valuess[i])
                else:
                    _node.keys.insert(0, kp)
                    for i in range(len(_node.pt)):
                        np.pt.append(_node.pt[i])
                        np.keys.append(_node.keys[i])

                np.nt = _node.nt
                self.delete_entry(_node.pr, kp, _node)

            else:
            # neigbors both lack of space for coalescing
            # Redistribution: borrow an entry from np
                if type(np) is leaf:
                    br_val = np.values.pop()    # borrowed value
                    br_key = np.keys.pop()      # borrowed keys
                    _node.val.insert(0, br_val)
                    _node.keys.insert(0, br_key)

                else:
                    br_pt  = np.pt.pop()        # borrowed pointer
                    br_key = np.keys.pop()      # borrowed keys

                    _node.pt.insert(0, br_pt)
                    _node.keys.insert(0, kp)

                # replace kp with br_key 
                _node.rp.keys[:] = [br_key if x==kp else x for x in _node.rp.keys]




    def __repr__(self):
        print("INDEX NAME: {}, DEPTH: {}".format(self.name, self.depth))

        # Enque the first node of each level
        que = deque([])
        curnode = self.root
        que.append(curnode)
        while len(curnode.pt) > 0:
            curnode = curnode.pt[0]
            que.append(curnode)

        for i, n in enumerate(que):
            # PRINT LEVEL INDEX
            print(i, end="\t")

            # PRINT NODE
            p = n.pr
            print("{", end="")
            while n != "none":
                if p != n.pr:
                    p = n.pr
                    print("} {", end="")

                print(n, end="  ")
                n = n.nt
            print("}")

            # END
            if type(n) is leaf:
                break

        # que.append(self.root)
        # # print("<ROOT> ", end="")
        # while len(que) > 0:
        #     if que[0].pt:
        #         for nd in que[0].pt:
        #             que.append(nd)

        #     n = que.popleft()
        #     if n is self.root:
        #         print("P: root ", end="") 
        #     else:
        #         print("P: {} N: {}".format(n.pr.keys[0], n.nt), end="")
        #     print(n)
        
        return "DONE \n"
    


if __name__ == "__main__":

    index = bplustree("test")
    # print(index.find_rec(1))

    for i in range(50):
        index.insert(randrange(99), "hi{}".format(i))
        # print(index)
    print(index)
