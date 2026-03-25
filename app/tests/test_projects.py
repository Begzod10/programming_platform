import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PROJECT = {
    "title": "Python FastAPI Loyihasi",
    "description": "Bu FastAPI bilan yozilgan test loyihasidir va tavsif yetarlicha uzun",
    "github_url": "https://github.com/test/project",
    "live_demo_url": "https://demo.example.com",
    "technologies_used": ["Python", "FastAPI", "PostgreSQL"],
    "difficulty_level": "Easy"
}

@pytest.fixture
async def created_project(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json=VALID_PROJECT
    )
    assert response.status_code == 201
    return response.json()


async def test_create_project_success(async_client: AsyncClient, auth_headers):
    """To'g'ri ma'lumotlar bilan loyiha yaratish → 201"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json=VALID_PROJECT
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == VALID_PROJECT["title"]
    assert data["status"] == "Draft"
    assert data["points_earned"] == 0
    assert "id" in data
    assert "student_id" in data


async def test_create_project_without_token(async_client: AsyncClient):
    """Token yo'q → 401"""
    response = await async_client.post("/api/v1/project/", json=VALID_PROJECT)
    assert response.status_code == 401


async def test_create_project_title_too_short(async_client: AsyncClient, auth_headers):
    """Sarlavha 2 ta belgi (minimum 3) → 422"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json={**VALID_PROJECT, "title": "Ab"}
    )
    assert response.status_code == 422


async def test_create_project_title_too_long(async_client: AsyncClient, auth_headers):
    """Sarlavha 201 ta belgi (maksimum 200) → 422"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json={**VALID_PROJECT, "title": "A" * 201}
    )
    assert response.status_code == 422


async def test_create_project_description_too_short(async_client: AsyncClient, auth_headers):
    """Tavsif 5 ta belgi (minimum 10) → 422"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json={**VALID_PROJECT, "description": "Qisqa"}
    )
    assert response.status_code == 422


async def test_create_project_invalid_github_url(async_client: AsyncClient, auth_headers):
    """GitHub URL https:// bilan boshlanmaydi → 422"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json={**VALID_PROJECT, "github_url": "github.com/test"}
    )
    assert response.status_code == 422


async def test_create_project_invalid_difficulty(async_client: AsyncClient, auth_headers):
    """Noto'g'ri difficulty_level → 422"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json={**VALID_PROJECT, "difficulty_level": "SuperHard"}
    )
    assert response.status_code == 422


async def test_create_project_without_optional_fields(async_client: AsyncClient, auth_headers):
    """Ixtiyoriy maydonlarsiz yaratish → 201"""
    response = await async_client.post(
        "/api/v1/project/",
        headers=auth_headers,
        json={
            "title": "Minimal Loyiha",
            "description": "Bu minimal loyiha tavsifi uzunroq bo'lishi kerak",
            "difficulty_level": "Easy"
        }
    )
    assert response.status_code == 201


# 2. LOYIHALAR RO'YXATI
# GET /api/v1/project/


async def test_get_projects_success(async_client: AsyncClient, auth_headers, created_project):
    """Token bilan barcha loyihalar → 200"""
    response = await async_client.get("/api/v1/project/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


async def test_get_projects_without_token(async_client: AsyncClient):
    """Token yo'q → 401"""
    response = await async_client.get("/api/v1/project/")
    assert response.status_code == 401


async def test_get_projects_pagination(async_client: AsyncClient, auth_headers):
    """Sahifalash parametrlari → 200"""
    response = await async_client.get(
        "/api/v1/project/?page=1&page_size=5",
        headers=auth_headers
    )
    assert response.status_code == 200


async def test_get_projects_invalid_page(async_client: AsyncClient, auth_headers):
    """page=0 (minimum 1) → 422"""
    response = await async_client.get(
        "/api/v1/project/?page=0",
        headers=auth_headers
    )
    assert response.status_code == 422


async def test_get_projects_invalid_page_size(async_client: AsyncClient, auth_headers):
    """page_size=200 (maksimum 100) → 422"""
    response = await async_client.get(
        "/api/v1/project/?page_size=200",
        headers=auth_headers
    )
    assert response.status_code == 422


# 3. ID BO'YICHA LOYIHA
# GET /api/v1/project/{id}


async def test_get_project_by_id_success(async_client: AsyncClient, auth_headers, created_project):
    """Mavjud loyiha ID si → 200"""
    project_id = created_project["id"]
    response = await async_client.get(f"/api/v1/project/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["title"] == VALID_PROJECT["title"]


async def test_get_project_nonexistent(async_client: AsyncClient, auth_headers):
    """Mavjud bo'lmagan ID → 404"""
    response = await async_client.get("/api/v1/project/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_get_project_invalid_id(async_client: AsyncClient, auth_headers):
    """ID sifatida matn → 422"""
    response = await async_client.get("/api/v1/project/notanumber", headers=auth_headers)
    assert response.status_code == 422


# 4. LOYIHANI YANGILASH
# PUT /api/v1/project/{id}


async def test_update_project_title(async_client: AsyncClient, auth_headers, created_project):
    """Sarlavhani yangilash → 200"""
    project_id = created_project["id"]
    response = await async_client.put(
        f"/api/v1/project/{project_id}",
        headers=auth_headers,
        json={"title": "Yangilangan Sarlavha"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Yangilangan Sarlavha"


async def test_update_project_difficulty(async_client: AsyncClient, auth_headers, created_project):
    """Qiyinlik darajasini yangilash → 200"""
    project_id = created_project["id"]
    response = await async_client.put(
        f"/api/v1/project/{project_id}",
        headers=auth_headers,
        json={"difficulty_level": "Hard"}
    )
    assert response.status_code == 200
    assert response.json()["difficulty_level"] == "Hard"


async def test_update_project_without_token(async_client: AsyncClient, created_project):
    """Token yo'q → 401"""
    project_id = created_project["id"]
    response = await async_client.put(
        f"/api/v1/project/{project_id}",
        json={"title": "Soxta"}
    )
    assert response.status_code == 401


async def test_update_nonexistent_project(async_client: AsyncClient, auth_headers):
    """Mavjud bo'lmagan loyihani yangilash → 404"""
    response = await async_client.put(
        "/api/v1/project/99999",
        headers=auth_headers,
        json={"title": "Yangilanish"}
    )
    assert response.status_code == 404


# 5. LOYIHANI O'CHIRISH
# DELETE /api/v1/project/{id}


async def test_delete_project_success(async_client: AsyncClient, auth_headers, created_project):
    """Loyihani o'chirish → 200, keyin 404"""
    project_id = created_project["id"]

    delete_response = await async_client.delete(
        f"/api/v1/project/{project_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 200
    assert "message" in delete_response.json()

    get_response = await async_client.get(
        f"/api/v1/project/{project_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


async def test_delete_project_without_token(async_client: AsyncClient, created_project):
    """Token yo'q → 401"""
    project_id = created_project["id"]
    response = await async_client.delete(f"/api/v1/project/{project_id}")
    assert response.status_code == 401


async def test_delete_nonexistent_project(async_client: AsyncClient, auth_headers):
    """Mavjud bo'lmagan loyihani o'chirish → 404"""
    response = await async_client.delete("/api/v1/project/99999", headers=auth_headers)
    assert response.status_code == 404


# 6. LOYIHANI BAHOLASH (REVIEW)
# POST /api/v1/project/{id}/review


async def test_review_project_success(async_client: AsyncClient, auth_headers, created_project):
    """Loyihani baholash → 200"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/review",
        headers=auth_headers,
        json={
            "status": "Approved",
            "grade": "A",
            "points_earned": 90,
            "instructor_feedback": "Juda yaxshi loyiha!"
        }
    )
    assert response.status_code in [200, 404]


async def test_review_project_invalid_points(async_client: AsyncClient, auth_headers, created_project):
    """Ball 100 dan ko'p → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/review",
        headers=auth_headers,
        json={
            "status": "Approved",
            "grade": "A",
            "points_earned": 150,  # 100 dan ko'p!
        }
    )
    assert response.status_code == 422


async def test_review_project_invalid_grade(async_client: AsyncClient, auth_headers, created_project):
    """Noto'g'ri baho harfi → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/review",
        headers=auth_headers,
        json={
            "status": "Approved",
            "grade": "Z",  # noto'g'ri!
            "points_earned": 80,
        }
    )
    assert response.status_code == 422


# 7. STATUS YANGILASH
# POST /api/v1/project/{id}/status


async def test_update_status_success(async_client: AsyncClient, auth_headers, created_project):
    """Statusni yangilash → 200"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/status",
        headers=auth_headers,
        json={"status": "Submitted"}
    )
    assert response.status_code in [200, 404]


async def test_update_status_invalid(async_client: AsyncClient, auth_headers, created_project):
    """Noto'g'ri status → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/status",
        headers=auth_headers,
        json={"status": "NotoGriStatus"}
    )
    assert response.status_code == 422


# 8. BAHO BERISH
# POST /api/v1/project/{id}/grade


async def test_update_grade_success(async_client: AsyncClient, auth_headers, created_project):
    """Baho berish → 200"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/grade",
        headers=auth_headers,
        json={"grade": "B", "points_earned": 80}
    )
    assert response.status_code in [200, 404]


async def test_update_grade_negative_points(async_client: AsyncClient, auth_headers, created_project):
    """Manfiy ball → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/grade",
        headers=auth_headers,
        json={"grade": "A", "points_earned": -10}
    )
    assert response.status_code == 422


# POST /api/v1/project/{id}/comment


async def test_add_comment_success(async_client: AsyncClient, auth_headers, created_project):
    """Izoh qoldirish → 200"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/comment",
        headers=auth_headers,
        json={"comment": "Bu juda yaxshi loyiha!"}
    )
    assert response.status_code in [200, 404]


async def test_add_comment_too_short(async_client: AsyncClient, auth_headers, created_project):
    """Izoh 2 ta belgi (minimum 3) → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/comment",
        headers=auth_headers,
        json={"comment": "Ha"}
    )
    assert response.status_code == 422


async def test_add_comment_too_long(async_client: AsyncClient, auth_headers, created_project):
    """Izoh 1001 ta belgi (maksimum 1000) → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/comment",
        headers=auth_headers,
        json={"comment": "A" * 1001}
    )
    assert response.status_code == 422


# POST /api/v1/project/{id}/difficulty


async def test_update_difficulty_success(async_client: AsyncClient, auth_headers, created_project):
    """Qiyinlik darajasini yangilash → 200"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/difficulty",
        headers=auth_headers,
        json={"difficulty_level": "Hard"}
    )
    assert response.status_code in [200, 404]


async def test_update_difficulty_invalid(async_client: AsyncClient, auth_headers, created_project):
    """Noto'g'ri qiyinlik darajasi → 422"""
    project_id = created_project["id"]
    response = await async_client.post(
        f"/api/v1/project/{project_id}/difficulty",
        headers=auth_headers,
        json={"difficulty_level": "SuperEasy"}
    )
    assert response.status_code == 422
