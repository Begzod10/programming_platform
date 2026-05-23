from app.db.base_class import Base
from app.models.lesson import Lesson
from app.models.quiz import Quiz, Question, StudentQuizResult
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.dictionary import UserDictionary
__all__ = ["Base", "Lesson", UserDictionary, "Quiz", "Question", "StudentQuizResult", "Exercise", "ExerciseSubmission"]
