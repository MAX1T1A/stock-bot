def user_check_on_admin(user_id):
    if user_id in (1172084194, 1041232059):
        return "admin"
    else:
        return "customer"
