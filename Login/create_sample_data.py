from django.contrib.auth.models import User
from english.models import USER_PROFILE
from django.utils import timezone
from datetime import datetime

def create_sample_data():
    # Danh sách người dùng (14 bản ghi)
    users_data = [
        # 10 học sinh (người dùng thông thường)
        {
            'username': 'student1',
            'email': 'student1@mr-lam.com',
            'password': 'student123',
            'first_name': 'Lê',
            'last_name': 'Minh Châu',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student2',
            'email': 'student2@mr-lam.com',
            'password': 'student123',
            'first_name': 'Phạm',
            'last_name': 'Đức Dũng',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student3',
            'email': 'student3@mr-lam.com',
            'password': 'student123',
            'first_name': 'Hoàng',
            'last_name': 'Thị Ngọc',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student4',
            'email': 'student4@mr-lam.com',
            'password': 'student123',
            'first_name': 'Vũ',
            'last_name': 'Quang Huy',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student5',
            'email': 'student5@mr-lam.com',
            'password': 'student123',
            'first_name': 'Ngô',
            'last_name': 'Thanh Hương',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student6',
            'email': 'student6@mr-lam.com',
            'password': 'student123',
            'first_name': 'Đinh',
            'last_name': 'Văn Khang',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student7',
            'email': 'student7@mr-lam.com',
            'password': 'student123',
            'first_name': 'Bùi',
            'last_name': 'Thị Lan',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student8',
            'email': 'student8@mr-lam.com',
            'password': 'student123',
            'first_name': 'Lý',
            'last_name': 'Minh Nam',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student9',
            'email': 'student9@mr-lam.com',
            'password': 'student123',
            'first_name': 'Đoàn',
            'last_name': 'Thị Phượng',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'student10',
            'email': 'student10@mr-lam.com',
            'password': 'student123',
            'first_name': 'Mai',
            'last_name': 'Văn Tâm',
            'is_staff': False,
            'is_superuser': False,
        },
        # 3 giáo viên
        {
            'username': 'teacher1',
            'email': 'teacher1@mr-lam.com',
            'password': 'teacher123',
            'first_name': 'Nguyễn',
            'last_name': 'Văn An',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'teacher2',
            'email': 'teacher2@mr-lam.com',
            'password': 'teacher123',
            'first_name': 'Trần',
            'last_name': 'Thị Bình',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'teacher3',
            'email': 'teacher3@mr-lam.com',
            'password': 'teacher123',
            'first_name': 'Lê',
            'last_name': 'Hồng Cẩm',
            'is_staff': True,
            'is_superuser': False,
        },
        # 1 quản trị viên
        {
            'username': 'admin',
            'email': 'admin@mr-lam.com',
            'password': 'admin123456',
            'first_name': 'Quản Trị',
            'last_name': 'Hệ Thống',
            'is_staff': True,
            'is_superuser': True,
        },
    ]

    # Danh sách hồ sơ người dùng (USER_PROFILE) tương ứng
    profiles_data = [
        # 10 học sinh
        {'dob': '2005-05-10', 'sex': 'F', 'description': 'Học sinh', 'image': 'https://example.com/student1.jpg'},
        {'dob': '2006-08-25', 'sex': 'M', 'description': 'Học sinh', 'image': 'https://example.com/student2.jpg'},
        {'dob': '2007-02-14', 'sex': 'F', 'description': 'Học sinh', 'image': 'https://example.com/student3.jpg'},
        {'dob': '2005-11-30', 'sex': 'M', 'description': 'Học sinh', 'image': 'https://example.com/student4.jpg'},
        {'dob': '2006-09-18', 'sex': 'F', 'description': 'Học sinh', 'image': 'https://example.com/student5.jpg'},
        {'dob': '2007-04-05', 'sex': 'M', 'description': 'Học sinh', 'image': 'https://example.com/student6.jpg'},
        {'dob': '2005-12-12', 'sex': 'F', 'description': 'Học sinh', 'image': 'https://example.com/student7.jpg'},
        {'dob': '2006-06-20', 'sex': 'M', 'description': 'Học sinh', 'image': 'https://example.com/student8.jpg'},
        {'dob': '2007-03-03', 'sex': 'F', 'description': 'Học sinh', 'image': 'https://example.com/student9.jpg'},
        {'dob': '2005-10-28', 'sex': 'M', 'description': 'Học sinh', 'image': 'https://example.com/student10.jpg'},
        # 3 giáo viên
        {'dob': '1985-03-15', 'sex': 'M', 'description': 'Giáo viên Tiếng Anh', 'image': 'https://example.com/teacher1.jpg'},
        {'dob': '1990-07-22', 'sex': 'F', 'description': 'Giáo viên Tiếng Anh', 'image': 'https://example.com/teacher2.jpg'},
        {'dob': '1988-09-10', 'sex': 'F', 'description': 'Giáo viên Tiếng Anh', 'image': 'https://example.com/teacher3.jpg'},
        # 1 quản trị viên
        {'dob': '1980-01-01', 'sex': 'M', 'description': 'Quản trị viên hệ thống', 'image': 'https://example.com/admin.jpg'},
    ]

    # Tạo người dùng và hồ sơ
    for user_data, profile_data in zip(users_data, profiles_data):
        # Tạo hoặc lấy người dùng
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_superuser': user_data['is_superuser'],
                'is_staff': user_data['is_staff'],
                'is_active': True,
                'date_joined': timezone.now(),
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Created user: {user.username}")

        # Tạo hoặc cập nhật hồ sơ người dùng
        USER_PROFILE.objects.get_or_create(
            userprofile=user,
            defaults={
                'dob': datetime.strptime(profile_data['dob'], '%Y-%m-%d').date(),
                'sex': profile_data['sex'],
                'description': profile_data['description'],
                'image': profile_data['image'],
            }
        )
        print(f"Created/Updated profile for: {user.username}")

if __name__ == "__main__":
    create_sample_data()


