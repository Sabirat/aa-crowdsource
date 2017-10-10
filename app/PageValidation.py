import MySQLdb
import re
def CreateFileWithHTMLSource(urlid,filename):
    html_source = ''
    db = MySQLdb.connect('localhost', 'root', 'br4cruta', 'AAmeetings')
    cursor = db.cursor()
    sql = 'SELECT textcontent FROM PageContentFromAlgo WHERE id =' + str(urlid) + ' ORDER BY sequenceofcontent'
    cursor.execute(sql)
    for row in cursor:
        html_source += row[0]
    local_html = open(filename, 'w+')
    html_source.decode('string_escape')
    html_source=re.sub(r'[^\x00-\x7F]+','', html_source)
    local_html.write(html_source)
    local_html.close()
    return
