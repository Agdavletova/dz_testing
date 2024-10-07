from django.db import models
from django.conf import settings


class Student(models.Model):

    name = models.TextField()

    birth_date = models.DateField(
        null=True,
    )


class Course(models.Model):

    name = models.TextField()

    students = models.ManyToManyField(
        Student,
        blank=True,
    )
    def add_student(self, other):
        if self.students.count() >= settings.MAX_STUDENTS_PER_COURSE:
            raise ValueError("Нельзя добавить больше 20 сдентов на курс")
        self.students.add(other)
