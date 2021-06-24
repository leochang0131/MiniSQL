import random

# INSERT
# insert into student values (0, st0, 0, M)


table = "student"
INSERT_PREFIX = "insert into {} values ".format(table)

with open("insert.test", "w") as f:
    for i in range(20):
        values = "({}, s{}, {}, {});\n".format(i, i, random.randint(10, 20), 'M' if i % 2 == 0 else 'F')
        f.writelines(INSERT_PREFIX + values)
