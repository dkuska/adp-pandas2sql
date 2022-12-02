import typing

import libcst as cst

from utils.pd_df_operations import DF_OPERATIONS, PD_AGGREGATIONS, PD_ALIASES, PD_JOINS
from utils.assignment import Assignment
from utils.imports import Import, ImportFrom

class Visitor(cst.CSTVisitor):
    def __init__(self) -> None:
        self.pandas_imported = False
        self.pandas_alias = None

        self.imports = []  # Object used to keep track of imports in file
        self.imports_from = []

        self.assignments = []  # Object used to keep track of assignments

        self.dfs = []  # Object used to keep track of DataFrames
        self.sql_dfs = []

        super().__init__()


    def visit_Import(self, node: cst.Import) -> None:
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                import_name = name.name.value
                alias_name = ""
                if name.asname:
                    alias_name = name.asname.name.value
                    
                self.imports.append(Import(lib_name = import_name, alias = alias_name))


    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        module = node.module
        if isinstance(module, cst.Name):
            module_name = module.value
            imports = []
            if isinstance(node.names, typing.Sequence):
                for name in node.names:
                    if isinstance(name, cst.ImportAlias):
                        imports.append(name.name.value)
            elif isinstance(node.names, cst.ImportStar):
                imports.append('*')

            self.imports_from.append(ImportFrom(lib_name=module_name, imports=imports))
        elif isinstance(module, cst.Attribute):
            pass
        else:
            pass


    def visit_Assign(self, node: cst.Assign):
        targets = []
        values = []

        ## Parse targets
        for target in node.targets:
            if isinstance(target, cst.AssignTarget):
                target_target = target.target
                if isinstance(target_target, cst.Name):
                    targets.append(target_target.value)
                elif isinstance(target_target, cst.Tuple):
                    for element in target_target.elements:
                        if isinstance(element.value, cst.Name):
                            targets.append(element.value.value)

        ## Parse values
        node_value = node.value
        if isinstance(node_value, cst.Call):
            values.append(self.recursive_analyze_Call(node_value))
            print(self.recursive_analyze_Call(node_value))
        elif isinstance(node_value, cst.SimpleString):
            values.append(node_value.value)
            print(node_value.value)
        if isinstance(node_value, cst.Tuple):
            for element in node_value.elements:
                ## TODO: Parse element.value if this is somethin complicated....
                if isinstance(element.value, cst.SimpleString):
                    values.append(element.value.value)
                    print(element.value.value)
                    

        if len(targets) == len(values):
            for target, value in zip(targets, values):
                pass
        elif len(targets) > len(values):
            # Values returns multiple args
            pass


    def analyze_assignments(self):
        # First analyze all assignments
        for assignment in self.assignments:
            for df_operation in DF_OPERATIONS:
                if df_operation in assignment:
                    pass
                    # self.dfs[var_name] = value
        # Then analyze all DFs
        for df in self.dfs:
            pass

    
    def analyze_imports(self):
        for imp in self.imports:       
            ### PANDAS CHECK
            if imp.lib_name in PD_ALIASES or imp.alias in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = imp.alias
                if imp.alias == '':
                    self.pandas_alias = imp.lib_names
        for imp in self.imports_from:
            if imp.lib_name in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = imp.lib_name
    
    
    def recursive_analyze_Call(self, call: cst.Call):
        func = call.func
        lib, attribute = "", ""
        if isinstance(func, cst.Attribute):  # TODO: Figure out what other flows can be returned by call
            func_value = func.value
            # Func Value is simple name
            if isinstance(func_value, cst.Name):
                lib = func_value.value
            elif isinstance(func_value, cst.Call):
                lib = self.recursive_analyze_Call(func_value)  # Recursive call

            func_attr = func.attr
            if isinstance(func_attr, cst.Name):
                attribute = func_attr.value

        args = call.args
        parts_n = []
        for arg in args:
            keyword, argument = "", ""
            arg_value = arg.value
            if arg.keyword:
                arg_keyword = arg.keyword
                if isinstance(arg_keyword, cst.Name) or isinstance(arg_keyword, cst.SimpleString):
                    keyword = arg.keyword.value
                elif isinstance(arg_keyword, cst.Call):
                    keyword = self.recursive_analyze_Call(arg_keyword)

            if isinstance(arg_value, cst.Arg) or isinstance(arg_value, cst.SimpleString):
                argument = arg_value.value
            elif isinstance(arg_value, cst.Call):
                argument = self.recursive_analyze_Call(arg_value)

            if keyword == "":
                parts_n.append(argument)
            else:
                parts_n.append("=".join([keyword, argument]))

        ## TODO: Persist this somehow...
        return_value = lib + "." + attribute + "(" + ",".join(parts_n) + ")"

        return return_value


    def print_summary(self):
        print("Report:")

        print(f"# imports {len(self.imports) + len(self.imports_from)}")
        for imp in self.imports:
            print(imp)
            
        for imp_from in self.imports_from:
            print(imp_from)

        print(f"pandas imported: {self.pandas_imported}")
        print(f"pandas_alias: {self.pandas_alias}")

        print(f"# assignments {self.assign_counter}")
        for assignment in self.assignments:
            pass
            # print(f"{var_name} = {value}")

        print(f"# dfs {len(self.dfs)}")
        for df in self.dfs:
            pass
            # print(f"df: {var_name} = {value}")