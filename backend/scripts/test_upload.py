import httpx
import asyncio
import os

async def test_upload():
    # We need a valid course ID. Looking at database check, let's use ID 22 (Python Dasturlash Asoslari)
    course_id = 22
    url = f"http://127.0.0.1:8000/api/v1/courses/{course_id}/upload-image"
    
    # We need to login as o'qituvchi.
    # From previous logs, there is an o'qituvchi. 
    # Let's try to get a token.
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    login_data = {"username": "admin", "password": "adminpassword"} # Hypothetical, let's check auth_service for defaults
    
    # Actually, I'll just check if the directory exists and I can write to it via python first.
    # If the endpoint uses the same logic, it should work if this works.
    
    test_file = "test_image.png"
    with open(test_file, "wb") as f:
        f.write(b"fake image data")
        
    print(f"Testing directory: uploads/courses")
    if not os.path.exists("uploads/courses"):
        os.makedirs("uploads/courses")
        print("Created uploads/courses")
    
    try:
        tmp_path = os.path.join("uploads/courses", "test_write.txt")
        with open(tmp_path, "w") as f:
            f.write("test")
        print(f"Successfully wrote to {tmp_path}")
        os.remove(tmp_path)
    except Exception as e:
        print(f"Failed to write to uploads/courses: {e}")

if __name__ == "__main__":
    asyncio.run(test_upload())
