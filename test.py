import pandas as pd


def removeWhiteSpace(arg_str=str):
    n1 = False  # num of \'
    n2 = False  # num of \"
    new_str = ""
    for ch in arg_str:
        new_str += ch
        if ch == '\'':
            n1 = not n1
        elif ch == '\"':
            n2 = not n2
        elif ch == ' ':
            if not n1 and not n2:
                new_str = new_str[:-1]

    return new_str


class Database:
    tables = dict()

    def getFile(self):
        str = input("input csv file: ")
        try:
            data = pd.read_csv(str, index_col=0)
        except:
            print("file name does no exist!")

        # store df in tables
        self.tables[str.removesuffix('.csv')] = data

    def help(self):
        print("supply command:"
              "\n* read: read"
              "\n* quit: quit"
              "\n* select: select"
              "\n* project: project(<table1>, label1, label2...)"
              "\n* rename: rename(<table>, <newName>)"
              "\n* cartesian product: product(<table1>, <table2>)"
              "\n* set union: union(<table1>, <table2>"
              "\n* set difference: differ(<table1>, <table2>"
              "\n* list: ls or ls <table_name>")

    def list(self, arg_str=str):
        if len(arg_str) == 0:
            print("all tables:")
            print([table_name for table_name in self.tables.keys()], sep=', ')
        else:
            print("all columns in " + arg_str + ":")
            print([label_name for label_name in self.tables[arg_str].columns])

    def cmd_parser(self, cmd_str):
        # parse the command string
        cmd_str = removeWhiteSpace(cmd_str)
        print(cmd_str)
        arg = str
        # check if there is any following arguments
        if (cmd_str.find('(') == -1):
            operation = cmd_str
            arg = ''
        else:
            operation, arg = cmd_str.split('(', 1)
            if arg[-1] == ')':  # remove last ')' from argument string
                arg = arg[:-1]

        unary_cmd = ['select', 'project', 'rename']
        binary_cmd = ['product', 'differ', 'union', 'intersect', 'divide', 'join']

        try:
            if operation in unary_cmd:
                if arg.count('(') > 0:
                    # split the arg_str to be [operation, arg]
                    new_operation, arg = arg.rsplit('),', 1)
                    table1 = self.cmd_parser(new_operation)
                # get which table to be selected
                else:
                    table_name, arg = arg.split(',', 1)
                    table1 = self.tables[table_name]
            elif operation in binary_cmd:
                table1_name, table2_name = self.splitBinary(arg)
                if table1_name.count('(') > 0:
                    table1 = self.cmd_parser(table1_name)
                else:
                    table1 = self.tables[table1_name]
                if table2_name.count('(') > 0:
                    table2 = self.cmd_parser(table2_name)
                else:
                    table2 = self.tables[table2_name]
        except:
            print("format error!")
            return

        if operation == 'help':
            return self.help()
        elif operation == 'read':
            return self.getFile()
        elif operation == 'ls':
            return self.list(arg)
        elif operation == 'select':
            return self.select(table1, arg)
        elif operation == 'project':
            return self.project(table1, arg)
        elif operation == 'rename':
            return self.rename(table1, arg)
        elif operation == 'product':
            return self.product(table1, table2)
        elif operation == 'differ':
            return self.differ(table1, table2)
        elif operation == 'union':
            return self.union(table1, table2)
        elif operation == 'intersect':
            return self.intersect(table1, table2)
        elif operation == 'divide':
            return self.divide(table1, table2)
        elif operation == 'join':
            return self.join(table1, table2)

    def search(self, table=pd.DataFrame, condition=str):
        operators = ['==', '<', '<=', '>', '>=']
        arg1 = str
        arg2 = str
        compare = str
        for oper in operators:
            if condition.find(oper) != -1:  # operator exist
                arg1, arg2 = condition.split(oper, 1)
                compare = oper
                break
        if arg1 not in table.columns:
            print("invalid keyword: " + arg1)

        label1 = arg1.strip('\'')
        label1 = label1.strip('\"')
        # decide arg2 is a label or constant
        if arg2.isdigit() or arg2.count('\'') > 0 or arg2.count('\"') > 0:
            # is a constant
            label1_index = table.columns.get_loc(label1)
            aDF = pd.DataFrame(
                [aData for aData in table.values if self.compare(aData[label1_index], arg2, compare)]
                , columns=table.columns)

        else:
            label2 = arg2.strip('\'')
            label2 = label2.strip('\"')
            try:
                label1_index = table.columns.get_loc(label1)
                label2_index = table.columns.get_loc(label2)
                aDF = pd.DataFrame(
                    [aData for aData in table.values if self.compare(aData[label1_index], aData[label2_index], compare)]
                    , columns=table.columns)
            except:
                print("label1 or label2 invalid")
        return aDF

    def compare(self, data1, data2, operator):
        expr = '\"' + str(data1) + '\"' + operator + str(data2)
        return eval(expr)

    def select(self, table=pd.DataFrame, arg_str=str):

        # return the data which fit the condition
        df = self.search(table, arg_str)
        return df

    def project(self, table=pd.DataFrame, arg_str=str):

        projected_columns = arg_str.split(',')
        df = table.copy()
        cols = [col for col in df.columns if col not in projected_columns]
        return df.drop(columns=cols)

    def rename(self, table=pd.DataFrame, arg=str):

        cols = arg.split(',')
        new_name = cols[0]
        cols.remove(new_name)
        # check if the number of the name of columns is match
        if len(cols) == 0:
            new_table = table.copy()
            self.tables[new_name] = new_table
            return new_table
        elif len(cols) != len(table.columns):
            print("numbers of columns do not match!")
            return None
        else:
            aDict = dict()
            for col, new_col in zip(table.columns, cols):
                aDict[col] = new_col
            new_table = table.rename(columns=aDict)
            self.tables[new_name] = new_table
            return new_table

    def product(self, table1=pd.DataFrame, table2=pd.DataFrame):
        labels = table1.columns + table2.columns

        newTable = pd.DataFrame(columns=labels)
        for data1 in table1.values:
            for data2 in table2.values:
                data1 = pd.Series(data1)
                data2 = pd.Series(data2)
                newTable.add(pd.concat([data1, data2]), axis='columns')
        return newTable

    def union(self, table1=pd.DataFrame, table2=pd.DataFrame):

        table1_tuples = [tuple(row) for row in table1.to_numpy()]
        table2_tuples = [tuple(row) for row in table2.to_numpy()]
        union_set = set(table1_tuples).union(set(table2_tuples))
        union_df = pd.DataFrame(union_set, columns=table1.columns)
        return union_df

    def differ(self, table1=pd.DataFrame, table2=pd.DataFrame):

        table1_tuples = [tuple(row) for row in table1.to_numpy()]
        table2_tuples = [tuple(row) for row in table2.to_numpy()]

        difference = set(table1_tuples) - set(table2_tuples)

        # 将差集转换回 DataFrame
        difference_df = pd.DataFrame(list(difference), columns=table1.columns)

        return difference_df
        # differ(pokemon,select(pokemon,HP<100))

    def intersect(self, table1=pd.DataFrame, table2=pd.DataFrame):
        table1_tuples = [tuple(row) for row in table1.to_numpy()]
        table2_tuples = [tuple(row) for row in table2.to_numpy()]
        # A - (A-B)
        diff_set = set(table1_tuples) - set(table2_tuples)
        intersection_set = set(table1_tuples) - diff_set
        return pd.DataFrame(intersection_set, columns=table1.columns)

    def splitBinary(self, arg_str=str):
        # find which ',' to split string into two tables

        n = 0  # number of ['(', ')'] pair
        idx = 0
        table1 = str
        table2 = str
        for i in arg_str:
            if i == '(':
                n += 1
            elif i == ')':
                n -= 1
            elif i == ',' and n == 0:
                table1 = arg_str[:idx]
                table2 = arg_str[idx + 1:]
                break
            idx += 1

        return table1, table2


def interface():
    aDatabase = Database()
    while True:
        print("type \"help\" for more detail")
        command = input("input command: ")
        if command == 'quit':
            break
        else:
            print(aDatabase.cmd_parser(command))


'''
table1 = pd.DataFrame({"Name":['a','b','c'], "HP":[10,11,12]})
table2 = pd.DataFrame({"pokeName":['sd','ew','dd','ee']})
print(table1)
'''
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
interface()

