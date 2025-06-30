import os
import uuid

def save_table_visualization(rows, columns):
    """
    Menyimpan hasil query SQL ke file HTML sederhana untuk divisualisasikan.
    """
    html_content = "<html><head><title>Hasil Query</title></head><body>"
    html_content += "<h2>Hasil Query SQL</h2>"
    html_content += "<table border='1' cellpadding='5' cellspacing='0'>"
    html_content += "<tr>" + "".join([f"<th>{col}</th>" for col in columns]) + "</tr>"

    for row in rows:
        html_content += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"

    html_content += "</table></body></html>"

    file_name = f"{uuid.uuid4()}.html"
    file_path = os.path.join("public", "tag_viz", file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return file_path
