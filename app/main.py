from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import engine
from .database import SessionLocal
from . import models, schemas

from fastapi import HTTPException

from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

models.Base.metadata.create_all(bind=engine)

def create_default_admin():

    db = SessionLocal()

    existing_admin = db.query(models.Admin).filter(
        models.Admin.email == "admin@gmail.com"
    ).first()

    if not existing_admin:

        admin = models.Admin(
            name="Admin",
            email="admin@gmail.com",
            password=hash_password("admin123")
        )

        db.add(admin)
        db.commit()

        print("Default admin created")

    db.close()

create_default_admin()
app = FastAPI()

security = HTTPBearer()


# DATABASE DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# GET CURRENT USER FROM JWT
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return payload


# ADMIN-ONLY PROTECTION
def admin_only(user=Depends(get_current_user)):

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user


# HOME
@app.get("/")
def home():
    return {
        "message": "Backend running"
    }


# GET ALL COURSES
@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):

    courses = db.query(models.Course).all()

    return courses


# CREATE COURSE (ADMIN ONLY)
@app.post("/courses")
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    new_course = models.Course(
        course_name=course.course_name,
        course_code=course.course_code,
        course_duration=course.course_duration
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return {
        "message": "Course created successfully"
    }


# CREATE STUDENT (ADMIN ONLY)
@app.post("/students")
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    course = db.query(models.Course).filter(
        models.Course.course_id == student.course_id
    ).first()

    if not course:
        return {
            "error": "Course not found"
        }

    new_student = models.Student(
        name=student.name,
        email=student.email,
        password=hash_password(student.password),
        course_id=student.course_id
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student created successfully"
    }


# GET ALL STUDENTS (ADMIN ONLY)
@app.get(
    "/students",
    response_model=list[schemas.StudentResponse]
)
def get_students(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    students = db.query(models.Student).all()

    return students


# UPDATE STUDENT (ADMIN ONLY)
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    if not student:
        return {
            "error": "Student not found"
        }

    course = db.query(models.Course).filter(
        models.Course.course_id == updated_student.course_id
    ).first()

    if not course:
        return {
            "error": "Course not found"
        }

    student.name = updated_student.name
    student.email = updated_student.email
    student.course_id = updated_student.course_id

    db.commit()

    return {
        "message": "Student updated successfully"
    }


# DELETE STUDENT (ADMIN ONLY)
@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    if not student:
        return {
            "error": "Student not found"
        }

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }


# GET STUDENTS BY COURSE
@app.get(
    "/courses/{course_id}/students",
    response_model=list[schemas.StudentResponse]
)
def get_students_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    course = db.query(models.Course).filter(
        models.Course.course_id == course_id
    ).first()

    if not course:
        return {
            "error": "Course not found"
        }

    return course.students


# ADMIN LOGIN
@app.post("/admin/login")
def admin_login(
    request: schemas.AdminLogin,
    db: Session = Depends(get_db)
):

    admin = db.query(models.Admin).filter(
        models.Admin.email == request.email
    ).first()

    if not admin:
        return {
            "error": "Invalid email"
        }

    if not verify_password(
        request.password,
        admin.password
    ):
        return {
            "error": "Invalid password"
        }

    token = create_access_token({
        "email": admin.email,
        "role": "admin"
    })

    return {
        "access_token": token
    }


# STUDENT LOGIN
@app.post("/student/login")
def student_login(
    request: schemas.StudentLogin,
    db: Session = Depends(get_db)
):

    student = db.query(models.Student).filter(
        models.Student.email == request.email
    ).first()

    if not student:
        return {
            "error": "Invalid email"
        }

    if not verify_password(
        request.password,
        student.password
    ):
        return {
            "error": "Invalid password"
        }

    token = create_access_token({
        "email": student.email,
        "role": "student"
    })

    return {
        "access_token": token
    }


# CREATE ADMIN (ADMIN ONLY)
@app.post("/admins")
def create_admin(
    admin: schemas.AdminCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    existing_admin = db.query(models.Admin).filter(
        models.Admin.email == admin.email
    ).first()

    if existing_admin:
        return {
            "error": "Admin already exists"
        }

    new_admin = models.Admin(
        name=admin.name,
        email=admin.email,
        password=hash_password(admin.password)
    )

    db.add(new_admin)
    db.commit()

    return {
        "message": "Admin created successfully"
    }


# STUDENT CAN VIEW OWN PROFILE
@app.get(
    "/me",
    response_model=schemas.StudentResponse
)
def get_my_profile(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    student = db.query(models.Student).filter(
        models.Student.email == user["email"]
    ).first()

    if not student:
        return {
            "error": "Student not found"
        }

    return student

@app.put("/change-password")
def change_password(
    passwords: schemas.ChangePassword,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    student = db.query(models.Student).filter(
        models.Student.email == user["email"]
    ).first()

    if not student:
        return {
            "error": "Student not found"
        }

    # Verify old password
    if not verify_password(
        passwords.old_password,
        student.password
    ):
        return {
            "error": "Old password is incorrect"
        }

    # Hash new password
    student.password = hash_password(
        passwords.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }