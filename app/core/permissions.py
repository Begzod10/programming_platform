# from fastapi import Depends, HTTPException, status
# from app.models.user import Student, UserRole
# from app.core.security import get_current_user
#
#
# def require_role(allowed_roles: list[UserRole]):
#     """
#     Role-based access control decorator.
#     Faqat ruxsat berilgan rollar kirishi mumkin.
#     """
#
#     async def role_checker(current_user: Student = Depends(get_current_user)):
#         if current_user.role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Bu amalni bajarish uchun {[r.value for r in allowed_roles]} roli kerak"
#             )
#         return current_user
#
#     return role_checker
#
#
# def get_current_student(current_user: Student = Depends(get_current_user)) -> Student:
#     """Faqat studentlar kirishi mumkin"""
#     if current_user.role != UserRole.STUDENT:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Bu sahifa faqat talabalar uchun"
#         )
#     return current_user
#
#
# def get_current_instructor(current_user: Student = Depends(get_current_user)) -> Student:
#     """Faqat o'qituvchilar kirishi mumkin"""
#     if current_user.role != UserRole.INSTRUCTOR:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Bu sahifa faqat o'qituvchilar uchun"
#         )
#     return current_user
#
#
# def get_current_admin(current_user: Student = Depends(get_current_user)) -> Student:
#     """Faqat adminlar kirishi mumkin"""
#     if current_user.role != UserRole.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Bu sahifa faqat adminlar uchun"
#         )
#     return current_user
#
#
# def instructor_or_admin(current_user: Student = Depends(get_current_user)) -> Student:
#     """O'qituvchi yoki admin kirishi mumkin"""
#     if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Bu sahifa faqat o'qituvchilar va adminlar uchun"
#         )
#     return current_user
