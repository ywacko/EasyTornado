from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import pymysql


class selectHandler(RequestHandler):

    def doSelect(self, table, id, name):
        db = sqlStart()
        result, n = db.select(table, id, name)
        if n == 0:
            results = ""
            for rows in result:
                results += str(rows) + "   "
            self.render("result.html", result = results)
        else:
            self.render("result.html", result = result)
        db.close()

    def get(self):
        self.render("select.html")

    def post(self):
        name = self.get_argument("name", "")
        id = self.get_argument("id", "")
        table = self.get_argument("table")
        self.doSelect(table, id, name)


class insertHandler(RequestHandler):

    def doInsert(self, table, value):
        db = sqlStart()
        result = db.insert(table, value)
        self.render("result.html", result = result)
        db.close()

    def get(self):
        self.render("insert.html")

    def post(self):
        table = self.get_argument("table")
        value = self.get_argument("value")
        self.doInsert(table, value)


class updateHandler(RequestHandler):

    def doUpdate(self, table, id, column, newValue):
        db = sqlStart()
        result = db.update(table, id, column, newValue)
        self.render("result.html", result=result)
        db.close()

    def get(self):
        self.render("update.html")

    def post(self):
        table = self.get_argument("table")
        id = self.get_argument("id", "")
        column = self.get_argument("column")
        newValue = self.get_argument("value")
        self.doUpdate(table, id, column, newValue)


class sqlStart:

    def __init__(self):
        self.db = pymysql.connect(user="root", passwd="yugioh", database="test")
        self.cursor = self.db.cursor()
        self.selectError = "No Record"

    def close(self):
        self.db.close();

    def select(self, table, id, name):
        table = table.capitalize()
        if id != "":
            key = table + "ID"
            isID = 0
        elif name != "":
            key = table + "Name"
            name = "\"" + name + "\""
            isID = 1
        else:
            isID = 2
        list = [id, name]
        sql = "select * from " + table
        if isID != 2:
            sql += " Where " + key + " = " + list[isID]
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                return result, 0
            else:
                return self.selectError, 1
        except Exception as e:
            return e, 2

    def insert(self, table, value):
        table = table.capitalize()
        sql = "insert into " + table + " values " + value
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return "Inserted Successfully"
        except Exception as e:
            self.db.rollback()
            return "Inserted Failed " + str(e)

    def update(self, table, id, column, newValue):
        table = table.capitalize()
        key = table + "ID"
        sql = "update " + table + " set " + column + " = " + newValue
        if id != "":
            sql += " Where " + key + " = " + id
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return "Updated Successfully"
        except Exception as e:
            self.db.rollback()
            return "Updated Failed " + str(e)


def main():
    app = Application(handlers=[(r"/select", selectHandler),
                                (r"/insert", insertHandler),
                                (r"/update", updateHandler)])
    httpServer = HTTPServer(app)
    httpServer.listen(8080)
    IOLoop.current().start()


if __name__ == '__main__':
    main()