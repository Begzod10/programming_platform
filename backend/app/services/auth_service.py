from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import Student, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.db.session import get_db
from app.services.gennis_service import GennisService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def create_ranking(db: AsyncSession, student_id: int):
    """Ranking yaratish helper function"""
    from app.models.ranking import Ranking

    # Mavjudligini tekshirish
    result = await db.execute(select(Ranking).where(Ranking.student_id == student_id))
    if result.scalar_one_or_none():
        return None

    # Yangi ranking yaratish
    new_ranking = Ranking(
        student_id=student_id,
        daily_points=0,
        weekly_points=0,
        monthly_points=0,
        total_points=0,
        global_rank=0,
        level_rank=0,
        projects_completed=0,
        average_grade=0.0
    )
    db.add(new_ranking)
    await db.commit()
    await db.refresh(new_ranking)
    return new_ranking


async def register_new_student(db: AsyncSession, user_data: UserCreate):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish"""
    # Email tekshirish
    result = await db.execute(select(Student).where(Student.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Bu email bilan ro'yxatdan o'tilgan."
        )

    # Username tekshirish
    result2 = await db.execute(select(Student).where(Student.username == user_data.username))
    if result2.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Bu username band!"
        )

    # Yangi foydalanuvchi yaratish
    new_student = Student(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    # ✅ Ranking avtomatik yaratish (FAQAT student uchun)
    if new_student.role == UserRole.student:
        await create_ranking(db, new_student.id)

    # Token yaratish
    access_token = create_access_token(subject=new_student.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_student
    }


async def login(db: AsyncSession, username: str, password: str):
    """Login - Gennis birinchi, keyin lokal"""
    username = username.strip()
    
    # 1. Gennis bilan login qilib ko'ramiz
    print(f"Attempting Gennis login for: {username}")
    gennis_data = await GennisService.login(username, password)
    
    if gennis_data:
        print("Gennis data received, syncing...")
        # Gennis login muvaffaqiyatli
        user_data = gennis_data.get("user", {})
        gennis_id = user_data.get("id") or user_data.get("user_id") or gennis_data.get("id")

        
        # role_str ni to'g'ri aniqlash (Gennis API ba'zan dict qaytaradi)
        raw_role = user_data.get("role")
        if isinstance(raw_role, dict):
            role_str = raw_role.get("name")
        elif isinstance(raw_role, str):
            role_str = raw_role
        else:
            role_str = gennis_data.get("type_user")
            
        print(f"Gennis ID: {gennis_id}, Role: {role_str}")
        
        # Bizning bazadan foydalanuvchini topamiz (username yoki email orqali)
        # Gennis foydalanuvchilari uchun username ko'pincha 'gennis_{id}' bo'ladi
        # Lekin o'qituvchilar o'z username'lari bilan kirishadi
        gennis_email = user_data.get("email")
        if gennis_email:
            gennis_email = gennis_email.strip()

        print(f"DEBUG: Login attempt - username: {username}, gennis_id: {gennis_id}, gennis_email: {gennis_email}")
        
        conditions = [
            func.lower(Student.username) == username.lower(),
            func.lower(Student.email) == username.lower(),
            Student.username == f"gennis_{gennis_id}"
        ]
        if gennis_email:
            conditions.append(func.lower(Student.email) == gennis_email.lower())
            
        stmt = select(Student).where(or_(*conditions))
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        print(f"DEBUG: Users found count: {len(users)}")
        for u in users:
            print(f"DEBUG: Found User - ID: {u.id}, Username: {u.username}, Email: {u.email}")
            
        user = users[0] if users else None


        
        if not user:
            # Yangi foydalanuvchi yaratamiz
            role = UserRole.teacher if role_str == 'teacher' else UserRole.student
            user = Student(
                username=username if role == UserRole.teacher else f"gennis_{gennis_id}",
                email=user_data.get("email") or f"{username}@gennis.uz",
                full_name=f"{user_data.get('name', '')} {user_data.get('surname', '')}".strip(),
                hashed_password="external_auth",
                role=role,
                is_active=True
            )
            db.add(user)
            try:
                await db.commit()
                await db.refresh(user)
            except IntegrityError:
                await db.rollback()
                print("DEBUG: IntegrityError during creation, trying to find user one more time...")
                # Bir marta yana qidirib ko'ramiz (balki email yoki username banddir)
                stmt = select(Student).where(
                    (Student.username == user.username) | 
                    (Student.email == user.email)
                )
                result = await db.execute(stmt)
                user = result.scalars().first()
                if not user:
                    print("DEBUG: Still no user found after IntegrityError. Raising exception.")
                    raise # Qayta tashlaymiz agar baribir topilmasa
                print(f"DEBUG: Found user {user.username} after IntegrityError fallback.")
            
            # Ranking yaratish (faqat student uchun)
            if user.role == UserRole.student:
                await create_ranking(db, user.id)

        # Foydalanuvchi mavjud, rolini yangilash kerakmi tekshiramiz
        if user:
            correct_role = UserRole.teacher if role_str == 'teacher' else UserRole.student
            changed = False
            if user.role != correct_role:
                user.role = correct_role
                changed = True

            # Student uchun "gennis_None" username'ni to'g'irlash
            if correct_role == UserRole.student and (user.username == "gennis_None" or not user.username) and gennis_id:
                user.username = f"gennis_{gennis_id}"
                changed = True

            # O'qituvchi uchun username kiritilgan qiymatga moslashtiramiz
            # (eski "gennis_{id}" username'ni asl username bilan almashtiramiz)
            if correct_role == UserRole.teacher and user.username != username:
                conflict = await db.execute(
                    select(Student).where(
                        Student.username == username,
                        Student.id != user.id,
                    )
                )
                if conflict.scalars().first() is None:
                    user.username = username
                    changed = True

            if changed:
                await db.commit()
                await db.refresh(user)


        # Sinxronizatsiyani boshlaymiz
        if user.role == UserRole.teacher:
            await GennisService.sync_teacher_data(db, user, gennis_data)
        elif user.role == UserRole.student:
            await GennisService.sync_student_data(db, user, gennis_data)
            
        return {
            "access_token": create_access_token(subject=user.id),
            "token_type": "bearer",
            "user": user
        }

    # 2. Gennis o'xshasa (yoki admin bo'lsa), lokal bazadan tekshiramiz
    result = await db.execute(
        select(Student).where(
            (Student.username == username) |
            (Student.email == username)
        )
    )
    user = result.scalars().first()

    # Foydalanuvchi yoki parol noto'g'ri
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username yoki parol noto'g'ri"
        )

    # Faol emasligini tekshirish
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )

    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
        "user": user
    }


async def logout(db: AsyncSession, email: str, password: str):
    """Logout (TODO: Redis token blacklist)"""
    return {"message": "Logout qilindi"}


async def delete_user(user_id: int, db: AsyncSession):
    """Foydalanuvchini o'chirish"""
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    await db.delete(user)
    await db.commit()

    return {"message": "Foydalanuvchi o'chirildi"}


async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession):
    """Foydalanuvchini yangilash"""
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    # Ma'lumotlarni yangilash
    for key, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user
