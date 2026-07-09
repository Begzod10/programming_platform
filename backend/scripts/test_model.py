from app.schemas.project import ProjectRead
from app.models.project import Project
from datetime import datetime

data_dict = {
    'id': 1,
    'title': 'Практическое задание',
    'description': 'dcdcdcdcdcdcd',
    'github_url': 'https://test',
    'live_demo_url': 'https://test',
    'technologies_used': '',
    'difficulty_level': 'Easy',
    'project_files': '',
    'student_id': 1,
    'status': 'Draft',
    'points_earned': 0,
    'views_count': 0,
    'likes_count': 0,
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow()
}

p = Project(**data_dict)

try:
    if hasattr(ProjectRead, 'model_validate'):
        read_obj = ProjectRead.model_validate(p)
    else:
        read_obj = ProjectRead.from_orm(p)
    print("READ VALIDATED:", read_obj)
except Exception as e:
    print("ERROR DURING PARSE:", type(e), e)
