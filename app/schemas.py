from pydantic import BaseModel


class CourseCreate(BaseModel):
    course_name: str
    course_code: str
    course_duration: int


class StudentCreate(BaseModel):
    name: str
    email: str
    password: str
    course_id: int


class CourseResponse(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    course_duration: int

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    student_id: int
    name: str
    email: str
    course: CourseResponse

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    name: str
    email: str
    course_id: int

class LoginRequest(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str

class StudentLogin(BaseModel):
    email: str
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class AdminCreate(BaseModel):
    name: str
    email: str
    password: str