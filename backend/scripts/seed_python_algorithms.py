"""Seed "Python: Algoritmlar va Ma'lumotlar Tuzilmasi" (10 lessons): mirrors
"JavaScript: Algoritmlar va Ma'lumotlar Tuzilmasi" (course 69) lesson-for-
lesson in Python — Big O, LinkedList, Stack/Queue, Binary Search, Sorting
I/II, HashMap, BST, Graph, Capstone. Closes the parity gap: JS has a
dedicated DS&A course, Python's track (Asoslari/Flask/.../Testlash) had none.

Usage:
    cd backend
    python scripts/seed_python_algorithms.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order.

Every lesson is authored bilingually in the same pass: Uzbek content goes
directly into the Lesson/Exercise rows (source_lang='uz'), Russian goes
directly into translation_cache via write_ru_translations.py.

STATUS: fill in LESSON_PLAN status "done" as each lesson's UZ + RU content
is written; run --dry-run after each to review before applying.

If you're using this file as a template for a NEW course: read
write_ru_translations.py's module docstring first — RU translation must
cover every EXERCISE (title/description/hint/options/drag_items+
correct_order), not just the lesson's own fields. Run
`python scripts/check_ru_coverage.py <course_id>` after seeding + RU
translation and treat any reported gap as a bug before considering the
course done. A platform-wide audit found 1,371 exercises across 21
courses where this exact step had been silently skipped.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson_sample import LessonSample  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "Python: Algoritmlar va Ma'lumotlar Tuzilmasi",
    "description": (
        "Big O notatsiyasi, LinkedList, Stack/Queue, Binary Search, "
        "tartiblash algoritmlari, HashMap, Binary Search Tree va Graph — "
        "Python tilida amaliy misollar bilan. Texnik intervyularga "
        "tayyorgarlik va algoritmik fikrlashni rivojlantirish uchun."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 5,
    "max_points": 130,
    "category_id": 8,  # Python
    "prerequisite_course_id": 30,  # Python Asoslari
    "is_active": True,
    "is_published": False,  # flip to True once all 10 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Big O Notatsiyasi",
     "scope": "Time/space complexity, O(1)/O(log n)/O(n)/O(n log n)/O(n^2)/O(2^n)."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Bog'liq ro'yxat (LinkedList)",
     "scope": "Singly/Doubly/Circular LinkedList, append/prepend/delete."},
    {"order": 2, "ref": "L3", "status": "done",
     "title": "3-Stack va Queue",
     "scope": "LIFO/FIFO, push/pop, enqueue/dequeue, balanced parentheses."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-Ikkilik Qidiruv (Binary Search)",
     "scope": "Iterative/recursive binary search, divide and conquer."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Tartiblash I: Bubble, Selection, Insertion Sort",
     "scope": "O(n^2) sorting algorithms, stability."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-Tartiblash II: Merge Sort va Quick Sort",
     "scope": "Divide and conquer sorting, O(n log n), pivot/partition."},
    {"order": 6, "ref": "L7", "status": "done",
     "title": "7-HashMap (Hash Table)",
     "scope": "Hash function, collision resolution, load factor, dict."},
    {"order": 7, "ref": "L8", "status": "done",
     "title": "8-Ikkilik Qidiruv Daraxti (BST)",
     "scope": "BST property, insert/search, inorder/preorder/postorder."},
    {"order": 8, "ref": "L9", "status": "done",
     "title": "9-Graf (Graph)",
     "scope": "Directed/undirected/weighted, adjacency list, BFS/DFS."},
    {"order": 9, "ref": "L10", "status": "done",
     "title": "10-Capstone: Algoritmlar amaliyot",
     "scope": "Combining HashMap + Merge Sort + Binary Search on real data."},
]


L1_TEXT = """\
<h3>Big O Notatsiyasi nima?</h3>
<p>Big O notatsiyasi &mdash; bu algoritmning <strong>vaqt murakkabligi</strong> (time complexity) va <strong>xotira murakkabligi</strong> (space complexity)ni ma'lumotlar hajmi ortishi bilan qanday o'zgarishini tavsiflovchi matematik yozuv usuli. U bizga algoritmning eng yomon holatdagi (worst case) ishlash tezligini baholash imkonini beradi, bu esa turli algoritmlarni bir-biri bilan solishtirish uchun juda muhim.</p>
<p>Dasturchi sifatida siz kodni yozganda nafaqat u to'g'ri ishlashini, balki katta hajmdagi ma'lumotlar bilan ham samarali ishlashini ta'minlashingiz kerak. Masalan, 10 ta elementli ro'yxatda ishlaydigan funksiya 10 million elementli ro'yxatda ham maqbul vaqtda ishlashi kerak.</p>
<h3>Asosiy murakkablik turlari</h3>
<ul>
<li><strong>O(1)</strong> &mdash; Doimiy vaqt (constant time). Ro'yxatning bitta elementiga indeks orqali murojaat qilish.</li>
<li><strong>O(log n)</strong> &mdash; Logarifmik vaqt. Binary Search kabi algoritmlar.</li>
<li><strong>O(n)</strong> &mdash; Chiziqli vaqt. Ro'yxat bo'ylab bitta marta aylanish (loop).</li>
<li><strong>O(n log n)</strong> &mdash; Merge Sort, Quick Sort kabi samarali tartiblash algoritmlari.</li>
<li><strong>O(n^2)</strong> &mdash; Kvadratik vaqt. Ichma-ich ikkita loop (masalan, Bubble Sort).</li>
<li><strong>O(2^n)</strong> &mdash; Eksponensial vaqt. Rekursiv Fibonacci kabi samarasiz algoritmlar.</li>
</ul>
<h3>Murakkablikni solishtirish jadvali</h3>
<table>
<tr><th>Notatsiya</th><th>Nomi</th><th>n=10</th><th>n=1000</th></tr>
<tr><td>O(1)</td><td>Doimiy</td><td>1</td><td>1</td></tr>
<tr><td>O(log n)</td><td>Logarifmik</td><td>~3</td><td>~10</td></tr>
<tr><td>O(n)</td><td>Chiziqli</td><td>10</td><td>1000</td></tr>
<tr><td>O(n log n)</td><td>Log-chiziqli</td><td>~33</td><td>~10000</td></tr>
<tr><td>O(n^2)</td><td>Kvadratik</td><td>100</td><td>1000000</td></tr>
</table>
<p>Quyidagi diagramma murakkablik turlarini o'sish tezligi bo'yicha eng tezdan eng sekingacha tartiblab ko'rsatadi:</p>
<pre class="mermaid">
flowchart TB
  A["O(1) - Doimiy"] --> B["O(log n) - Logarifmik"]
  B --> C["O(n) - Chiziqli"]
  C --> D["O(n log n) - Log-chiziqli"]
  D --> E["O(n^2) - Kvadratik"]
  E --> F["O(2^n) - Eksponensial"]
</pre>
<p>Big O ni to'g'ri tushunish orqali siz kodni optimallashtirish, algoritm tanlash va texnik intervyularda samarali javob berish qobiliyatiga ega bo'lasiz. Har doim eng yomon holatni (worst case) hisobga oling va doimiy koeffitsientlar (constants) hamda kichik hadlarni e'tiborga olmang &mdash; masalan, O(2n) shunchaki O(n) deb yoziladi.</p>
"""

L1_CODE = """\
# Big O notatsiyasi - amaliy misollar

# O(1) - Doimiy vaqt: ro'yxat elementiga indeks orqali murojaat
def get_first_element(arr):
    # Har doim bitta amal, ro'yxat hajmidan qat'i nazar
    return arr[0]


# O(n) - Chiziqli vaqt: ro'yxat bo'ylab bir marta aylanish
def find_max(arr):
    max_val = arr[0]
    for i in range(1, len(arr)):
        # Har bir elementni bitta marta tekshiramiz
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val


# O(n^2) - Kvadratik vaqt: ichma-ich ikkita loop
def has_duplicates(arr):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            # Har bir juftlikni solishtiramiz - taxminan n * n amal
            if arr[i] == arr[j]:
                return True
    return False


# O(log n) - Logarifmik vaqt: binary search
def binary_search(sorted_arr, target):
    left = 0
    right = len(sorted_arr) - 1

    while left <= right:
        # Har safar qidiruv maydonini yarmiga qisqartiramiz
        mid = (left + right) // 2

        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# O(n log n) - samarali tartiblash uchun Python'ning o'rnatilgan sorted()
def sort_numbers(arr):
    # Python Timsort algoritmidan foydalanadi - o'rtacha O(n log n)
    return sorted(arr)


# Amaliyot uchun test
numbers = [5, 3, 8, 1, 9, 2, 7]
print("Max element (O(n)):", find_max(numbers))
print("Duplicates bormi (O(n^2)):", has_duplicates(numbers))

sorted_numbers = sort_numbers(numbers)
print("Tartiblangan (O(n log n)):", sorted_numbers)
print("Binary search natijasi (O(log n)):", binary_search(sorted_numbers, 8))

# Har bir funksiya uchun murakkablikni izohlash muhim,
# chunki bu real loyihalarda performance muammolarini
# oldindan aniqlash imkonini beradi.
"""

L1_EX = [
    {
        "title": "Konstant vaqt murakkabligi",
        "description": "Ro'yxatning bitta elementiga indeks orqali murojaat qilish qanday murakkablikka ega?",
        "exercise_type": "multiple_choice",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Indeks orqali murojaat qilish ro'yxat hajmiga bog'liq emas.",
        "explanation": "arr[0] kabi indeks orqali murojaat har doim bitta amal, ro'yxat hajmidan qat'i nazar — bu O(1), doimiy vaqt.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Ichma-ich loop",
        "description": "Ichma-ich joylashgan ikkita loop odatda qanday murakkablikni beradi?",
        "exercise_type": "multiple_choice",
        "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Har bir tashqi qadam uchun ichki loop to'liq ishga tushadi.",
        "explanation": "Ichma-ich ikkita loop odatda O(n^2) beradi, chunki har bir tashqi iteratsiya uchun ichki loop yana n marta ishga tushadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Samarali tartiblash algoritmlari",
        "description": "Quyidagilardan qaysilari O(n log n) murakkablikka ega samarali tartiblash algoritmlari?",
        "exercise_type": "multiple_choice",
        "options": ["Merge Sort", "Bubble Sort", "Quick Sort", "Selection Sort"],
        "correct_answers": "A,C",
        "is_multiple_select": True,
        "hint": "Ikkitasi 'divide and conquer' tamoyiliga asoslangan.",
        "explanation": "Merge Sort va Quick Sort o'rtacha holatda O(n log n) murakkablikka ega. Bubble Sort va Selection Sort esa O(n^2).",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Binary Search murakkabligi",
        "description": "Binary Search algoritmining vaqt murakkabligini Big O notatsiyasida yozing (masalan: O(log n)).",
        "exercise_type": "text_input",
        "expected_answer": "O(log n)",
        "hint": "Har qadamda qidiruv maydoni yarmiga qisqaradi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Bitta loop murakkabligi",
        "description": "Ro'yxat bo'ylab faqat bitta marta aylanadigan loopning murakkabligini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "O(n)",
        "hint": "Har bir element bir marta ko'riladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Tezlik bo'yicha tartiblash",
        "description": "Murakkablik turlarini eng tezdan eng sekingacha tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["O(n^2)", "O(1)", "O(n log n)", "O(n)"],
        "correct_order": ["O(1)", "O(n)", "O(n log n)", "O(n^2)"],
        "hint": "Doimiy vaqt eng tez, kvadratik vaqt eng sekin.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Binary Search qadamlari",
        "description": "Binary Search algoritmining qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "chap va o'ng chegaralarni belgilash",
            "mid indeksni hisoblash",
            "mid elementni target bilan solishtirish",
            "mos yarmida qidiruvni davom ettirish",
        ],
        "correct_order": [
            "chap va o'ng chegaralarni belgilash",
            "mid indeksni hisoblash",
            "mid elementni target bilan solishtirish",
            "mos yarmida qidiruvni davom ettirish",
        ],
        "hint": "Avval chegaralar, keyin o'rta nuqta, keyin solishtirish.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L2_TEXT = """\
<h3>LinkedList (Bog'liq ro'yxat) nima?</h3>
<p>LinkedList &mdash; bu ma'lumotlarni <strong>node</strong> (tugun) deb ataluvchi alohida elementlar ko'rinishida saqlaydigan chiziqli ma'lumotlar tuzilmasi. Har bir node ikki qismdan iborat: <em>value</em> (qiymat) va <em>next</em> (keyingi nodega ko'rsatkich). Ro'yxatdan (list) farqli o'laroq, LinkedList elementlari xotirada ketma-ket joylashmaydi &mdash; ular ko'rsatkichlar (pointers) orqali bir-biriga bog'lanadi.</p>
<p>Bu xususiyat LinkedListga o'ziga xos afzalliklar beradi: elementni boshiga qo'shish yoki o'chirish O(1) vaqtda amalga oshadi, chunki Python ro'yxatidagi (list) kabi qolgan elementlarni siljitish shart emas.</p>
<h3>LinkedList turlari</h3>
<ul>
<li><strong>Singly LinkedList</strong> &mdash; har bir node faqat keyingi nodega ishora qiladi.</li>
<li><strong>Doubly LinkedList</strong> &mdash; har bir node ham keyingi, ham oldingi nodega ishora qiladi.</li>
<li><strong>Circular LinkedList</strong> &mdash; oxirgi node yana boshiga qaytib bog'lanadi.</li>
</ul>
<h3>Python list va LinkedList taqqoslash jadvali</h3>
<table>
<tr><th>Amal</th><th>Python list</th><th>LinkedList</th></tr>
<tr><td>Indeks bo'yicha o'qish</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>Boshiga qo'shish</td><td>O(n)</td><td>O(1)</td></tr>
<tr><td>Oxiriga qo'shish</td><td>O(1)*</td><td>O(1) (tail bilan)</td></tr>
<tr><td>O'rtadan o'chirish</td><td>O(n)</td><td>O(n) (qidiruv uchun)</td></tr>
<tr><td>Xotira</td><td>Ketma-ket</td><td>Tarqoq (pointer bilan)</td></tr>
</table>
<p>Quyidagi diagramma bog'liq ro'yxatning tuzilishini ko'rsatadi &mdash; har bir node keyingisiga ishora qiladi, oxirgi node esa <code>None</code>ga bog'lanadi:</p>
<pre class="mermaid">
flowchart LR
  Head["Head"] --> A["Node: 10"]
  A --> B["Node: 20"]
  B --> C["Node: 30"]
  C --> D["None"]
</pre>
<p>LinkedList real hayotda navbatlar (queue), steklar (stack), va boshqa murakkab tuzilmalarni (masalan, hash table'dagi chaining) yaratishda asos sifatida ishlatiladi. U Python'da o'rnatilgan tur emas, shuning uchun uni class yordamida o'zimiz yaratishimiz kerak bo'ladi. Bog'liq ro'yxatni tushunish rekursiya va ko'rsatkichlar bilan ishlash mahoratini rivojlantiradi, bu esa keyingi mavzular &mdash; daraxtlar va graflar uchun poydevor bo'lib xizmat qiladi.</p>
"""

L2_CODE = """\
# Singly LinkedList klassi

class ListNode:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    # Ro'yxat oxiriga qo'shish - O(1)
    def append(self, value):
        node = ListNode(value)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.length += 1
        return self

    # Ro'yxat boshiga qo'shish - O(1)
    def prepend(self, value):
        node = ListNode(value)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head = node
        self.length += 1
        return self

    # Elementni o'chirish - O(n)
    def delete(self, value):
        if not self.head:
            return False
        if self.head.value == value:
            self.head = self.head.next
            self.length -= 1
            return True
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                self.length -= 1
                return True
            current = current.next
        return False

    # Ro'yxatni Python list'ga aylantirish (debug uchun qulay)
    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result


# Amaliyot
linked_list = LinkedList()
linked_list.append(10)
linked_list.append(20)
linked_list.prepend(5)
print("Ro'yxat:", linked_list.to_list())  # [5, 10, 20]
linked_list.delete(10)
print("O'chirilgandan keyin:", linked_list.to_list())  # [5, 20]
print("Uzunlik:", linked_list.length)
"""

L2_EX = [
    {
        "title": "Node tuzilishi",
        "description": "LinkedList'dagi bitta node nechta asosiy maydondan iborat bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": ["1", "2", "3", "4"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "value va next.",
        "explanation": "Har bir node ikki asosiy maydondan iborat: value (qiymat) va next (keyingi nodega ko'rsatkich).",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Boshiga qo'shish murakkabligi",
        "description": "Singly LinkedList boshiga element qo'shish qanday murakkablikka ega?",
        "exercise_type": "multiple_choice",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Boshqa elementlarni siljitish shart emas.",
        "explanation": "Yangi node yaratib, uni head'ga bog'lash va head'ni yangilash — bularning barchasi doimiy vaqt talab qiladi, shuning uchun O(1).",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "LinkedList turlari",
        "description": "Quyidagilardan qaysilari LinkedList turlari hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Singly LinkedList", "Doubly LinkedList", "Binary LinkedList", "Circular LinkedList"],
        "correct_answers": "A,B,D",
        "is_multiple_select": True,
        "hint": "\"Binary\" bu yerda mos emas — bu daraxt tushunchasi.",
        "explanation": "LinkedList'ning uchta asosiy turi: Singly, Doubly va Circular. \"Binary LinkedList\" degan tushuncha mavjud emas.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Oxirgi nodening qiymati",
        "description": "Singly LinkedList'dagi oxirgi nodening 'next' maydoni odatda nimaga teng bo'ladi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "None",
        "hint": "Python'da \"yo'qlik\"ni bildiruvchi maxsus qiymat.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Qidiruv murakkabligi",
        "description": "LinkedList'da qiymat bo'yicha qidirish qanday murakkablikka ega? (Big O shaklida yozing)",
        "exercise_type": "text_input",
        "expected_answer": "O(n)",
        "hint": "Har bir nodeni ketma-ket tekshirish kerak bo'lishi mumkin.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Boshiga qo'shish qadamlari",
        "description": "LinkedList boshiga yangi node qo'shish qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "yangi node yaratish",
            "yangi node.next ni eski head'ga bog'lash",
            "head'ni yangi nodega o'tkazish",
            "length'ni birga oshirish",
        ],
        "correct_order": [
            "yangi node yaratish",
            "yangi node.next ni eski head'ga bog'lash",
            "head'ni yangi nodega o'tkazish",
            "length'ni birga oshirish",
        ],
        "hint": "Avval node yaratiladi, keyin bog'lanadi, keyin head yangilanadi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Python list vs LinkedList",
        "description": "Amallarni tegishli ma'lumotlar tuzilmasi bilan (qaysi biri tezroq) mos ravishda tartiblang: eng tez o'qishdan eng tez qo'shishgacha.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Python list: indeks bo'yicha o'qish O(1)",
            "LinkedList: boshiga qo'shish O(1)",
            "Python list: boshiga qo'shish O(n)",
            "LinkedList: indeks bo'yicha o'qish O(n)",
        ],
        "correct_order": [
            "Python list: indeks bo'yicha o'qish O(1)",
            "LinkedList: boshiga qo'shish O(1)",
            "Python list: boshiga qo'shish O(n)",
            "LinkedList: indeks bo'yicha o'qish O(n)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L3_TEXT = """\
<h3>Stack va Queue nima?</h3>
<p>Stack (stek) va Queue (navbat) &mdash; bu ma'lumotlarga kirish tartibi bilan farqlanadigan ikkita fundamental chiziqli ma'lumotlar tuzilmasi. Ular ko'pincha ro'yxat (list) yoki LinkedList asosida qurilgan bo'ladi, lekin ular kirish/chiqish tartibini cheklaydi.</p>
<h3>Stack &mdash; LIFO tamoyili</h3>
<p><strong>Stack</strong> &mdash; <em>LIFO (Last In, First Out)</em> tamoyiliga asoslanadi: oxirgi qo'shilgan element birinchi bo'lib olib tashlanadi. Bu xuddi tarelkalar to'plamiga o'xshaydi &mdash; eng ustidagi tarelkani birinchi olasiz. Asosiy amallar: <code>push</code> (qo'shish) va <code>pop</code> (olib tashlash).</p>
<p>Stack qo'llanilishi: brauzerning "orqaga qaytish" tarixi, funksiya chaqiruvlari (call stack), undo/redo funksiyalari, qavslarning muvofiqligini tekshirish.</p>
<h3>Queue &mdash; FIFO tamoyili</h3>
<p><strong>Queue</strong> &mdash; <em>FIFO (First In, First Out)</em> tamoyiliga asoslanadi: birinchi qo'shilgan element birinchi bo'lib olib tashlanadi. Bu xuddi navbatga o'xshaydi &mdash; birinchi kelgan birinchi xizmat oladi. Asosiy amallar: <code>enqueue</code> (qo'shish) va <code>dequeue</code> (olib tashlash).</p>
<p>Queue qo'llanilishi: chop etish navbatlari (print queue), BFS (Breadth-First Search) algoritmi, so'rovlarni navbat bilan qayta ishlash (task scheduling).</p>
<h3>Solishtirish jadvali</h3>
<table>
<tr><th>Xususiyat</th><th>Stack</th><th>Queue</th></tr>
<tr><td>Tamoyil</td><td>LIFO</td><td>FIFO</td></tr>
<tr><td>Qo'shish amali</td><td>push</td><td>enqueue</td></tr>
<tr><td>Olib tashlash amali</td><td>pop</td><td>dequeue</td></tr>
<tr><td>Murakkablik</td><td>O(1)</td><td>O(1)</td></tr>
<tr><td>Misol</td><td>Call stack</td><td>Print queue</td></tr>
</table>
<p>Quyidagi diagramma ikkala tuzilmaning ishlash tamoyilini ko'rsatadi:</p>
<pre class="mermaid">
flowchart TB
  subgraph Stack["Stack (LIFO)"]
    S1["push(3)"] --> S2["push(2)"] --> S3["push(1)"] --> S4["pop() -> 1"]
  end
  subgraph Queue["Queue (FIFO)"]
    Q1["enqueue(3)"] --> Q2["enqueue(2)"] --> Q3["enqueue(1)"] --> Q4["dequeue() -> 3"]
  end
</pre>
<p>Python'da Stack va Queue uchun maxsus o'rnatilgan tur yo'q, lekin ularni oddiy ro'yxat (list) yordamida <code>append/pop</code> (Stack uchun) orqali amalga oshirish mumkin. Katta hajmdagi ma'lumotlar bilan ishlashda ro'yxatning boshidan olib tashlash (<code>pop(0)</code>) O(n) vaqt olishi mumkinligini yodda tuting, shuning uchun samarali Queue uchun <code>collections.deque</code> (ikki tomonlama navbat) ishlatiladi &mdash; u boshidan va oxiridan O(1) vaqtda qo'shish/olib tashlashni ta'minlaydi.</p>
"""

L3_CODE = """\
from collections import deque


# Stack (LIFO) implementatsiyasi
class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0


# Queue (FIFO) implementatsiyasi - deque bilan samarali
class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, value):
        self.items.append(value)

    def dequeue(self):
        return self.items.popleft()  # O(1) - list.pop(0) O(n) bo'lardi

    def front(self):
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0


# Amaliy misol: Stack yordamida qavslar muvofiqligini tekshirish
def is_balanced(expression):
    stack = Stack()
    pairs = {")": "(", "]": "[", "}": "{"}

    for char in expression:
        if char in "([{":
            stack.push(char)
        elif char in ")]}":
            # Yopuvchi qavsga mos ochuvchi qavs stackning tepasida bo'lishi kerak
            if stack.is_empty() or stack.pop() != pairs[char]:
                return False
    return stack.is_empty()


# Amaliyot
stack = Stack()
stack.push(1)
stack.push(2)
stack.push(3)
print("Stack pop:", stack.pop())  # 3 (LIFO)

queue = Queue()
queue.enqueue("A")
queue.enqueue("B")
queue.enqueue("C")
print("Queue dequeue:", queue.dequeue())  # A (FIFO)

print(is_balanced("{[()]}"))  # True
print(is_balanced("{[(])}"))  # False
"""

L3_EX = [
    {
        "title": "Stack tamoyili",
        "description": "Stack qanday tamoyilga asoslanadi?",
        "exercise_type": "multiple_choice",
        "options": ["FIFO", "LIFO", "Random", "Priority"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Oxirgi qo'shilgan element birinchi bo'lib chiqadi.",
        "explanation": "Stack — LIFO (Last In, First Out) tamoyiliga asoslanadi: oxirgi qo'shilgan element birinchi bo'lib olib tashlanadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Queue amali",
        "description": "Queue'ga element qo'shish uchun qaysi amal ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": ["push", "pop", "enqueue", "peek"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Bu — Queue'ga xos atama.",
        "explanation": "Queue'ga element qo'shish uchun enqueue amali ishlatiladi, olib tashlash uchun esa dequeue.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Stack qo'llanilish sohalari",
        "description": "Quyidagilardan qaysilari Stack qo'llaniladigan real holatlar?",
        "exercise_type": "multiple_choice",
        "options": ["Call stack (funksiya chaqiruvlari)", "Undo/Redo funksiyasi", "Print queue", "Qavslarni tekshirish"],
        "correct_answers": "A,B,D",
        "is_multiple_select": True,
        "hint": "\"Print queue\" nomining o'zida Queue yozilgan.",
        "explanation": "Call stack, undo/redo va qavslarni tekshirish — barchasi Stack (LIFO) mantiqiga asoslanadi. Print queue esa Queue (FIFO) misoli.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Stack'dan element olish",
        "description": "Stack'dan elementni olib tashlash uchun ishlatiladigan metodning nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "pop",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "BFS algoritmi",
        "description": "BFS (Breadth-First Search) algoritmi odatda qaysi tuzilmadan foydalanadi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "queue",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Stack amallari tartibi",
        "description": "push(1), push(2), push(3), pop() amallari bajarilganda natijalarni to'g'ri tartibda joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Stack: [1]",
            "Stack: [1,2]",
            "Stack: [1,2,3]",
            "pop() natijasi: 3, Stack: [1,2]",
        ],
        "correct_order": [
            "Stack: [1]",
            "Stack: [1,2]",
            "Stack: [1,2,3]",
            "pop() natijasi: 3, Stack: [1,2]",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Qavslarni tekshirish algoritmi",
        "description": "Stack yordamida qavslar muvofiqligini tekshirish algoritmi qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "ochuvchi qavsni ko'rsangiz, stackka push qiling",
            "yopuvchi qavsni ko'rsangiz, stack'dan pop qiling",
            "pop qilingan qavs mos kelmasa, False qaytaring",
            "oxirida stack bo'sh bo'lsa, True qaytaring",
        ],
        "correct_order": [
            "ochuvchi qavsni ko'rsangiz, stackka push qiling",
            "yopuvchi qavsni ko'rsangiz, stack'dan pop qiling",
            "pop qilingan qavs mos kelmasa, False qaytaring",
            "oxirida stack bo'sh bo'lsa, True qaytaring",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L4_TEXT = """\
<h3>Binary Search (Ikkilik qidiruv) nima?</h3>
<p>Binary Search &mdash; <strong>tartiblangan</strong> ro'yxatda elementni juda tez topish uchun ishlatiladigan samarali qidiruv algoritmi. U <em>"bo'lib boshqarish" (divide and conquer)</em> tamoyiliga asoslanadi: har bir qadamda qidiruv maydoni yarmiga qisqartiriladi.</p>
<p>Muhim shart: ro'yxat <strong>oldindan tartiblangan</strong> bo'lishi kerak. Aks holda algoritm noto'g'ri natija berishi mumkin.</p>
<h3>Algoritm qanday ishlaydi</h3>
<ul>
<li>Ro'yxatning o'rtasidagi elementni (<code>mid</code>) tanlaymiz.</li>
<li>Agar <code>mid</code> qidirilayotgan qiymatga teng bo'lsa &mdash; topildi.</li>
<li>Agar qidirilayotgan qiymat <code>mid</code>dan kichik bo'lsa &mdash; chap yarmida davom etamiz.</li>
<li>Agar qidirilayotgan qiymat <code>mid</code>dan katta bo'lsa &mdash; o'ng yarmida davom etamiz.</li>
<li>Qidiruv maydoni bo'sh bo'lguncha yoki element topilguncha takrorlaymiz.</li>
</ul>
<h3>Linear Search bilan solishtirish</h3>
<table>
<tr><th>Xususiyat</th><th>Linear Search</th><th>Binary Search</th></tr>
<tr><td>Talab</td><td>Tartiblanmagan bo'lishi mumkin</td><td>Tartiblangan bo'lishi shart</td></tr>
<tr><td>Vaqt murakkabligi</td><td>O(n)</td><td>O(log n)</td></tr>
<tr><td>1,000,000 elementda taxminiy qadamlar</td><td>1,000,000</td><td>~20</td></tr>
<tr><td>Amalga oshirish</td><td>Oddiy loop</td><td>Ikki ko'rsatkich (left/right)</td></tr>
</table>
<p>Quyidagi diagramma binary search jarayonini bosqichma-bosqich ko'rsatadi (target=7 uchun tartiblangan ro'yxatda qidiruv):</p>
<pre class="mermaid">
flowchart TB
  A["left=0, right=6, mid=3"] --> B{"arr[mid] == 7?"}
  B -->|"Ha"| C["Topildi!"]
  B -->|"arr[mid] &lt; 7"| D["left = mid+1, chap tomonni tashlab, o'ngda davom etish"]
  B -->|"arr[mid] &gt; 7"| E["right = mid-1, o'ng tomonni tashlab, chapda davom etish"]
</pre>
<p>Binary Search &mdash; texnik intervyularda eng ko'p so'raladigan algoritmlardan biri. U rekursiv yoki iterativ ko'rinishda yozilishi mumkin. Bundan tashqari, oddiy chiziqli qidiruvdan farqli o'laroq, katta tartiblangan ma'lumotlar to'plamlarida (masalan, bazadagi indekslangan yozuvlar) binary search algoritmi sezilarli darajada tezroq ishlaydi. Python'ning <code>bisect</code> moduli aynan shu algoritmning tayyor, optimallashtirilgan versiyasini taqdim etadi.</p>
"""

L4_CODE = """\
# Binary Search - iterativ variant
def binary_search_iterative(sorted_arr, target):
    left = 0
    right = len(sorted_arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if sorted_arr[mid] == target:
            return mid  # Topildi
        elif sorted_arr[mid] < target:
            left = mid + 1  # O'ng yarimda davom etish
        else:
            right = mid - 1  # Chap yarimda davom etish

    return -1  # Topilmadi


# Binary Search - rekursiv variant
def binary_search_recursive(sorted_arr, target, left=0, right=None):
    if right is None:
        right = len(sorted_arr) - 1

    if left > right:
        return -1  # Baza holati: qidiruv maydoni tugadi

    mid = (left + right) // 2

    if sorted_arr[mid] == target:
        return mid
    elif sorted_arr[mid] < target:
        return binary_search_recursive(sorted_arr, target, mid + 1, right)
    else:
        return binary_search_recursive(sorted_arr, target, left, mid - 1)


# Amaliy misol: birinchi element indeksini topish (lower bound)
def find_first_occurrence(sorted_arr, target):
    left = 0
    right = len(sorted_arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if sorted_arr[mid] == target:
            result = mid
            right = mid - 1  # Chapga davom etib, birinchi uchrashni izlaymiz
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result


# Amaliyot
numbers = [1, 3, 5, 7, 9, 11, 13, 15]
print("Iterativ qidiruv (7):", binary_search_iterative(numbers, 7))
print("Rekursiv qidiruv (13):", binary_search_recursive(numbers, 13))
print("Topilmagan qiymat (4):", binary_search_iterative(numbers, 4))

with_duplicates = [1, 2, 2, 2, 3, 4, 5]
print("Birinchi uchrash (2):", find_first_occurrence(with_duplicates, 2))
"""

L4_EX = [
    {
        "title": "Binary Search sharti",
        "description": "Binary Search algoritmi ishlashi uchun ro'yxat qanday bo'lishi shart?",
        "exercise_type": "multiple_choice",
        "options": ["Tasodifiy", "Tartiblangan", "Takrorlanmas", "Manfiy sonlardan iborat"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Algoritm chap/o'ng qismga bo'lish orqali ishlaydi.",
        "explanation": "Binary Search faqat tartiblangan ro'yxatda to'g'ri ishlaydi, chunki u qiymatlarni solishtirib qidiruv maydonini yarmiga qisqartiradi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Binary Search murakkabligi",
        "description": "Binary Search algoritmining vaqt murakkabligi qanday?",
        "exercise_type": "multiple_choice",
        "options": ["O(n)", "O(n^2)", "O(log n)", "O(1)"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Har qadamda qidiruv maydoni yarmiga qisqaradi.",
        "explanation": "Binary Search har qadamda qidiruv maydonini yarmiga qisqartiradi, shuning uchun uning murakkabligi O(log n).",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Binary Search xususiyatlari",
        "description": "Quyidagilardan qaysilari Binary Search algoritmiga tegishli to'g'ri xususiyatlar?",
        "exercise_type": "multiple_choice",
        "options": [
            "Divide and conquer tamoyiliga asoslangan",
            "Har doim tartiblanmagan ro'yxatda ishlaydi",
            "Rekursiv yoki iterativ yozilishi mumkin",
            "Har qadamda qidiruv maydonini yarmiga qisqartiradi",
        ],
        "correct_answers": "A,C,D",
        "is_multiple_select": True,
        "hint": "Ikkinchi variant algoritmning asosiy talabiga zid.",
        "explanation": "Binary Search divide and conquer tamoyiliga asoslangan, rekursiv yoki iterativ yozilishi mumkin va har qadamda qidiruv maydonini yarmiga qisqartiradi. Lekin u faqat TARTIBLANGAN ro'yxatda ishlaydi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "O'rta indeks formulasi",
        "description": "left va right ko'rsatkichlari yordamida mid indeksni hisoblash formulasini yozing (Python sintaksisida, masalan: (left + right) // 2).",
        "exercise_type": "text_input",
        "expected_answer": "(left + right) // 2",
        "hint": "Python'da butun sonli bo'lish operatori // ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "1,000,000 elementda qadamlar",
        "description": "1,000,000 elementli tartiblangan ro'yxatda Binary Search bilan qidiruv taxminan nechta qadamda amalga oshadi? (raqam bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "20",
        "hint": "log2(1,000,000) ni hisoblang.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Binary Search qadamlari tartibi",
        "description": "Binary Search algoritmining bajarilish qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "left=0, right=length-1 belgilash",
            "mid indeksni hisoblash",
            "arr[mid] ni target bilan solishtirish",
            "left yoki right ni yangilab, takrorlash",
        ],
        "correct_order": [
            "left=0, right=length-1 belgilash",
            "mid indeksni hisoblash",
            "arr[mid] ni target bilan solishtirish",
            "left yoki right ni yangilab, takrorlash",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Linear vs Binary tezlik",
        "description": "Ro'yxat hajmi ortishi bilan qidiruv usullarini sekindan tezgacha tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["Binary Search: O(log n)", "Linear Search: O(n)"],
        "correct_order": ["Linear Search: O(n)", "Binary Search: O(log n)"],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L5_TEXT = """\
<h3>Oddiy tartiblash algoritmlari</h3>
<p>Tartiblash (sorting) &mdash; ma'lumotlar to'plamini muayyan tartibda (o'suvchi yoki kamayuvchi) joylashtirish jarayoni. Bubble Sort, Selection Sort va Insertion Sort &mdash; eng oddiy va tushunish uchun eng qulay tartiblash algoritmlari hisoblanadi. Ularning barchasi eng yomon holatda O(n^2) murakkablikka ega, shuning uchun katta hajmdagi ma'lumotlar uchun samarasiz, lekin kichik ro'yxatlarda va o'quv maqsadida juda foydali.</p>
<h3>Bubble Sort</h3>
<p>Qo'shni ikkita elementni solishtirib, agar ular noto'g'ri tartibda bo'lsa, ularni almashtiradi (swap). Bu jarayon ro'yxat butunlay tartiblanguncha takrorlanadi. Har bir "pass"da eng katta element o'z o'rniga "ko'tariladi" (bubble up), shundan nomi kelib chiqqan.</p>
<h3>Selection Sort</h3>
<p>Har bir qadamda tartiblanmagan qismdan eng kichik elementni topib, uni tartiblangan qismning oxiriga qo'yadi. Bubble Sort'dan farqli o'laroq, kamroq almashtirish (swap) amalga oshiradi &mdash; har bir pass'da faqat bitta swap.</p>
<h3>Insertion Sort</h3>
<p>Ro'yxatni tartiblangan va tartiblanmagan ikki qismga bo'lib, tartiblanmagan qismdagi har bir elementni tartiblangan qismning to'g'ri joyiga "kiritadi" (insert). Kichik yoki deyarli tartiblangan ro'yxatlar uchun ayniqsa samarali &mdash; bunday holatlarda tezligi O(n) ga yaqinlashadi.</p>
<h3>Solishtirish jadvali</h3>
<table>
<tr><th>Algoritm</th><th>O'rtacha holat</th><th>Eng yomon holat</th><th>Barqarorlik</th></tr>
<tr><td>Bubble Sort</td><td>O(n^2)</td><td>O(n^2)</td><td>Barqaror</td></tr>
<tr><td>Selection Sort</td><td>O(n^2)</td><td>O(n^2)</td><td>Barqaror emas</td></tr>
<tr><td>Insertion Sort</td><td>O(n^2)</td><td>O(n^2)</td><td>Barqaror</td></tr>
</table>
<p>Quyidagi diagramma Bubble Sort'ning bir necha o'tishini (pass) ko'rsatadi:</p>
<pre class="mermaid">
flowchart TB
  A["[5,3,8,1]"] --> B["1-pass: [3,5,1,8]"]
  B --> C["2-pass: [3,1,5,8]"]
  C --> D["3-pass: [1,3,5,8] - Tartiblangan"]
</pre>
<p>Bu uchala algoritm ham "comparison-based" (solishtirishga asoslangan) tartiblash algoritmlari bo'lib, ular real loyihalarda kamdan-kam qo'llaniladi, chunki Python'ning o'rnatilgan <code>sorted()</code> funksiyasi va Merge/Quick Sort kabi algoritmlar ancha samarali. Ammo ularni tushunish algoritmik fikrlashni rivojlantirish uchun juda muhim va texnik intervyularda tez-tez so'raladi. Barqarorlik (stability) &mdash; teng qiymatga ega elementlarning nisbiy tartibi saqlanishini anglatadi, bu ba'zi amaliy holatlarda muhim ahamiyatga ega.</p>
"""

L5_CODE = """\
# Bubble Sort - qo'shni elementlarni solishtirib almashtirish
def bubble_sort(arr):
    result = arr.copy()
    n = len(result)

    for i in range(n - 1):
        swapped = False
        # Har bir pass'da eng katta element oxiriga "ko'tariladi"
        for j in range(n - 1 - i):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        # Agar hech qanday almashtirish bo'lmasa, ro'yxat allaqachon tartiblangan
        if not swapped:
            break
    return result


# Selection Sort - eng kichik elementni tanlab joylashtirish
def selection_sort(arr):
    result = arr.copy()
    n = len(result)

    for i in range(n - 1):
        min_index = i
        # Tartiblanmagan qismdan eng kichik elementni topish
        for j in range(i + 1, n):
            if result[j] < result[min_index]:
                min_index = j
        if min_index != i:
            result[i], result[min_index] = result[min_index], result[i]
    return result


# Insertion Sort - har bir elementni to'g'ri joyga kiritish
def insertion_sort(arr):
    result = arr.copy()

    for i in range(1, len(result)):
        current = result[i]
        j = i - 1

        # current'dan katta elementlarni bir pozitsiyaga suramiz
        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


# Amaliyot
data = [5, 3, 8, 1, 9, 2, 7]
print("Bubble Sort:", bubble_sort(data))
print("Selection Sort:", selection_sort(data))
print("Insertion Sort:", insertion_sort(data))

# Deyarli tartiblangan ro'yxatda Insertion Sort tezroq ishlaydi
almost_sorted = [1, 2, 4, 3, 5, 6, 7]
print("Deyarli tartiblangan:", insertion_sort(almost_sorted))
"""

L5_EX = [
    {
        "title": "Bubble Sort tamoyili",
        "description": "Bubble Sort algoritmi asosan qanday amalga tayanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Qo'shni elementlarni solishtirib almashtirish", "Rekursiya", "Xeshlash", "Ikkiga bo'lish"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Nomining o'zida \"ko'tarilish\" (bubble up) ma'nosi bor.",
        "explanation": "Bubble Sort qo'shni ikkita elementni solishtirib, noto'g'ri tartibda bo'lsa, ularni almashtiradi — shu jarayon takrorlanaveradi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Uchala algoritm murakkabligi",
        "description": "Bubble, Selection va Insertion Sort algoritmlarining eng yomon holatdagi murakkabligi qanday?",
        "exercise_type": "multiple_choice",
        "options": ["O(n)", "O(n log n)", "O(n^2)", "O(2^n)"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Uchalasi ham ichma-ich loop ishlatadi.",
        "explanation": "Bubble, Selection va Insertion Sort — uchalasi ham eng yomon holatda O(n^2) murakkablikka ega.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Barqaror algoritmlar",
        "description": "Quyidagi algoritmlardan qaysilari barqaror (stable) tartiblash algoritmi hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Bubble Sort", "Selection Sort", "Insertion Sort", "Quick Sort (odatiy)"],
        "correct_answers": "A,C",
        "is_multiple_select": True,
        "hint": "Selection Sort elementlarni uzoq masofaga almashtirgani uchun barqaror emas.",
        "explanation": "Bubble Sort va Insertion Sort barqaror algoritmlar hisoblanadi, chunki ular teng qiymatlarning nisbiy tartibini saqlaydi. Selection Sort va odatiy Quick Sort esa barqaror emas.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Selection Sort'da swap soni",
        "description": "Selection Sort algoritmi har bir pass'da odatda nechta almashtirish (swap) amalga oshiradi? (raqam bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "1",
        "hint": "Faqat eng kichik element topilgach, bitta joy almashtiriladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Deyarli tartiblangan ro'yxat",
        "description": "Deyarli tartiblangan ro'yxatlar uchun eng samarali oddiy tartiblash algoritmi nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "Insertion Sort",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Bubble Sort qadamlari",
        "description": "Bubble Sort algoritmining bir pass ichidagi qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "ikkita qo'shni elementni solishtirish",
            "agar tartib noto'g'ri bo'lsa, ularni almashtirish",
            "keyingi juftlikka o'tish",
            "ro'yxat oxiriga yetganda pass tugaydi",
        ],
        "correct_order": [
            "ikkita qo'shni elementni solishtirish",
            "agar tartib noto'g'ri bo'lsa, ularni almashtirish",
            "keyingi juftlikka o'tish",
            "ro'yxat oxiriga yetganda pass tugaydi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Algoritmlarni tezlik bo'yicha moslashtirish",
        "description": "Kichik ro'yxatlar uchun algoritmlarni tavsiya etilgan holatlar bilan mos ravishda joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Insertion Sort - deyarli tartiblangan ma'lumotlar uchun",
            "Selection Sort - swap sonini minimallashtirish kerak bo'lganda",
            "Bubble Sort - o'qitish va tushunish uchun",
        ],
        "correct_order": [
            "Insertion Sort - deyarli tartiblangan ma'lumotlar uchun",
            "Selection Sort - swap sonini minimallashtirish kerak bo'lganda",
            "Bubble Sort - o'qitish va tushunish uchun",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L6_TEXT = """\
<h3>Samarali tartiblash: Merge Sort va Quick Sort</h3>
<p>Merge Sort va Quick Sort &mdash; <em>"bo'lib boshqarish" (divide and conquer)</em> tamoyiliga asoslangan, sanoat darajasida keng qo'llaniladigan samarali tartiblash algoritmlari. Ularning ikkalasi ham o'rtacha holatda O(n log n) murakkablikka ega bo'lib, bu Bubble/Selection/Insertion Sort'ning O(n^2) murakkabligidan sezilarli darajada tezroq.</p>
<h3>Merge Sort</h3>
<p>Ro'yxatni rekursiv ravishda ikkiga bo'lib, har bir yarmi bittalik elementgacha bo'linadi, so'ngra ikkita tartiblangan yarmi <code>merge</code> funksiyasi orqali birlashtiriladi. Merge Sort har doim, hatto eng yomon holatda ham, O(n log n) kafolatlaydi, lekin qo'shimcha O(n) xotira talab qiladi.</p>
<h3>Quick Sort</h3>
<p>Ro'yxatdan <em>pivot</em> elementni tanlab, undan kichik elementlarni chapga, kattalarini o'ngga ajratadi (partition), so'ngra har ikki qismni rekursiv tartiblaydi. Quick Sort o'rtacha holatda juda tez (O(n log n)) ishlaydi va kam qo'shimcha xotira talab qiladi (in-place), lekin noto'g'ri pivot tanlanganda eng yomon holatda O(n^2) ga tushib qolishi mumkin.</p>
<h3>Solishtirish jadvali</h3>
<table>
<tr><th>Xususiyat</th><th>Merge Sort</th><th>Quick Sort</th></tr>
<tr><td>O'rtacha holat</td><td>O(n log n)</td><td>O(n log n)</td></tr>
<tr><td>Eng yomon holat</td><td>O(n log n)</td><td>O(n^2)</td></tr>
<tr><td>Xotira</td><td>O(n) qo'shimcha</td><td>O(log n) (in-place)</td></tr>
<tr><td>Barqarorlik</td><td>Barqaror</td><td>Barqaror emas</td></tr>
</table>
<p>Quyidagi diagramma Merge Sort'ning rekursiya daraxtini ko'rsatadi:</p>
<pre class="mermaid">
flowchart TB
  A["[8,3,7,4,2,9,1,5]"] --> B["[8,3,7,4]"]
  A --> C["[2,9,1,5]"]
  B --> D["[8,3]"] & E["[7,4]"]
  C --> F["[2,9]"] & G["[1,5]"]
  D --> H["merge -> [3,8]"]
  E --> I["merge -> [4,7]"]
  F --> J["merge -> [2,9]"]
  G --> K["merge -> [1,5]"]
</pre>
<p>Amaliyotda Python'ning o'rnatilgan <code>sorted()</code> funksiyasi Timsort (Merge Sort va Insertion Sort gibridi) algoritmidan foydalanadi. Katta ma'lumotlar bazalari va tizimlarda Quick Sort ko'pincha o'rtacha holatda tezligi tufayli tanlanadi, lekin xotira cheklovlari yoki barqarorlik talab qilinganda Merge Sort afzal ko'riladi.</p>
"""

L6_CODE = """\
# Merge Sort - divide and conquer
def merge_sort(arr):
    if len(arr) <= 1:
        return arr  # Baza holati

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


# Ikkita tartiblangan ro'yxatni birlashtirish
def merge(left, right):
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Qolgan elementlarni qo'shish
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# Quick Sort - pivot orqali bo'lish (partition)
def quick_sort(arr):
    if len(arr) <= 1:
        return arr  # Baza holati

    pivot = arr[-1]
    left = []
    right = []

    for i in range(len(arr) - 1):
        if arr[i] < pivot:
            left.append(arr[i])
        else:
            right.append(arr[i])

    return quick_sort(left) + [pivot] + quick_sort(right)


# Quick Sort - in-place (xotirani tejaydigan) variant
def quick_sort_in_place(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_index = partition(arr, low, high)
        quick_sort_in_place(arr, low, pivot_index - 1)
        quick_sort_in_place(arr, pivot_index + 1, high)
    return arr


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# Amaliyot
data = [8, 3, 7, 4, 2, 9, 1, 5, 6]

print("Merge Sort:", merge_sort(data))
print("Quick Sort:", quick_sort(data))
print("Quick Sort (in-place):", quick_sort_in_place(data.copy()))
"""

L6_EX = [
    {
        "title": "Umumiy strategiya",
        "description": "Merge Sort va Quick Sort qaysi umumiy strategiyadan foydalanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Greedy", "Divide and Conquer", "Dynamic Programming", "Brute Force"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ro'yxatni kichik qismlarga bo'lib, alohida hal qilishadi.",
        "explanation": "Merge Sort va Quick Sort ikkalasi ham \"bo'lib boshqarish\" (divide and conquer) tamoyiliga asoslangan.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Merge Sort xotira murakkabligi",
        "description": "Merge Sort odatda qanday qo'shimcha xotira murakkabligiga ega?",
        "exercise_type": "multiple_choice",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Birlashtirish (merge) uchun yangi ro'yxatlar yaratiladi.",
        "explanation": "Merge Sort ikkita yarmini birlashtirish uchun qo'shimcha O(n) xotira talab qiladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Quick Sort xususiyatlari",
        "description": "Quick Sort haqida qaysi tasdiqlar to'g'ri?",
        "exercise_type": "multiple_choice",
        "options": [
            "O'rtacha holatda O(n log n) murakkablikka ega",
            "Har doim eng yomon holatda ham O(n log n) ga ega",
            "Pivot elementdan foydalanadi",
            "Har doim barqaror (stable) algoritm",
        ],
        "correct_answers": "A,C",
        "is_multiple_select": True,
        "hint": "Noto'g'ri pivot tanlansa, eng yomon holat yomonlashadi.",
        "explanation": "Quick Sort o'rtacha holatda O(n log n) va pivot elementdan foydalanadi. Lekin eng yomon holatda O(n^2) ga tushishi mumkin, va odatda barqaror emas.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Quick Sort eng yomon holat",
        "description": "Quick Sort'ning eng yomon holatdagi vaqt murakkabligini Big O ko'rinishida yozing.",
        "exercise_type": "text_input",
        "expected_answer": "O(n^2)",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Merge funksiyasi",
        "description": "Merge Sort'da ikkita allaqachon tartiblangan yarmini birlashtiruvchi funksiya odatda qanday nomlanadi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "merge",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Merge Sort qadamlari",
        "description": "Merge Sort algoritmining asosiy qadamlarini to'g'ri tartibda joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Ro'yxatni ikkiga bo'lish",
            "Har bir yarmini rekursiv tartiblash",
            "Ikkita tartiblangan yarmini birlashtirish (merge)",
        ],
        "correct_order": [
            "Ro'yxatni ikkiga bo'lish",
            "Har bir yarmini rekursiv tartiblash",
            "Ikkita tartiblangan yarmini birlashtirish (merge)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Algoritmlarni xususiyat bo'yicha moslashtirish",
        "description": "Algoritmlarni ularga mos tavsifi bilan tartibga soling: avval Merge Sort (kafolatlangan O(n log n)), keyin Quick Sort (o'rtacha tez, lekin eng yomon holatda O(n^2)).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Kafolatlangan O(n log n), qo'shimcha xotira ko'proq",
            "O'rtacha tez, lekin eng yomon holatda O(n^2)",
        ],
        "correct_order": [
            "Kafolatlangan O(n log n), qo'shimcha xotira ko'proq",
            "O'rtacha tez, lekin eng yomon holatda O(n^2)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L7_TEXT = """\
<h3>HashMap (Hash Table) nima?</h3>
<p>HashMap &mdash; kalit-qiymat (key-value) juftliklarini saqlaydigan va ularga <strong>o'rtacha O(1)</strong> vaqtda kirish imkonini beruvchi ma'lumotlar tuzilmasi. Bu uning eng katta afzalligi &mdash; ro'yxat yoki LinkedList'da qidiruv O(n) vaqt olsa, HashMap'da bu deyarli bir zumda amalga oshadi.</p>
<h3>Qanday ishlaydi</h3>
<p>HashMap ichida <strong>hash funksiyasi</strong> har bir kalitni raqamli indeksga aylantiradi, bu indeks esa ro'yxat (bucket'lar to'plami)dagi o'rinni bildiradi. Masalan, "email" kalitini hash funksiyasi 42-indeksga aylantirishi mumkin, va qiymat aynan shu joyga saqlanadi.</p>
<h3>Kolliziyalarni hal qilish (Collision Resolution)</h3>
<ul>
<li><strong>Chaining</strong> &mdash; bir xil indeksga tushgan barcha elementlar shu bucket ichida LinkedList (yoki ro'yxat) sifatida saqlanadi.</li>
<li><strong>Open Addressing</strong> &mdash; kolliziya yuz berganda, algoritm keyingi bo'sh joyni qidiradi (masalan, linear probing).</li>
</ul>
<p><strong>Load factor</strong> (yuklama koeffitsienti) &mdash; elementlar sonining bucket'lar soniga nisbati. Yuqori load factor ko'proq kolliziyaga olib keladi, shuning uchun HashMap odatda ma'lum chegaradan oshganda o'lchamini kattalashtiradi (resize).</p>
<h3>Solishtirish jadvali</h3>
<table>
<tr><th>Amal</th><th>O'rtacha holat</th><th>Eng yomon holat</th></tr>
<tr><td>Qo'shish (set)</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>Qidirish (get)</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>O'chirish (delete)</td><td>O(1)</td><td>O(n)</td></tr>
</table>
<p>Quyidagi diagramma hash table ichidagi bucket'lar tuzilishini ko'rsatadi (chaining usuli bilan):</p>
<pre class="mermaid">
flowchart LR
  H["hash('email')=2"] --> B0["Bucket 0: bo'sh"]
  H --> B1["Bucket 1: bo'sh"]
  H --> B2["Bucket 2: [email -> user@site.com]"]
  H --> B3["Bucket 3: [age -> 25] -> [name -> Ali]"]
</pre>
<p>Python'da HashMap tabiati <code>dict</code> orqali amalga oshiriladi. <code>dict</code> obyekti kalit sifatida istalgan o'zgarmas (immutable) turdan foydalanish, qulay iteratsiya va o'lchamni <code>len()</code> orqali olish imkonini beradi. Python'ning o'rnatilgan <code>dict</code>i ichida aynan shu darsda ko'rgan hash jadval mantig'i ishlatiladi.</p>
"""

L7_CODE = """\
# Oddiy HashMap implementatsiyasi (chaining usuli bilan)

class HashMap:
    def __init__(self, size=16):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    # Oddiy hash funksiyasi - kalitni raqamli indeksga aylantiradi
    def _hash(self, key):
        hash_value = 0
        string_key = str(key)
        for i, char in enumerate(string_key):
            hash_value = (hash_value + ord(char) * (i + 1)) % self.size
        return hash_value

    # Kalit-qiymat juftligini qo'shish yoki yangilash - O(1) o'rtacha
    def set(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]

        for entry in bucket:
            if entry[0] == key:
                entry[1] = value  # Mavjud kalitni yangilash
                return
        bucket.append([key, value])  # Yangi juftlik qo'shish

    # Kalit bo'yicha qiymatni olish - O(1) o'rtacha
    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for entry in bucket:
            if entry[0] == key:
                return entry[1]
        return None

    # Kalitni o'chirish - O(1) o'rtacha
    def delete(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, entry in enumerate(bucket):
            if entry[0] == key:
                bucket.pop(i)
                return True
        return False

    def has(self, key):
        return self.get(key) is not None


# Amaliyot
my_map = HashMap()
my_map.set("name", "Ali")
my_map.set("age", 25)
my_map.set("email", "ali@example.com")

print("name:", my_map.get("name"))  # Ali
print("age:", my_map.get("age"))  # 25
print("has phone:", my_map.has("phone"))  # False

my_map.delete("age")
print("age o'chirilgandan keyin:", my_map.get("age"))  # None

# Python'ning o'rnatilgan dict bilan solishtirish
builtin_dict = {}
builtin_dict["name"] = "Ali"
print("Built-in dict:", builtin_dict["name"])
"""

L7_EX = [
    {
        "title": "HashMap murakkabligi",
        "description": "HashMap'da kalit bo'yicha qiymatni olish o'rtacha holatda qanday murakkablikka ega?",
        "exercise_type": "multiple_choice",
        "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Hash funksiyasi to'g'ridan-to'g'ri indeksni hisoblab beradi.",
        "explanation": "HashMap'da kalit bo'yicha qidirish o'rtacha holatda O(1), chunki hash funksiyasi kalitni to'g'ridan-to'g'ri indeksga aylantiradi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Kolliziya nima",
        "description": "HashMap'da 'kolliziya' (collision) atamasi nimani anglatadi?",
        "exercise_type": "multiple_choice",
        "options": ["Ikki xil kalit bir xil indeksga tushishi", "HashMap to'lib qolishi", "Kalit topilmasligi", "Qiymat noto'g'ri turda bo'lishi"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bu — hash funksiyasi natijasi bilan bog'liq.",
        "explanation": "Kolliziya — ikki xil kalitning hash funksiyasi orqali bir xil indeksga tushishini bildiradi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Kolliziya usullari",
        "description": "Quyidagilardan qaysilari kolliziyani hal qilish usullari hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Chaining", "Open Addressing", "Binary Search", "Merge Sort"],
        "correct_answers": "A,B",
        "is_multiple_select": True,
        "hint": "Ikkitasi HashMap'ga xos, ikkitasi boshqa mavzularga tegishli.",
        "explanation": "Chaining va Open Addressing — HashMap'da kolliziyani hal qilishning ikki asosiy usuli.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Kalitni raqamga aylantirish",
        "description": "HashMap ichida kalitni raqamli indeksga aylantiruvchi funksiya qanday nomlanadi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "hash",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Elementlar/bucket nisbati",
        "description": "Elementlar sonining bucket'lar soniga nisbatini bildiruvchi atamani yozing.",
        "exercise_type": "text_input",
        "expected_answer": "load factor",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "HashMap.set() qadamlari",
        "description": "HashMap'ga yangi kalit-qiymat qo'shish (set) jarayonining qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "kalitni hash funksiyasidan o'tkazib indeks olish",
            "mos bucket'ni topish",
            "bucket ichida shu kalit mavjudligini tekshirish",
            "mavjud bo'lsa yangilash, bo'lmasa yangi juftlik qo'shish",
        ],
        "correct_order": [
            "kalitni hash funksiyasidan o'tkazib indeks olish",
            "mos bucket'ni topish",
            "bucket ichida shu kalit mavjudligini tekshirish",
            "mavjud bo'lsa yangilash, bo'lmasa yangi juftlik qo'shish",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Tuzilma va murakkablik mosligi",
        "description": "Ma'lumotlar tuzilmalarini o'rtacha qidiruv murakkabligiga mos ravishda joylashtiring: eng tezdan eng sekingacha.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "LinkedList qidiruvi O(n)",
            "HashMap qidiruvi O(1)",
            "Binary Search O(log n)",
        ],
        "correct_order": [
            "HashMap qidiruvi O(1)",
            "Binary Search O(log n)",
            "LinkedList qidiruvi O(n)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L8_TEXT = """\
<h3>Binary Search Tree (BST) nima?</h3>
<p>Binary Search Tree (BST) &mdash; har bir node'i maksimum ikkita farzandga (chap va o'ng) ega bo'lgan, va muhim <strong>tartib xususiyatiga</strong> (BST property) ega bo'lgan daraxt ko'rinishidagi ma'lumotlar tuzilmasi: <em>chap farzand qiymati ota-nodedan kichik, o'ng farzand qiymati esa katta</em> bo'lishi shart.</p>
<p>Bu xususiyat tufayli BST'da qidirish, qo'shish va o'chirish amallari o'rtacha holatda <strong>O(log n)</strong> vaqtda amalga oshadi &mdash; xuddi Binary Search kabi, lekin dinamik (o'zgaruvchan) ma'lumotlar uchun.</p>
<h3>Daraxt aylanib chiqish turlari (Traversal)</h3>
<ul>
<li><strong>Inorder</strong> (chap &rarr; ildiz &rarr; o'ng) &mdash; elementlarni o'suvchi tartibda beradi.</li>
<li><strong>Preorder</strong> (ildiz &rarr; chap &rarr; o'ng) &mdash; daraxt strukturasini nusxalash uchun foydali.</li>
<li><strong>Postorder</strong> (chap &rarr; o'ng &rarr; ildiz) &mdash; node'larni o'chirishda foydali.</li>
</ul>
<h3>Murakkablik jadvali</h3>
<table>
<tr><th>Amal</th><th>O'rtacha holat (balanslangan)</th><th>Eng yomon holat (nomutanosib)</th></tr>
<tr><td>Qidirish</td><td>O(log n)</td><td>O(n)</td></tr>
<tr><td>Qo'shish</td><td>O(log n)</td><td>O(n)</td></tr>
<tr><td>O'chirish</td><td>O(log n)</td><td>O(n)</td></tr>
</table>
<p>Eng yomon holat daraxt "nomutanosib" (skewed) bo'lganda, ya'ni har bir node faqat bitta farzandga ega bo'lib, aslida LinkedList'ga aylanganda yuzaga keladi. Shuning uchun amaliyotda AVL Tree yoki Red-Black Tree kabi <em>o'z-o'zini balanslaydigan</em> (self-balancing) daraxtlar qo'llaniladi.</p>
<p>Quyidagi diagramma tipik BST tuzilishini ko'rsatadi:</p>
<pre class="mermaid">
flowchart TB
  A["8"] --> B["3"]
  A --> C["10"]
  B --> D["1"]
  B --> E["6"]
  C --> F["14"]
</pre>
<p>BST daraxt tuzilmalari, saralangan ma'lumotlar to'plami, avtomatik to'ldirish (autocomplete) funksiyalari va diapazon bo'yicha qidiruv (range query) kabi vazifalarda keng qo'llaniladi. Rekursiya BST bilan ishlashda asosiy vosita hisoblanadi, chunki har bir kichik daraxt (subtree) o'zi ham BST xususiyatiga ega bo'ladi.</p>
"""

L8_CODE = """\
# Binary Search Tree (BST) implementatsiyasi

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    # Yangi qiymat qo'shish - O(log n) o'rtacha
    def insert(self, value):
        new_node = TreeNode(value)
        if not self.root:
            self.root = new_node
            return self

        current = self.root
        while True:
            if value < current.value:
                if not current.left:
                    current.left = new_node
                    return self
                current = current.left
            else:
                if not current.right:
                    current.right = new_node
                    return self
                current = current.right

    # Qiymatni qidirish - O(log n) o'rtacha
    def search(self, value):
        current = self.root
        while current:
            if value == current.value:
                return True
            current = current.left if value < current.value else current.right
        return False

    # Inorder traversal - o'suvchi tartibda barcha qiymatlarni qaytaradi
    def inorder_traversal(self, node="root", result=None):
        if result is None:
            result = []
        if node == "root":
            node = self.root
        if node:
            self.inorder_traversal(node.left, result)
            result.append(node.value)
            self.inorder_traversal(node.right, result)
        return result

    # Daraxtning minimal qiymatini topish
    def find_min(self, node="root"):
        if node == "root":
            node = self.root
        while node and node.left:
            node = node.left
        return node.value if node else None


# Amaliyot
bst = BinarySearchTree()
for value in [8, 3, 10, 1, 6, 14, 4, 7]:
    bst.insert(value)

print("Inorder (tartiblangan):", bst.inorder_traversal())
print("6 ni qidirish:", bst.search(6))  # True
print("100 ni qidirish:", bst.search(100))  # False
print("Minimal qiymat:", bst.find_min())
"""

L8_EX = [
    {
        "title": "BST xususiyati",
        "description": "BST xususiyatiga ko'ra, o'ng farzand nodening qiymati ota-nodega nisbatan qanday bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": ["Kichik", "Katta", "Teng", "Har qanday"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Chap — kichik, o'ng — katta.",
        "explanation": "BST xususiyatiga ko'ra, chap farzand qiymati ota-nodedan kichik, o'ng farzand qiymati esa katta bo'lishi shart.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "BST murakkabligi",
        "description": "Balanslangan BST'da qidirish o'rtacha holatda qanday murakkablikka ega?",
        "exercise_type": "multiple_choice",
        "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Binary Search'ga o'xshab, har qadamda yarmi tashlanadi.",
        "explanation": "Balanslangan BST'da qidirish o'rtacha holatda O(log n), chunki har bir qadamda daraxtning yarmi qidiruvdan chetlashtiriladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Traversal turlari",
        "description": "Quyidagilardan qaysilari BST daraxtini aylanib chiqish (traversal) turlari hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Inorder", "Preorder", "Postorder", "Binary Search"],
        "correct_answers": "A,B,C",
        "is_multiple_select": True,
        "hint": "Binary Search — bu qidiruv algoritmi, traversal turi emas.",
        "explanation": "Inorder, Preorder va Postorder — BST'ni aylanib chiqishning uch asosiy turi. Binary Search esa alohida qidiruv algoritmi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Eng yomon holat sababi",
        "description": "BST eng yomon holatda O(n) murakkablikka ega bo'lishining asosiy sababini bitta so'z bilan yozing (masalan: daraxt qanday bo'lganda?).",
        "exercise_type": "text_input",
        "expected_answer": "skewed",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "O'suvchi tartib",
        "description": "BST'ni qaysi traversal turi bilan aylanib chiqish natijasi o'suvchi tartiblangan ro'yxatni beradi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "inorder",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Qo'shish (insert) qadamlari",
        "description": "BST'ga yangi qiymat qo'shish jarayonining qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "ildiz (root) node'dan boshlash",
            "qiymatni joriy node bilan solishtirish",
            "kichik bo'lsa chapga, katta bo'lsa o'ngga o'tish",
            "bo'sh joy topilganda yangi node'ni joylashtirish",
        ],
        "correct_order": [
            "ildiz (root) node'dan boshlash",
            "qiymatni joriy node bilan solishtirish",
            "kichik bo'lsa chapga, katta bo'lsa o'ngga o'tish",
            "bo'sh joy topilganda yangi node'ni joylashtirish",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Traversal natijalarini moslashtirish",
        "description": "Traversal turlarini ularning asosiy qo'llanilish maqsadi bilan mos ravishda joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Inorder - tartiblangan ro'yxat olish",
            "Preorder - daraxt strukturasini nusxalash",
            "Postorder - node'larni xavfsiz o'chirish",
        ],
        "correct_order": [
            "Inorder - tartiblangan ro'yxat olish",
            "Preorder - daraxt strukturasini nusxalash",
            "Postorder - node'larni xavfsiz o'chirish",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L9_TEXT = """\
<h3>Graf (Graph) nima?</h3>
<p>Graf &mdash; <strong>node'lar (vertices/tugunlar)</strong> va ularni bog'lovchi <strong>edge'lar (qirralar)</strong>dan tashkil topgan ma'lumotlar tuzilmasi. Graf orqali ijtimoiy tarmoqlar (do'stlar tarmog'i), yo'l xaritalari, veb-sahifalar orasidagi havolalar kabi ko'plab real hodisalarni modellashtirish mumkin.</p>
<h3>Graf turlari</h3>
<ul>
<li><strong>Directed (Yo'naltirilgan)</strong> &mdash; edge'lar faqat bitta yo'nalishda harakatlanadi (masalan, Instagram'da "follow").</li>
<li><strong>Undirected (Yo'naltirilmagan)</strong> &mdash; edge'lar ikki tomonlama (masalan, Facebook'da "friend").</li>
<li><strong>Weighted (Og'irlikli)</strong> &mdash; har bir edge o'ziga xos "og'irlik"ka (masofasi, narxi) ega (masalan, yo'l xaritasidagi masofalar).</li>
</ul>
<h3>Grafni ifodalash usullari</h3>
<table>
<tr><th>Usul</th><th>Xotira</th><th>Qo'shnini tekshirish</th><th>Qulayligi</th></tr>
<tr><td>Adjacency List</td><td>O(V + E)</td><td>O(qo'shnilar soni)</td><td>Siyrak graflar uchun yaxshi</td></tr>
<tr><td>Adjacency Matrix</td><td>O(V^2)</td><td>O(1)</td><td>Zich graflar uchun yaxshi</td></tr>
</table>
<p>Amaliyotda Adjacency List ko'pincha afzal ko'riladi, chunki aksariyat real graflar (ijtimoiy tarmoqlar, veb-sahifalar) "siyrak" bo'ladi &mdash; ya'ni node'lar soniga nisbatan edge'lar soni kam bo'ladi.</p>
<h3>Graf bo'ylab yurish algoritmlari</h3>
<ul>
<li><strong>BFS (Breadth-First Search)</strong> &mdash; Queue yordamida qatlam-qatlam (level by level) aylanib chiqadi. Eng qisqa yo'lni topishda ishlatiladi.</li>
<li><strong>DFS (Depth-First Search)</strong> &mdash; Stack (yoki rekursiya) yordamida bitta yo'nalish bo'ylab imkon qadar chuqur boradi.</li>
</ul>
<p>Quyidagi diagramma oddiy yo'naltirilmagan grafni ko'rsatadi:</p>
<pre class="mermaid">
flowchart TB
  A["A"] --- B["B"]
  A --- C["C"]
  B --- D["D"]
  C --- D
  D --- E["E"]
</pre>
<p>Graflar ijtimoiy tarmoqlar tahlili, GPS navigatsiya tizimlari, tarmoq yo'nalishlarini aniqlash (routing) va tavsiya tizimlarida (recommendation systems) keng qo'llaniladi. BFS va DFS &mdash; deyarli barcha graf algoritmlarining (masalan, eng qisqa yo'l topish, siklni aniqlash) asosini tashkil qiladi.</p>
"""

L9_CODE = """\
from collections import deque


# Graph implementatsiyasi - adjacency list usuli bilan
class Graph:
    def __init__(self):
        self.adjacency_list = {}

    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []

    # Yo'naltirilmagan graf uchun ikki tomonlama bog'lanish
    def add_edge(self, vertex1, vertex2):
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        self.adjacency_list[vertex1].append(vertex2)
        self.adjacency_list[vertex2].append(vertex1)

    # BFS - Queue yordamida qatlam-qatlam aylanib chiqish
    def bfs(self, start_vertex):
        visited = {start_vertex}
        queue = deque([start_vertex])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in self.adjacency_list.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result

    # DFS - rekursiya yordamida chuqur aylanib chiqish
    def dfs(self, start_vertex, visited=None, result=None):
        if visited is None:
            visited = set()
        if result is None:
            result = []

        visited.add(start_vertex)
        result.append(start_vertex)

        for neighbor in self.adjacency_list.get(start_vertex, []):
            if neighbor not in visited:
                self.dfs(neighbor, visited, result)
        return result


# Amaliyot
graph = Graph()
graph.add_edge("A", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("C", "D")
graph.add_edge("D", "E")

print("BFS natija:", graph.bfs("A"))  # ['A', 'B', 'C', 'D', 'E']
print("DFS natija:", graph.dfs("A"))  # ['A', 'B', 'D', 'C', 'E']
"""

L9_EX = [
    {
        "title": "Graf elementlari",
        "description": "Grafni tashkil etuvchi ikkita asosiy element qanday nomlanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Node va Edge", "Root va Leaf", "Key va Value", "Head va Tail"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bittasi tugunlar, ikkinchisi ularni bog'lovchi qirralar.",
        "explanation": "Graf node'lar (vertices) va ularni bog'lovchi edge'lar (qirralar)dan tashkil topadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "BFS tuzilmasi",
        "description": "BFS algoritmi qaysi ma'lumotlar tuzilmasidan foydalanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Stack", "Queue", "BST", "HashMap"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Qatlam-qatlam (level by level) aylanib chiqish uchun FIFO tuzilma kerak.",
        "explanation": "BFS Queue (FIFO) yordamida qatlam-qatlam aylanib chiqadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Graf turlari",
        "description": "Quyidagilardan qaysilari graf turlari hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": ["Directed", "Undirected", "Weighted", "Balanced"],
        "correct_answers": "A,B,C",
        "is_multiple_select": True,
        "hint": "\"Balanced\" — bu daraxtlarga tegishli tushuncha.",
        "explanation": "Directed, Undirected va Weighted — graflarning asosiy turlari. \"Balanced\" esa daraxtlar (BST, AVL) kontekstida ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "DFS tuzilmasi",
        "description": "DFS algoritmi odatda qaysi tuzilma yoki mexanizmdan foydalanadi? (bitta so'z bilan javob bering, masalan: stack yoki rekursiya)",
        "exercise_type": "text_input",
        "expected_answer": "stack",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Siyrak graf ifodasi",
        "description": "Siyrak (kam edge'li) graflar uchun xotira jihatidan samaraliroq ifodalash usulini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "adjacency list",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "BFS qadamlari",
        "description": "BFS algoritmining bajarilish qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "boshlang'ich node'ni queue'ga qo'shish va visited deb belgilash",
            "queue'dan bitta node'ni chiqarish (dequeue)",
            "uning barcha qo'shnilarini tekshirish",
            "ko'rilmagan qo'shnilarni queue'ga qo'shish",
        ],
        "correct_order": [
            "boshlang'ich node'ni queue'ga qo'shish va visited deb belgilash",
            "queue'dan bitta node'ni chiqarish (dequeue)",
            "uning barcha qo'shnilarini tekshirish",
            "ko'rilmagan qo'shnilarni queue'ga qo'shish",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Ifodalash usullarini moslashtirish",
        "description": "Grafni ifodalash usullarini ularga mos xususiyat bilan joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Adjacency List - siyrak graflar uchun samarali",
            "Adjacency Matrix - qo'shnini O(1)da tekshirish",
        ],
        "correct_order": [
            "Adjacency List - siyrak graflar uchun samarali",
            "Adjacency Matrix - qo'shnini O(1)da tekshirish",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


L10_TEXT = """\
<h3>Capstone: Kurs yakuni va amaliy loyiha</h3>
<p>Tabriklaymiz! Siz "Python: Algoritmlar va Ma'lumotlar Tuzilmasi" kursining barcha asosiy mavzularini &mdash; Big O notatsiyasi, LinkedList, Stack/Queue, Binary Search, tartiblash algoritmlari, HashMap, BST va Graf &mdash; o'rgandingiz. Ushbu yakuniy darsda barcha bilimlaringizni birlashtirib, real muammoni hal qilish orqali mustahkamlaysiz.</p>
<h3>Nima uchun bu bilimlar muhim</h3>
<p>Ma'lumotlar tuzilmalari va algoritmlarni chuqur tushunish sizga nafaqat texnik intervyularda muvaffaqiyatga erishishga, balki real loyihalarda <em>to'g'ri tuzilmani tanlash</em> orqali kodni tezroq va samaraliroq qilishga yordam beradi. Masalan, tez-tez qidiruv talab qiluvchi vazifada oddiy ro'yxat o'rniga HashMap (dict) tanlash dastur tezligini yuzlab marta oshirishi mumkin.</p>
<h3>Barcha mavzularni umumlashtiruvchi jadval</h3>
<table>
<tr><th>Tuzilma/Algoritm</th><th>Asosiy murakkablik</th><th>Qachon ishlatiladi</th></tr>
<tr><td>List</td><td>Kirish O(1), Qidiruv O(n)</td><td>Ketma-ket ma'lumot</td></tr>
<tr><td>LinkedList</td><td>Qo'shish O(1), Qidiruv O(n)</td><td>Tez-tez qo'shish/o'chirish</td></tr>
<tr><td>Stack/Queue</td><td>O(1) barcha asosiy amallar</td><td>LIFO/FIFO mantiqiy vazifalar</td></tr>
<tr><td>Binary Search</td><td>O(log n)</td><td>Tartiblangan ma'lumotda qidiruv</td></tr>
<tr><td>Merge/Quick Sort</td><td>O(n log n)</td><td>Katta hajmli tartiblash</td></tr>
<tr><td>HashMap (dict)</td><td>O(1) o'rtacha</td><td>Tez qidiruv, kesh</td></tr>
<tr><td>BST</td><td>O(log n) o'rtacha</td><td>Tartiblangan dinamik ma'lumot</td></tr>
<tr><td>Graph (BFS/DFS)</td><td>O(V + E)</td><td>Tarmoq, marshrut, bog'lanishlar</td></tr>
</table>
<p>Quyidagi diagramma kurs davomida o'rgangan bilimlar yo'lini ko'rsatadi:</p>
<pre class="mermaid">
flowchart LR
  A["Big O"] --> B["LinkedList"] --> C["Stack/Queue"] --> D["Binary Search"]
  D --> E["Tartiblash I & II"] --> F["HashMap"] --> G["BST"] --> H["Graph"] --> I["Capstone loyiha"]
</pre>
<p>Endi siz nafaqat algoritmlarni yozishni, balki ularning samaradorligini baholashni ham bilasiz. Keyingi qadam &mdash; ushbu bilimlarni real loyihalarda qo'llash, LeetCode kabi platformalarda mashq qilish va murakkabroq mavzular (Dynamic Programming, Greedy algoritmlar, Trie) bilan tanishishdir.</p>
"""

L10_CODE = """\
# Capstone: barcha bilimlarni birlashtiruvchi amaliy misol
# Vazifa: talabalar ro'yxatida tezkor qidiruv, tartiblash va
# diapazon bo'yicha qidiruv funksiyalarini amalga oshirish

students = [
    {"id": 101, "name": "Ali", "score": 87},
    {"id": 102, "name": "Vali", "score": 65},
    {"id": 103, "name": "Guli", "score": 92},
    {"id": 104, "name": "Sami", "score": 78},
    {"id": 105, "name": "Dilnoza", "score": 55},
]


# 1) HashMap (dict) yordamida ID bo'yicha O(1) tezkor qidiruv
def build_student_index(students):
    index = {}
    for student in students:
        index[student["id"]] = student
    return index


student_index = build_student_index(students)
print("ID=103 talaba:", student_index.get(103))


# 2) Merge Sort yordamida ballar bo'yicha tartiblash - O(n log n)
def merge_sort_by_score(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_by_score(arr[:mid])
    right = merge_sort_by_score(arr[mid:])
    return merge_by_score(left, right)


def merge_by_score(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i]["score"] <= right[j]["score"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


sorted_by_score = merge_sort_by_score(students)
print(
    "Ballar bo'yicha tartiblangan:",
    [f"{s['name']}:{s['score']}" for s in sorted_by_score],
)


# 3) Binary Search yordamida ma'lum balldan yuqori birinchi talabani topish
def find_first_above_score(sorted_students, min_score):
    left = 0
    right = len(sorted_students) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if sorted_students[mid]["score"] >= min_score:
            result = mid
            right = mid - 1
        else:
            left = mid + 1
    return sorted_students[result] if result != -1 else None


print("70 balldan yuqori birinchi talaba:", find_first_above_score(sorted_by_score, 70))

# Xulosa: HashMap (dict) - tez qidiruv, Merge Sort - samarali tartiblash,
# Binary Search - tartiblangan ma'lumotda tez qidiruv uchun birgalikda ishlatildi.
"""

L10_EX = [
    {
        "title": "Tez qidiruv uchun tuzilma",
        "description": "ID bo'yicha tez (O(1)) qidiruv kerak bo'lganda qaysi ma'lumotlar tuzilmasi eng mos keladi?",
        "exercise_type": "multiple_choice",
        "options": ["List", "LinkedList", "HashMap (dict)", "Stack"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Bu tuzilma o'rtacha O(1) qidiruv beradi.",
        "explanation": "HashMap (Python'da dict) kalit bo'yicha o'rtacha O(1) vaqtda qidiruv imkonini beradi, shuning uchun ID bo'yicha tez qidiruv uchun eng mos.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "1 million sonni tartiblash",
        "description": "1,000,000 ta tasodifiy sonni tartiblash uchun eng yaxshi tanlov qaysi?",
        "exercise_type": "multiple_choice",
        "options": ["Bubble Sort O(n^2)", "Selection Sort O(n^2)", "Merge/Quick Sort O(n log n)", "Insertion Sort o'rtacha O(n^2)"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Katta hajmli ma'lumotlar uchun O(n^2) juda sekin.",
        "explanation": "Katta hajmli ma'lumotlar uchun O(n log n) murakkablikka ega Merge/Quick Sort ancha samaraliroq.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Kursda o'rganilgan tuzilmalar",
        "description": "Ushbu kursda o'rgangan quyidagi tuzilma/algoritmlardan qaysilari to'g'ri?",
        "exercise_type": "multiple_choice",
        "options": ["LinkedList", "Binary Search Tree", "Graph (BFS/DFS)", "Neural Network"],
        "correct_answers": "A,B,C",
        "is_multiple_select": True,
        "hint": "Bittasi bu kursga umuman aloqasi yo'q mavzu.",
        "explanation": "LinkedList, Binary Search Tree va Graph — kursda o'rganilgan mavzular. Neural Network — bu kurs doirasiga kirmagan.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Telefon kitob tuzilmasi",
        "description": "Ism bo'yicha O(1) qidiruv va barcha ismlarni alfavit tartibida chiqarish kerak bo'lgan telefon kitob ilovasi uchun qaysi kombinatsiya eng mos? (masalan: 'HashMap va BST')",
        "exercise_type": "text_input",
        "expected_answer": "HashMap va BST",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Barcha tuzilmalarni solishtirish",
        "description": "Kursda o'rgangan 8 ta asosiy tuzilma/algoritmning umumiy nomini eslab, ularning umumiy murakkablik toifasini yozing (masalan: 'chiziqli va logarifmik').",
        "exercise_type": "text_input",
        "expected_answer": "chiziqli va logarifmik",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "To'g'ri tuzilmani tanlash qadamlari",
        "description": "Muammoni tahlil qilib to'g'ri ma'lumotlar tuzilmasini tanlash jarayonining qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Vazifaning asosiy amallarini aniqlash (qidiruv, qo'shish, tartiblash)",
            "Har bir amal uchun talab qilinadigan tezlikni baholash",
            "Mos murakkablikka ega tuzilmani tanlash",
            "Tanlangan tuzilmani amalga oshirish va sinash",
        ],
        "correct_order": [
            "Vazifaning asosiy amallarini aniqlash (qidiruv, qo'shish, tartiblash)",
            "Har bir amal uchun talab qilinadigan tezlikni baholash",
            "Mos murakkablikka ega tuzilmani tanlash",
            "Tanlangan tuzilmani amalga oshirish va sinash",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Kurs mavzularini tartiblash",
        "description": "Kurs davomida o'rganilgan mavzularni ular o'qitilgan tartibda joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Big O Notatsiyasi",
            "LinkedList",
            "Stack va Queue",
            "Binary Search",
            "Tartiblash algoritmlari",
            "HashMap",
            "BST",
            "Graph",
        ],
        "correct_order": [
            "Big O Notatsiyasi",
            "LinkedList",
            "Stack va Queue",
            "Binary Search",
            "Tartiblash algoritmlari",
            "HashMap",
            "BST",
            "Graph",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(order: int, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "python",
                         project_task: dict | None = None) -> str:
    sections = [
        {"id": f"t{order}", "type": "text", "label": "Текст",
         "html": text, "order": 0},
        {"id": f"c{order}", "type": "code", "label": "Код",
         "code": code, "lang": lang, "order": 1},
    ]
    if video:
        sections.append({"id": f"v{order}", "type": "video", "label": "Видео",
                          "videoUrl": video, "order": 2})
    if exercise_rows:
        sections.append({
            "id": f"e{order}", "type": "exercise", "label": "Упражнения",
            "exercises": [
                {
                    "_localId": e.id, "id": e.id,
                    "title": e.title, "description": e.description,
                    "exercise_type": e.exercise_type,
                    "options": e.options or "",
                    "correct_answers": e.correct_answers or "",
                    "drag_items": e.drag_items or "",
                    "correct_order": e.correct_order or "",
                    "is_multiple_select": bool(e.is_multiple_select),
                    "expected_answer": e.expected_answer or "",
                    "hint": e.hint or "",
                    "explanation": e.explanation or "",
                    "difficulty_level": e.difficulty_level,
                    "points": e.points, "order": e.order,
                }
                for e in exercise_rows
            ],
            "order": 3,
        })
    if project_task:
        sections.append({
            "id": f"p{order}", "type": "project", "label": project_task["task_title"],
            "description": project_task["task_description"],
            "requirements": project_task["task_requirements"],
            "techStack": project_task["task_technologies"],
            "deadline": project_task["task_deadline_days"],
            "order": 4,
        })
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()

        if existing:
            course = existing
            print(f"Course '{COURSE['title']}' already exists (id={course.id}). "
                  f"Adding/updating lessons only.")
        else:
            course = Course(**COURSE)
            db.add(course)
            await db.flush()
            print(f"Created course: id={course.id}  title='{course.title}'")

        existing_orders = {
            row[0] for row in (
                await db.execute(select(Lesson.order).where(Lesson.course_id == course.id))
            ).all()
        }

        done_lessons = [l for l in LESSON_PLAN if l["status"] == "done"]
        print(f"\nSeeding {len(done_lessons)}/{len(LESSON_PLAN)} lessons "
              f"(rest are still 'todo' in LESSON_PLAN):\n")

        for ldata in done_lessons:
            if ldata["order"] in existing_orders:
                print(f"  ⏭️  order={ldata['order']:>2}  {ldata['title']:<55}  "
                      f"already seeded, skipped")
                continue

            text = globals()[f"{ldata['ref']}_TEXT"]
            code = globals()[f"{ldata['ref']}_CODE"]
            ex_list = globals().get(f"{ldata['ref']}_EX", [])
            task = globals().get(f"{ldata['ref']}_TASK")
            lang = ldata.get("lang", "python")

            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=13,
                text_content=text,
                code_content=code,
                code_language=lang,
                video_url=None,  # TODO: add a real video link before publishing
                sections_json=None,
                task_title=task.get("task_title") if task else None,
                task_description=task.get("task_description") if task else None,
                task_requirements=task.get("task_requirements") if task else None,
                task_technologies=task.get("task_technologies") if task else None,
                task_deadline_days=task.get("task_deadline_days") if task else None,
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ex_list):
                row = Exercise(
                    lesson_id=lesson.id,
                    title=ex["title"],
                    description=ex.get("description", ex["title"]),
                    exercise_type=ex["exercise_type"],
                    options=_jdump(ex.get("options")),
                    correct_answers=_jdump(ex.get("correct_answers")),
                    drag_items=_jdump(ex.get("drag_items")),
                    correct_order=_jdump(ex.get("correct_order")),
                    is_multiple_select=bool(ex.get("is_multiple_select", False)),
                    expected_answer=ex.get("expected_answer", ""),
                    hint=ex.get("hint", ""),
                    explanation=ex.get("explanation", ""),
                    difficulty_level=ex["difficulty_level"],
                    points=ex["points"],
                    order=ex_order,
                    is_active=True,
                )
                db.add(row)
                ex_rows.append(row)
            await db.flush()

            lesson.sections_json = build_sections_json(
                ldata["order"], text, code, None, ex_rows, lang=lang,
                project_task=task,
            )

            sample = LessonSample(
                lesson_id=lesson.id,
                title=f"Namuna: {ldata['title']}",
                description=ldata["scope"],
                sample_type="code",
                code_files_json=json.dumps(
                    [{"filename": f"algoritm.{'py' if lang == 'python' else lang}",
                      "language": lang, "code": code}],
                    ensure_ascii=False,
                ),
            )
            db.add(sample)

            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<55}  exercises={len(ex_rows)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded {len(done_lessons)} lesson(s).")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
