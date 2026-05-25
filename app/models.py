from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    course_code = Column(String, unique=True, nullable=False)
    course_duration = Column(Integer)

    students = relationship(
        "Student",
        back_populates="course"
    )


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    

    course_id = Column(
        Integer,
        ForeignKey("courses.course_id")
    )

    course = relationship(
        "Course",
        back_populates="students"
    )

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)