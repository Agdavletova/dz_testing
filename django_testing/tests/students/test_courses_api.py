import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from model_bakery import baker
from students.serializers import CourseSerializer

from students.models import Course, Student
import random
from pytest import raises

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

@pytest.fixture
def random_number():
    return random.randint(0, 9)

@pytest.mark.django_db
def test_retrieve(client, course_factory):
    url = reverse("courses-list")
    course = course_factory(_quantity=1)
    resp = client.get(url)
    expected_data = CourseSerializer(course[0]).data
    assert resp.status_code == 200
    assert resp.json()[0] == expected_data

@pytest.mark.django_db
def test_list(client, course_factory):
    url = reverse("courses-list")
    courses = course_factory(_quantity=10)
    resp = client.get(url)
    expected_data = CourseSerializer(courses, many=True).data
    assert resp.status_code == 200
    assert resp.json() == expected_data

@pytest.mark.django_db
def test_filter_id(client, course_factory, random_number):
    courses = course_factory(_quantity=10)
    course_id = courses[random_number].id
    url = reverse("courses-list") + f"?id={course_id}"
    resp = client.get(url)
    expected_data = CourseSerializer(courses[random_number]).data
    assert resp.status_code == 200
    assert resp.json()[0] == expected_data

@pytest.mark.django_db
def test_filter_name(client, course_factory,random_number):
    courses = course_factory(_quantity=10)
    course_name = courses[random_number].name
    url = reverse("courses-list") + f"?name={course_name}"
    resp = client.get(url)
    expected_data = CourseSerializer(courses[random_number]).data
    assert resp.status_code == 200
    assert resp.json()[0] == expected_data

@pytest.mark.django_db
def test_create_course(client):
    url = reverse("courses-list")
    data = {
        "name" : "A"
    }
    resp = client.post(url, data=data)
    assert resp.status_code == 201
    course_id = resp.json()["id"]
    expected_data = client.get(reverse("courses-detail", kwargs={"pk":course_id}))
    assert resp.json() == expected_data.json()

@pytest.mark.django_db
def test_patch_course(client, course_factory,random_number):
    courses = course_factory(_quantity=10)
    course_id = courses[random_number].id
    url = reverse("courses-detail", kwargs={"pk": course_id})
    data = {
        "name" : "update"
    }
    resp = client.patch(url, data=data)
    assert resp.status_code == 200
    expected_data = client.get(url)
    assert  resp.json() == expected_data.json()

@pytest.mark.django_db
def test_patch_course(client, course_factory,random_number):
    courses = course_factory(_quantity=10)
    course_id = courses[random_number].id
    url = reverse("courses-detail", kwargs={"pk": course_id})
    resp = client.delete(url)
    assert resp.status_code == 204
    expected_data = client.get(url)
    assert expected_data.status_code == 404

@pytest.mark.django_db
def test_max_students(settings, client, course_factory, student_factory):
    settings.MAX_STUDENTS_PER_COURSE = 20
    course = course_factory()
    student = student_factory()
    course.students.count = lambda : 20
    with raises(ValueError, match="Нельзя добавить больше 20 студентов на курс"):
        course.add_student(student)

    assert course.students.count() == 20

