import config
import random
import json 
import math
from collections import deque

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

class leaf(node):
    def __init__(self, keys, pt, pr, nt):
    
        super().__init__(keys, pt, pr, nt)
        # pt now points to value

class bplustree():
    def __init__(self, name, depth=0, max_degree=config.max_degree, min_degree=config.max_degree//2):
        self.name = name                                  # index name
        self.root = leaf([], [], "root", "none")          # root node
        self.depth = depth                                # depth
        self.max_degree = config.max_degree
        self.min_degree = config.max_degree // 2 

    def replace_index(self, _key):
        """
        replace the _key with the smallest key of right child
        """
        cur_node = self.root
        while type(cur_node) is not leaf:
            if _key in cur_node.keys:
                # replace the internal node
                i = cur_node.keys.index(_key)
                tmp = cur_node.pt[i+1]          # right child

                while type(tmp) is not leaf:
                    tmp = tmp.pt[0]
                
                cur_node.keys[i] = tmp.keys[0]
                return True

            flag = True
            for i, key in enumerate(cur_node.keys):
                if key > _key:
                    cur_node = cur_node.pt[i]
                    flag = False
                    break
            
            # the value passed in is greater than all the keys in this node
            if flag:
                cur_node = cur_node.pt[-1]

        return False

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
            return True, _leaf.pt[_leaf.keys.index(_key)]
        
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
        
        return len(_node.pt)-1

    def insert(self, _key, value):
        print(f"{config.bcolors.BOLD}INSERT {config.bcolors.ENDC}" + "KEY: {}, VAL: {} \n".format(_key, value))

        l = self.find_leaf(_key)

        # check duplicate 
        if self.find_rec(l, _key)[0]:
            print("key already exists")
            return 

        self.insert_in_leaf(l, _key, value)

        # split leaf
        if len(l.keys) >= self.max_degree:
            new_leaf = leaf([], [], l.pr, l.nt)
            l.nt = new_leaf

            mid = int(math.ceil(self.max_degree / 2)) - 1
            new_leaf.keys = l.keys[mid + 1 : ]
            new_leaf.pt = l.pt[mid + 1 : ]
            l.keys = l.keys[ : mid + 1]
            l.pt = l.pt[ : mid + 1]
            
            self.insert_in_parent(l, new_leaf.keys[0], new_leaf)

    def insert_in_leaf(self, _leaf, _key, _value):
        # empty leaf or is the biggest number
        if (not _leaf.keys) or (_leaf.keys[-1] < _key):
            _leaf.keys.append(_key)
            _leaf.pt.append(_value)

        else:
            i = self.find_pos(_leaf, _key)
            _leaf.keys.insert(i, _key)
            _leaf.pt.insert(i, _value)

    def insert_in_parent(self, _node, _key, _node1):
        # print(f"{config.bcolors.WARNING}insert in parent: {config.bcolors.ENDC}") 

        if _node == self.root:
            self.root = node([_key], [_node, _node1], "root", "none")   # new root
            _node.pr = self.root    # new parent
            _node1.pr = self.root   # new parent
            self.depth += 1
            # print(f"{config.bcolors.BOLD}newroot: {config.bcolors.ENDC}", self.root) 
            return

        parent = _node.pr
        if parent.keys[-1] < _key:
            parent.keys.append(_key)
            parent.pt.append(_node1)   
        else:
            i = self.find_pos(parent, _key)
            parent.keys.insert(i, _key)
            parent.pt.insert(i+1, _node1)

        # split node
        if len(parent.pt) > self.max_degree:
            new_node = node([], [], parent.pr, parent.nt)
            parent.nt = new_node

            mid = int(math.ceil(self.max_degree / 2)) - 1

            new_node.pt = parent.pt[mid + 1 :]
            new_node.keys = parent.keys[mid + 1 : ]
            key_ = parent.keys[mid]

            parent.keys = parent.keys[ : mid + 1] if mid == 0 else parent.keys[ : mid]
            parent.pt = parent.pt[ : mid + 1]

            for child in parent.pt:
                child.pr = parent
            for child in new_node.pt:
                child.pr = new_node

            self.insert_in_parent(parent, key_, new_node)

    def delete(self, _key):
        print(f"{config.bcolors.BOLD}DELETE {config.bcolors.ENDC}" + "KEY: {}\n".format(_key))
        l = self.find_leaf(_key)
        v = self.find_rec(l, _key)

        if v[0]:
            self.delete_entry(l, _key, v[1])
            self.replace_index(_key)
            return True
        else:
            print("No such key {}".format(_key))
            return False

    def delete_entry(self, _node, _key, _pt):
        _node.keys.remove(_key)
        _node.pt.remove(_pt)

        if (_node == self.root) and (len(_node.pt) == 1) and self.depth != 0:
            # There is only one child remaining, making it the new root
            self.root = _node.pt[0]
            self.depth -= 1
            del _node

        elif (_node != self.root) and len(_node.keys) < self.min_degree-1:
            # Too few items to be a node
            is_prev = True
            parentNode = _node.pr
            PrevNode = False
            NextNode = False
            PrevK = False
            PostK = False
            
            i = self.find_pos(_node.pr, _key)              # the index of parents pointer pointing to _node
            if i > 0:
                PrevNode = parentNode.pt[i - 1]
                PrevK = parentNode.keys[i - 1]

            if i < len(parentNode.pt) - 1:
                NextNode = parentNode.pt[i + 1]
                PostK = parentNode.keys[i]
            
            # np: neighbor chosen to be borrowed or coalesced
            # kp: key between pointers of _node and np
            (np, kp, is_prev) = (PrevNode, PrevK, True) if PrevNode else (NextNode, PostK, False)
            
            # First consider borrow
            if len(np.keys) >= self.min_degree or (is_prev and PostK and len(NextNode.keys) >= self.min_degree):
                if len(np.keys) < self.min_degree:
                    np, kp, is_prev = NextNode, PostK, False

                if is_prev:
                    if type(np) is leaf:
                        br_val = np.pt.pop()        # borrowed value
                        br_key = np.keys.pop()      # borrowed keys
                        _node.pt.insert(0, br_val)
                        _node.keys.insert(0, br_key)
                    else:
                        br_pt  = np.pt.pop()        # borrowed pointer
                        br_key = np.keys.pop()      # borrowed keys
                        _node.pt.insert(0, br_pt)
                        _node.keys.insert(0, kp)

                    # replace kp with br_key 
                    _node.pr.keys[:] = [br_key if x==kp else x for x in _node.pr.keys] 
                
                else:
                    if type(np) is leaf:
                        br_val = np.pt.pop(0)       # borrowed value
                        br_key = np.keys.pop(0)     # borrowed keys
                        _node.pt.append(br_val)
                        _node.keys.append(br_key)
                        new_key = np.keys[0]
                    else:
                        br_pt  = np.pt.pop(0)       # borrowed pointer
                        new_key = np.keys.pop(0)    # borrowed keys
                        _node.pt.append(br_pt)
                        _node.keys.append(kp)

                    # replace kp with new_key 
                    _node.pr.keys[:] = [new_key if x==kp else x for x in _node.pr.keys] 

                if type(np) is not leaf:
                    for child in np.pt:
                        child.pr = np
                if type(_node) is not leaf:
                    for child in _node.pt:
                        child.pr = _node
                if type(parentNode) is not leaf:
                    for child in parentNode.pt:
                        child.pr = parentNode
            # Then condider coalescing 
            else:
                # making np.nt = _node
                if kp == PostK:
                    np, _node = _node, np

                if type(np) is not leaf:
                    _node.keys.insert(0, kp)

                np.keys += _node.keys
                np.pt += _node.pt 
                
                if type(np) is not leaf:
                    for child in np.pt:
                        child.pr = np

                np.nt = _node.nt
                self.delete_entry(_node.pr, kp, _node)
                del _node

    def __repr__(self):
        print("INDEX NAME: {}, DEPTH: {}, Max-De: {}\n".format(self.name, self.depth, self.max_degree))

        if not self.root.keys:
            print("empty")
        else:
            # Enque the first node of each level
            que = deque([])
            curnode = self.root
            que.append(curnode)

            for i in range(self.depth):
            # while type(curnode) is not leaf:
                curnode = curnode.pt[0]
                que.append(curnode)

            for i, n in enumerate(que):
                # PRINT LEVEL INDEX
                print(i, end="     ")

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
        
        return "\n" + self.name + "---\n"
    
    def __store__(self):
        index = {}
        nodes = []

        index["name"] = self.name
        index["depth"] = self.depth
        index["max_degree"] = self.max_degree

        # Enque the first node of each level
        que = deque([])
        curnode = self.root
        que.append(curnode)

        for i in range(self.depth):
            curnode = curnode.pt[0]
            que.append(curnode)

        for i, n in enumerate(que):
            p = n.pr    # check whether belongs to different parents
            pr_i = 0    # index indicates parent
            flag = True if type(n) is leaf else False

            while n != "none":
                _node = {}

                # check parents
                if p != n.pr:
                    p = n.pr
                    pr_i += 1

                # store node
                _node["d"] = i          # depth
                _node["k"] = n.keys     # keys
                _node["n"] = 0 if n.nt == "none" else 1 # next: if its the last one in the level, set 0
                _node["r"] = pr_i       # parent·
                if flag:
                    _node["v"] = n.pt   # only leaf node will store the values(pointers)

                nodes.append(_node)
                n = n.nt

        index["nodes"] = nodes

        with open(config.index_path + "{}.json".format(self.name), "w") as f:
            # print(json.dumps(index, indent=2))
            f.writelines(json.dumps(index, indent=2))

    @staticmethod
    def __load__(name, newtree):
        with open(config.index_path + "{}.json".format(name), "r") as f:
            j = json.load(f)
        
        lvl = 0             # number of nodes in current level
        flag = True         # is leaf
        nodes = ["root"]    # nodes
        pointers = []       # the pair of indices of each parent and child
        bplus_info = [0]    # the index of first node of each level

        for i, _node in enumerate(j["nodes"]):
            if flag and ("v" in _node):
                flag = False

            pr_i = lvl+int(_node["r"])
            if i > 0:
                pointers.append((pr_i, i+1))          

            new_node = node(_node["k"], [], nodes[pr_i], "") if flag else leaf(_node["k"], _node["v"], nodes[pr_i], "")
            # assign leaf's values(pt) and all nodes' keys and parents
            nodes.append(new_node)
            
            # assign nodes' next
            if i > 1:
                nodes[i-1].nt = nodes[i] if j["nodes"][i-2]["n"] == 1 else "none"
        
            if _node["n"] == 0:
                lvl = bplus_info[-1]+1
                bplus_info.append(i+1) 

        nodes[-2].nt = nodes[-1]
        nodes[-1].nt = "none"

        # assign pointers for internal nodes
        for pr_i, ch_i in pointers:
            nodes[pr_i].pt.append(nodes[ch_i]) 

        newtree.__init__(j["name"], j["depth"], int(j["max_degree"]), int(j["max_degree"])//2)
        newtree.max_degree = int(j["max_degree"])
        newtree.min_degree = int(j["max_degree"])//2
        newtree.root = nodes[1]

        
# test
if __name__ == "__main__":

    index = bplustree("test")

    for i in range(2000):
        index.insert(i, "hi%d"%(i))
    try:
        for i in range(2000):
            if i % 500 == 0:
                print(index)
            index.delete(i)
    except Exception:
        print(i)

    print(index)


