import sqlite3


class EuroclearPipeline:

    # Database setup
    conn = sqlite3.connect('euroclear.db')
    c = conn.cursor()

    def open_spider(self, spider):
        self.c.execute("""CREATE TABLE IF NOT EXISTS `euroclear`
                         (date text, title text, link text, content text)""")

    def process_item(self, item, spider):
        self.c.execute("""SELECT * FROM euroclear WHERE title = ? AND date = ?""",
                       (item.get('title'), item.get('date')))
        duplicate = self.c.fetchall()
        if len(duplicate):
            return item
        print(f"New entry added at {item['link']}")

        # Insert values
        self.c.execute("INSERT INTO euroclear (date, title, link, content)"
                       "VALUES (?,?,?,?)", (item.get('date'), item.get('title'), item.get('link'), item.get('content')))
        self.conn.commit()  # commit after every entry

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

