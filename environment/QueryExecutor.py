# import postgres connector class
from environment.PostgresSqlExecutor import PostgresSqlExecutor

PostgresSqlExecutor.create_hypo_index("orders", "o_comment")
PostgresSqlExecutor.create_hypo_index("orders", "o_custkey")
PostgresSqlExecutor.create_hypo_index("lineitem", "l_orderkey")

print()
print(PostgresSqlExecutor.execute_select_query("SELECT * FROM hypopg_list_indexes()"))
print()

PostgresSqlExecutor.remove_hypo_index("orders", "o_custkey")
print("After removal")
print(PostgresSqlExecutor.execute_select_query("SELECT * FROM hypopg_list_indexes()"))
