from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.db.session import get_db
from app.models.user import Student
from jose import JWTError, jwt
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_student(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except (JWTError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
    return user


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, student_id: int, data: ProjectCreate) -> Project:
        new_project = Project(**data.dict(), student_id=student_id)
        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)
        return new_project

    async def get_project(self, project_id: int) -> Project:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Proyekt topilmadi")
        return project

    async def get_all_projects(self, skip: int = 0, limit: int = 10):
        result = await self.db.execute(select(Project).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_project(self, project_id: int, student_id: int, data: ProjectUpdate) -> Project:
        project = await self.get_project(project_id)
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int, student_id: int):
        project = await self.get_project(project_id)
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        await self.db.delete(project)
        await self.db.commit()
        return {"message": "Proyekt o'chirildi"}

    async def get_all_projects_by_student(self, student_id: int):
        result = await self.db.execute(
            select(Project).where(Project.student_id == student_id)
        )
        return result.scalars().all()

    async def submit_project(self, project_id: int, student_id: int):
        project = await self.get_project(project_id)
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        if project.status != "Draft":
            raise HTTPException(status_code=400, detail="Proyekt allaqachon yuborilgan")
        project.status = "Submitted"
        from datetime import datetime
        project.submitted_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(project)
        return project
