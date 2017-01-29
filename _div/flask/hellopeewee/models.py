from peewee import *

db = SqliteDatabase('students.db')

class Student(Model):
	id = PrimaryKeyField()
	name = CharField()
	grade = IntegerField()

	class Meta:
		database = db


def initialize_db():
	db.connect()
	db.create_tables([Student], safe=True)

initialize_db()

david = Student.create(name='David', grade=95)
ezra = Student.create(name='Ezra', grade=50)

for s in Student.select().where(Student.grade < 75):
	print s.name

ezra.grade = 95
ezra.save()

ezra.delete_instance()

db.close()

