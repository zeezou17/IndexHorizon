from typing import Set, Dict, List
import sqlparse
import re
from environment.Constants import Constants


# this class parses only simple queries to extract each where condition and form a seperate query
#  which is used in later stages to find selectivity of each column

class Query:
    query_string: str
    # key will hold "table_name::column_name" and value will hold the selectivity query
    where_clause_columns_query: Dict[str, str]
    all_predicates: Set[str] = set()

    def __init__(self, query_string, columns_map: Dict[str, List[str]]):
        # parse the query with sql parse to remove comments and correct identation for efficient parsing
        self.query_string = sqlparse.format(query_string, strip_comments=True, reindent=True).strip()
        self.where_clause_columns_query = dict()
        # split to get contents of different sections of query, i.e from section, where clause, order by , group by
        # we need only from and where clause section to find the selectivity of each predicate
        from_section_start_pos = 0
        from_section_end_pos = -0
        where_section_start_pos = 0
        where_section_end_pos = len(self.query_string)
        from_section_not_discovered = True
        where_section_not_discovered = True
        where_section_not_ended = True
        cur_index_count = 0
        table_alias_dict = dict()
        for line in self.query_string.splitlines():
            if from_section_not_discovered and re.match(Constants.POSTGRES_KEYWORD_FROM, line):
                from_section_start_pos = cur_index_count + line.lower().find('from') + 4
                from_section_not_discovered = False
            if where_section_not_discovered and re.match(Constants.POSTGRES_KEYWORD_WHERE, line):
                from_section_end_pos = cur_index_count
                where_section_start_pos = cur_index_count + line.lower().find('where') + 5
                where_section_not_discovered = False
            if where_section_not_ended and re.match(Constants.POSTGRES_ORDER_BY_GROUP_BY_KEYWORDS, line):
                where_section_end_pos = cur_index_count
                break
            cur_index_count = cur_index_count + len(line) + 1  # +1 added for new line
        from_section = self.query_string[from_section_start_pos:from_section_end_pos]
        where_section = self.query_string[where_section_start_pos:where_section_end_pos]
        # extract all table names which is separated by comma
        for cur_tbl_text in re.split(",", from_section):
            # table may have alias first remove unwanted whitespace to do this check
            tbl_data = ' '.join(cur_tbl_text.strip().split()).split(' ')
            if len(tbl_data) == 1:
                table_alias_dict.update({tbl_data[0]: tbl_data[0]})
            else:
                table_alias_dict.update({tbl_data[1]: tbl_data[0]})
        # extra where section data
        # get individual predicates
        for predicate in re.split(Constants.POSTGRES_BOOLEAN_OPERATIONS_LIST_AS_STRING, where_section):
            predicate = predicate.strip().replace('\n', '').replace('\r', '')
            splitted_predicate = re.split(Constants.POSTGRES_PREDICATE_OPERATIONS_LIST_AS_STRING,
                                          ' '.join(predicate.split()))
            left_expr = splitted_predicate[0].strip()
            is_predicate_used_for_selectivity = True
            # right expr is present only if len > 1
            if len(splitted_predicate) > 1:
                right_expr = splitted_predicate[1]
                # check right side predicate whether it has further expression or just a value/column name
                # if further expression present no need to do further checks for right expr as
                # it is assumed that queries(which satisfy right expr conditon) used in this project will
                # hold only values not column names
                # example : o_orderdate < ---date '1994-01-01' + interval '1' year---
                # string between '---' is the right (sub) expr
                # there can be scenarios where expr might contain a string value with spaces  example
                # 'MIDDLE EAST' , this should be splitted

                splitted_right_expr = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', right_expr.strip())
                if len(splitted_right_expr) > 1:
                    is_predicate_used_for_selectivity = True
                else:
                    # check whether right expression is a join or some value if join then this predicate
                    # can be ignored from selectivity calculation
                    # if below condition is satisfied then it is a  join and it can not be considered for selectivity
                    if not self.find_matching_table_for_column(columns_map, table_alias_dict,
                                                               splitted_right_expr[0]) == '':
                        is_predicate_used_for_selectivity = False
            if is_predicate_used_for_selectivity:
                table_with_alias = self.find_matching_table_for_column(columns_map, table_alias_dict, left_expr)
                key = table_with_alias.split(' ')[-1] + Constants.MULTI_KEY_CONCATENATION_STRING + left_expr.split('.')[
                    -1]
                value = Constants.QUERY_FIND_SELECTIVITY.format(table_with_alias, predicate)
                self.where_clause_columns_query[key] = value
                Query.all_predicates.add(key)

    @staticmethod
    def find_matching_table_for_column(columns_map: Dict[str, List[str]], table_alias_dict: Dict[str, str],
                                       col_name: str):

        table_str: str = ''
        if col_name.find('.') != -1:
            table_str = table_alias_dict.get(col_name.split('.')[0]) + ' ' + col_name.split('.')[0]
        elif col_name in columns_map:
            table_list = columns_map.get(col_name)
            # if similar column names are present in more than one table then
            #  it need to be filtered by passing the table names extracted from "From Section"
            if len(table_list) > 1:
                inter_section = list(set(table_list) & set((table_alias_dict.values())))
                table_str = inter_section[0]
            else:
                table_str = table_list[0]
        return table_str

    @staticmethod
    def reset():
        Query.all_predicates.clear()
