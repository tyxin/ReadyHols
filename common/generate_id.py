def generate_id(type_count, cursor, table_name, id_name):
    valid_id = "{:09d}".format(type_count)
    exist_entry = None
    while exist_entry == None:
        cursor.execute('SELECT * from ' + table_name + ' where ' + ' ' + id_name + '=%s', (valid_id,))
        exist_entry = cursor.fetchone()
        if exist_entry == None:
            break
        type_count += 1
        valid_id = "{:09d}".format(type_count)
    return valid_id