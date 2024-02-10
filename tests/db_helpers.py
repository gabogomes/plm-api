def assert_wheres_are_equal(mock_where, which_call, expression):
    sql_expr = mock_where.call_args_list[which_call][0][0]
    assert sql_expr.compare(expression)
