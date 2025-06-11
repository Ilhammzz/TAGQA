def load_schema(conn):
    cur = conn.cursor()

    # Ambil struktur kolom
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    columns = cur.fetchall()

    # Ambil foreign key relationships
    cur.execute("""
        SELECT
            kcu.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM 
            information_schema.table_constraints AS tc 
        JOIN 
            information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN 
            information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
    """)
    foreign_keys = cur.fetchall()

    # Format skema deskriptif
    schema = ""
    current_table = None
    for table, column, dtype in columns:
        if table != current_table:
            if current_table is not None:
                schema += "\n"
            schema += f"Table \"{table}\":\n"
            current_table = table
        schema += f"  - {column} ({dtype})\n"

    # Tambahkan deskripsi relasi
    if foreign_keys:
        schema += "\n\n-- Foreign Key Relationships --\n"
        for table, col, ftable, fcol in foreign_keys:
            schema += f"{table}.{col} → {ftable}.{fcol}\n"

    cur.close()
    return schema.strip()






# def load_schema(conn):
#     """
#     Mengambil skema database (nama tabel dan kolom).
#     """
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT table_name, column_name, data_type
#         FROM information_schema.columns
#         WHERE table_schema = 'public'
#         ORDER BY table_name, ordinal_position;
#     """)
#     rows = cur.fetchall()
#     cur.close()

#     schema = ""
#     current_table = None
#     for table, column, dtype in rows:
#         if table != current_table:
#             schema += f"\nTable {table}:\n"
#             current_table = table
#         schema += f"  - {column} ({dtype})\n"
    
#     return schema.strip()
