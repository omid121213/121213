import random
import pickle
import os
import time

# پیکربندی ثابت‌ها
STUDENTS = 100_000
EXAMS = 10
SUBJECTS = 5
VALUES_PER_BYTE = 4  # چون هر مقدار فقط 2 بیت نیاز دارد

# کلاس فشرده‌سازی داده‌ها
class CompressedData:
    def __init__(self):
        self.total = STUDENTS * EXAMS * SUBJECTS
        self.data = bytearray((self.total + 3) // 4)  # هر 4 مقدار در یک بایت

    def _index(self, student_id, exam_id, subject_id):
        return (student_id - 1) * EXAMS * SUBJECTS + (exam_id - 1) * SUBJECTS + (subject_id - 1)

    def set_value(self, student_id, exam_id, subject_id, value):
        i = self._index(student_id, exam_id, subject_id)
        byte_index = i // 4
        offset = (i % 4) * 2
        self.data[byte_index] &= ~(0b11 << offset)  # پاک‌کردن مقدار قبلی
        self.data[byte_index] |= (value & 0b11) << offset  # نوشتن مقدار جدید

    def get_value(self, student_id, exam_id, subject_id):
        i = self._index(student_id, exam_id, subject_id)
        byte_index = i // 4
        offset = (i % 4) * 2
        return (self.data[byte_index] >> offset) & 0b11

    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)

    def load(self, filename):
        with open(filename, "rb") as f:
            self.data = pickle.load(f)

# تولید داده‌های تصادفی
def generate_random_data(store):
    for student in range(1, STUDENTS + 1):
        for exam in range(1, EXAMS + 1):
            for subject in range(1, SUBJECTS + 1):
                store.set_value(student, exam, subject, random.randint(0, 3))

# پیدا کردن N نفر با نمره آبی (۳) در یک درس یک آزمون
def top_n_blue(store, exam, subject, N):
    result = []
    for student in range(1, STUDENTS + 1):
        if store.get_value(student, exam, subject) == 3:
            result.append(student)
            if len(result) == N:
                break
    return result

# پیدا کردن N نفر برتر در یک آزمون با توجه به ضرایب دروس
def top_n_exam(store, exam, N):
    scores = []
    for student in range(1, STUDENTS + 1):
        total = sum(store.get_value(student, exam, subj) * subj for subj in range(1, SUBJECTS + 1))
        scores.append((student, total))
    scores.sort(key=lambda x: -x[1])
    return scores[:N]

# میانگین نمره هر درس در هر آزمون
def average_per_subject(store):
    result = {}
    for exam in range(1, EXAMS + 1):
        for subject in range(1, SUBJECTS + 1):
            total = sum(store.get_value(student, exam, subject) for student in range(1, STUDENTS + 1))
            avg = total / STUDENTS
            result[(exam, subject)] = round(avg, 2)
    return result

# اجرای کلی برنامه
if __name__ == "__main__":
    store = CompressedData()

    if os.path.exists("data.bin"):
        print(" Loading data from file...")
        store.load("data.bin")
    else:
        print(" Generating random data (this may take a few seconds)...")
        start = time.time()
        generate_random_data(store)
        store.save("data.bin")
        print(f" Data generated and saved. Time taken: {round(time.time() - start, 2)}s")

    # تست صحت
    store.set_value(1, 1, 1, 2)
    assert store.get_value(1, 1, 1) == 2
    print(" Test passed: Value setting/getting works correctly.")

    print("\n Top 5 Students in Exam 1, Subject 3 (Blue Only):")
    print(top_n_blue(store, 1, 3, 5))

    print("\n Top 5 Students in Exam 1 by Weighted Score:")
    for rank, (student, score) in enumerate(top_n_exam(store, 1, 5), 1):
        print(f"{rank}. Student {student} - Score: {score}")

    print("\nAverage Score per Subject per Exam:")
    averages = average_per_subject(store)
    for (exam, subject), avg in averages.items():
        print(f"Exam {exam}, Subject {subject}: Avg = {avg}")
