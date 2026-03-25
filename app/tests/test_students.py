import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_students(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/students/", headers=auth_headers)
    assert response.status_code == 200


async def test_get_student_by_id(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/students/1", headers=auth_headers)
    assert response.status_code in [200, 404]


async def test_get_student_projects(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/projects/", headers=auth_headers)
    assert response.status_code == 200


async def test_get_project_by_id(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/projects/1", headers=auth_headers)
    assert response.status_code in [200, 404]


# POST
async def test_review_project(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/v1/projects/1/review",
        headers=auth_headers,
        json={
            "status": "Approved",
            "grade": "A",
            "points_earned": 90,
            "instructor_feedback": "Yaxshi!"
        }
    )
    assert response.status_code in [200, 404]


async def test_update_project_status(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/v1/projects/1/status",
        headers=auth_headers,
        json={"status": "Submitted"}
    )
    assert response.status_code in [200, 404]


async def test_update_project_grade(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/v1/projects/1/grade",
        headers=auth_headers,
        json={"grade": "B", "points_earned": 80}
    )
    assert response.status_code in [200, 404]


async def test_update_project_comment(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/v1/projects/1/comment",
        headers=auth_headers,
        json={"comment": "Yaxshi loyiha!"}
    )
    assert response.status_code in [200, 404]


async def test_update_project_difficulty(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/v1/projects/1/difficulty",
        headers=auth_headers,
        json={"difficulty_level": "Hard"}
    )
    assert response.status_code in [200, 404]
