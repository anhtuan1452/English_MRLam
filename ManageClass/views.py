import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, ProtectedError
from django.forms import modelformset_factory
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from ManageClass.forms import ClassUpdateForm, LessonDetailForm, ClassForm  # ,, LessonForm
from ManageClass.forms import ClassUpdateForm, LessonDetailForm, ClassForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER, SUBMISSION, EXERCISE,
    LESSON, LESSON_DETAIL
)
from course_admin.forms import LessonDetailForm as CourseLessonDetailForm, LessonDetailFormSet as CourseLessonDetailFormSet

# Create a formset for LessonDetailForm (for class_detail view, editing dates only)
LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    fields=['date'],
    extra=0
)

def class_list(request):
    query = request.GET.get("q")
    classes = CLASS.objects.all()

    if query:
        classes = classes.filter(class_name__icontains=query)

    classes = classes.annotate(student_count=Count('user_class'))

    return render(request, 'class_list.html', {
        'classes': classes,
        'now': now().date(),
    })


def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                class_instance = form.save(commit=False)
                # Gán status mặc định (ví dụ: 'active')
                class_instance.status = 'active'
                class_instance.save()

                # Tạo LESSON_DETAIL cho tất cả LESSON của COURSE
                lessons = LESSON.objects.filter(course=class_instance.course).order_by('session_number')
                lesson_details = [
                    LESSON_DETAIL(lesson=lesson, classes=class_instance, date=None)
                    for lesson in lessons
                ]
                LESSON_DETAIL.objects.bulk_create(lesson_details)

                messages.success(request, "Thêm lớp học thành công!")
                return redirect('class_list')
        else:
            messages.error(request, "Có lỗi khi thêm lớp học.")
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})


from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, ProtectedError
from django.forms import modelformset_factory
from django.utils.timezone import now
from django.contrib.auth.models import User
from ManageClass.forms import ClassUpdateForm, LessonDetailForm, ClassForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER,
    SUBMISSION, EXERCISE, LESSON, LESSON_DETAIL, ROLLCALL
)

LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    fields=['date'],
    extra=0
)


def class_detail(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Lấy tất cả các buổi học của khóa học
    lessons = LESSON.objects.filter(course=class_instance.course).order_by('session_number')

    # Lấy hoặc tạo LESSON_DETAIL cho mỗi LESSON
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson')
    lesson_detail_dict = {ld.lesson_id: ld for ld in lesson_details}

    # Tự động tạo và lưu LESSON_DETAIL cho các LESSON chưa có
    with transaction.atomic():
        for lesson in lessons:
            if lesson.lesson_id not in lesson_detail_dict:
                lesson_detail = LESSON_DETAIL(
                    lesson=lesson,
                    classes=class_instance,
                    date=None
                )
                lesson_detail.save()
                lesson_detail_dict[lesson.lesson_id] = lesson_detail

    # Lấy lại lesson_details sau khi tạo mới
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson').order_by(
        'lesson__session_number')

    # Khởi tạo các form
    class_form = ClassUpdateForm(instance=class_instance)
    lesson_detail_formset = LessonDetailFormSet(queryset=lesson_details)

    # Zip formset với lesson_details để hiển thị
    zipped_form_details = zip(lesson_detail_formset.forms, lesson_details)

    if request.method == 'POST':
        action = request.POST.get('action')
        print(f"POST action: {action}")  # Debug
        print(f"POST data: {request.POST}")  # Debug

        if action == 'update_class':
            class_form = ClassUpdateForm(request.POST, instance=class_instance)
            if class_form.is_valid():
                class_form.save()
                messages.success(request, "Cập nhật lớp học thành công!")
                return redirect('class_detail', class_id=class_id)
            else:
                messages.error(request, "Có lỗi khi cập nhật lớp học.")

        elif action == 'update_lesson_dates':
            lesson_detail_formset = LessonDetailFormSet(request.POST, queryset=lesson_details)
            if lesson_detail_formset.is_valid():
                try:
                    with transaction.atomic():
                        instances = lesson_detail_formset.save(commit=False)
                        for instance in instances:
                            # Không cần gán lại instance.classes = class_instance
                            # vì instance đã có liên kết với class_instance
                            instance.save()

                        # Lưu các mối quan hệ many-to-many (nếu có)
                        lesson_detail_formset.save_m2m()

                        messages.success(request, "Cập nhật ngày học thành công.")
                        return redirect('class_detail', class_id=class_instance.class_id)
                except Exception as e:
                    print(f"Error saving formset: {str(e)}")  # Debug
                    messages.error(request, f"Có lỗi khi lưu ngày học: {str(e)}")
            else:
                print(f"Formset errors: {lesson_detail_formset.errors}")  # Debug
                for i, form in enumerate(lesson_detail_formset):
                    print(f"Form {i} errors: {form.errors}")  # Debug chi tiết từng form
                messages.error(request, "Có lỗi trong việc cập nhật ngày học. Vui lòng kiểm tra dữ liệu.")

        elif action == 'delete_class':
            try:
                class_instance.delete()
                messages.success(request, "Xóa lớp học thành công!")
                return redirect('class_list')
            except ProtectedError:
                messages.error(request, "Không thể xóa lớp học do có dữ liệu liên quan.")

    return render(request, 'class_detail.html', {
        'class_instance': class_instance,
        'lesson_details': lesson_details,
        'lessons': lessons,
        'class_form': class_form,
        'lesson_detail_formset': lesson_detail_formset,
        'zipped_form_details': zipped_form_details,
    })



def class_exercise(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    students = USER_CLASS.objects.filter(classes=class_instance).select_related('user')
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson').order_by(
        'lesson__session_number')

    # Tổng số học viên trong lớp
    total_students = students.count()

    lesson_data = []
    for lesson_detail in lesson_details:
        exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
        student_submissions = []

        # Thống kê cho buổi học này
        submission_stats = {
            'submitted_count': 0,  # Số bài đã nộp
            'not_submitted_count': total_students,  # Số bài chưa nộp (mặc định bằng tổng số học viên)
            'checked_count': 0,  # Số bài đã chấm
            'unchecked_count': 0,  # Số bài chưa chấm
        }

        if exercise:
            # Lấy tất cả bài nộp cho bài tập này
            submissions = SUBMISSION.objects.filter(exercise=exercise)

            # Số bài đã nộp
            submitted_count = submissions.count()
            submission_stats['submitted_count'] = submitted_count

            # Số bài chưa nộp
            submission_stats['not_submitted_count'] = total_students - submitted_count

            # Số bài đã chấm (status='done')
            checked_count = submissions.filter(status='Done').count()
            submission_stats['checked_count'] = checked_count

            # Số bài chưa chấm (status='check')
            unchecked_count = submissions.filter(status='Checking').count() + submissions.filter(status='Check').count()
            submission_stats['unchecked_count'] = unchecked_count

        for student in students:
            submission = None
            if exercise:
                submission = SUBMISSION.objects.filter(
                    userclass=student,
                    exercise=exercise
                ).select_related('userclass__user').first()

            student_submissions.append({
                'student': student,
                'submission': submission,
            })

        lesson_data.append({
            'lesson_detail': lesson_detail,
            'exercise': exercise,
            'student_submissions': student_submissions,
            'submission_stats': submission_stats,  # Thêm thống kê
        })

    return render(request, 'class_exercise.html', {
        'class_instance': class_instance,
        'class_id': class_id,
        'lesson_data': lesson_data,
    })



# views.py


@require_http_methods(["GET", "POST"])
def class_rollcall(request, class_id):
    """
    Hiển thị và xử lý điểm danh cho từng buổi (LESSON_DETAIL) của lớp.
    - GET: render template với danh sách buổi và form status hiện tại.
    - POST: nhận lesson_detail_id + status của từng USER_CLASS để lưu/cập nhật vào ROLLCALL và ROLLCALL_USER.
    """
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Lấy danh sách tất cả học viên (USER_CLASS) của lớp này
    user_classes = USER_CLASS.objects.filter(classes=class_instance).select_related('user')

    # Lấy danh sách LESSON_DETAIL chỉ của lớp này (classes=class_instance)
    lesson_details = LESSON_DETAIL.objects.filter(
        classes=class_instance
    ).select_related('lesson').order_by('lesson__session_number')

    # Xử lý POST: người dùng submit form "Lưu điểm danh" cho một buổi cụ thể
    if request.method == "POST":
        lesson_detail_id = request.POST.get('lesson_detail_id')
        if not lesson_detail_id:
            messages.error(request, "Không xác định được buổi học để lưu điểm danh.")
            return redirect('class_rollcall', class_id=class_id)

        # Lấy buổi học tương ứng
        lesson_detail = get_object_or_404(
            LESSON_DETAIL,
            pk=lesson_detail_id,
            classes=class_instance
        )

        # Tạo hoặc lấy ROLLCALL gắn với buổi này
        rollcall, _ = ROLLCALL.objects.get_or_create(lessondetail=lesson_detail)

        total_changes = 0
        # Duyệt qua từng USER_CLASS trong lớp, đọc status từ form
        for uc in user_classes:
            # Khóa chính của USER_CLASS là uc.userclass_id
            uc_id = uc.userclass_id
            # Tên field trong form: "status_<lesson_detail_id>_<userclass_id>"
            field_name = f"status_{lesson_detail_id}_{uc_id}"
            status_value = request.POST.get(field_name)
            # Nếu không chọn (empty) thì bỏ qua
            if status_value not in ['present', 'absent']:
                continue

            # Tạo mới hoặc cập nhật ROLLCALL_USER
            ru, created = ROLLCALL_USER.objects.get_or_create(
                rollcall=rollcall,
                userclass=uc,
                defaults={'status': status_value}
            )
            if created:
                total_changes += 1
            else:
                # Nếu đã tồn tại nhưng status khác, cập nhật
                if ru.status != status_value:
                    ru.status = status_value
                    ru.save()
                    total_changes += 1

        messages.success(
            request,
            f"Đã lưu điểm danh buổi “{lesson_detail.lesson.lesson_name}” "
            f"(Buổi #{lesson_detail.lesson.session_number}). Tổng thay đổi: {total_changes}"
        )
        return redirect('class_rollcall', class_id=class_id)

    # Nếu GET: chuẩn bị dữ liệu cho template
    rollcall_data = []
    for ld in lesson_details:
        # Lấy ROLLCALL (nếu đã có) cho buổi này
        rollcall = getattr(ld, 'rollcall', None)
        users_data = []
        for uc in user_classes:
            uc_id = uc.userclass_id
            if rollcall:
                ru = ROLLCALL_USER.objects.filter(
                    rollcall=rollcall,
                    userclass=uc
                ).first()
                status = ru.status if ru else ''
            else:
                status = ''
            users_data.append({
                'userclass': uc,
                'status': status,
            })
        rollcall_data.append({
            'lesson_detail': ld,
            'users_data': users_data,
        })

    return render(request, 'class_rollcall.html', {
        'class_instance': class_instance,
        'rollcall_data': rollcall_data,
    })

def add_student_to_class(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        USER_CLASS.objects.get_or_create(user=user, classes=class_instance)
        messages.success(request, "Thêm học viên thành công!")
        return redirect('class_detail', class_id=class_id)

    users_not_in_class = User.objects.exclude(
        id__in=USER_CLASS.objects.filter(classes=class_instance).values_list('user_id', flat=True)
    )
    return render(request, 'add_student_to_class.html', {
        'class_instance': class_instance,
        'users': users_not_in_class
    })


# Placeholder ClassForm (needs proper implementation)


def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Lưu CLASS
                class_instance = form.save()
                # Tự động tạo LESSON_DETAIL cho tất cả LESSON của COURSE
                lessons = LESSON.objects.filter(course=class_instance.course).order_by('session_number')
                lesson_details = [
                    LESSON_DETAIL(lesson=lesson, classes=class_instance, date=None)
                    for lesson in lessons
                ]
                LESSON_DETAIL.objects.bulk_create(lesson_details)
                messages.success(request, "Thêm lớp học thành công!")
                return redirect('class_list')
        else:
            messages.error(request, "Có lỗi khi thêm lớp học.")
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})


# views.py (tiếp tục bên dưới hoặc ở đoạn thích hợp)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt  # hoặc sử dụng @csrf_protect trên toàn project

# @require_http_methods(["POST"])
# @csrf_exempt  # nếu bạn đã cấu hình CSRF token trong template, bạn có thể bỏ dòng này
# def update_rollcall(request):
#     # Kiểm tra xem có phải AJAX request không
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         # --- TRƯỜNG HỢP 1: Tạo mới điểm danh ---
#         if request.POST.get('create_rollcall'):
#             lesson_detail_id = request.POST.get('lesson_detail_id')
#             if not lesson_detail_id:
#                 return JsonResponse({'error': 'Missing lesson_detail_id'}, status=400)
#
#             lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
#             # Tạo hoặc lấy ROLLCALL tương ứng
#             rollcall, created = ROLLCALL.objects.get_or_create(lessondetail=lesson_detail)
#
#             # Lấy tất cả USER_CLASS của lớp đó
#             user_classes = USER_CLASS.objects.filter(classes=lesson_detail.classes)
#
#             new_rollcall_users = []
#             for uc in user_classes:
#                 # Nếu chưa có ROLLCALL_USER cho cặp (rollcall, userclass), tạo mới
#                 exist = ROLLCALL_USER.objects.filter(rollcall=rollcall, userclass=uc).exists()
#                 if not exist:
#                     new_rollcall_users.append(
#                         ROLLCALL_USER(rollcall=rollcall, userclass=uc, status='absent')
#                     )
#
#             if new_rollcall_users:
#                 ROLLCALL_USER.objects.bulk_create(new_rollcall_users)
#
#             return JsonResponse({'message': 'Tạo điểm danh thành công.'})
#
#         # --- TRƯỜNG HỢP 2: Cập nhật điểm danh ---
#         elif request.POST.get('rollcall_data'):
#             try:
#                 data = json.loads(request.POST.get('rollcall_data'))
#             except json.JSONDecodeError:
#                 return JsonResponse({'error': 'Dữ liệu rollcall_data không hợp lệ.'}, status=400)
#
#             # Giả định tất cả các entry đều có chung lesson_detail_id
#             # Lấy lesson_detail_id từ phần tử đầu
#             first_item = next(iter(data.values()), None)
#             if not first_item or 'lesson_detail_id' not in first_item:
#                 return JsonResponse({'error': 'Không tìm thấy lesson_detail_id trong dữ liệu.'}, status=400)
#
#             lesson_detail_id = first_item['lesson_detail_id']
#             lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
#
#             # Lấy ROLLCALL hiện tại (bắt buộc đã tồn tại, vì đã tạo lúc create_rollcall)
#             try:
#                 rollcall = ROLLCALL.objects.get(lessondetail=lesson_detail)
#             except ROLLCALL.DoesNotExist:
#                 return JsonResponse({'error': 'Rollcall chưa được tạo trước đó.'}, status=400)
#
#             updated_instances = []
#             # Với mỗi userclass_id, cập nhật hoặc tạo mới ROLLCALL_USER
#             for uc_id_str, item in data.items():
#                 try:
#                     uc_id = int(uc_id_str)
#                     status = item.get('status')
#                 except (ValueError, KeyError):
#                     continue
#
#                 uc = get_object_or_404(USER_CLASS, pk=uc_id)
#                 # get_or_create: nếu đã có, get ra instance; nếu chưa, tạo mới với status được truyền
#                 ru, created = ROLLCALL_USER.objects.get_or_create(
#                     rollcall=rollcall,
#                     userclass=uc,
#                     defaults={'status': status}
#                 )
#                 if not created:
#                     # Nếu tồn tại nhưng status khác, update
#                     if ru.status != status:
#                         ru.status = status
#                         updated_instances.append(ru)
#
#             # Bulk update cho những bản ghi cũ có thay đổi status
#             if updated_instances:
#                 ROLLCALL_USER.objects.bulk_update(updated_instances, ['status'])
#
#             return JsonResponse({'message': 'Cập nhật điểm danh thành công.'})
#
#     # Nếu không phải AJAX hoặc thiếu tham số
#     return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=400)


def exercise_detail_view(request, class_id, submission_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    submission = get_object_or_404(SUBMISSION, pk=submission_id, userclass__classes=class_instance)

    if request.method == 'POST':
        review = request.POST.get('review')
        action = request.POST.get('action')

        if not review:
            messages.error(request, "Vui lòng cung cấp nhận xét.")
            return redirect('exercise_detail', class_id=class_id, submission_id=submission_id)

        submission.review = review
        if action == 'redo':
            submission.status = 'Check'
            subject = f'Yêu cầu làm lại bài tập: {submission.exercise.lessondetail.lesson.lesson_name}'
            message = f"""
Kính gửi {submission.userclass.user.get_full_name},

Bài tập "{submission.exercise.lessondetail.lesson.lesson_name}" của bạn cần được làm lại. Dưới đây là nhận xét từ giáo viên:

{review}

Vui lòng nộp lại bài tập qua hệ thống trước hạn chót.

Trân trọng,
Hệ thống quản lý lớp học
"""
            messages.success(request, "Yêu cầu làm lại bài tập đã được gửi tới học viên!")
        else:  # action == 'done'
            submission.status = 'Done'
            subject = f'Nhận xét bài tập: {submission.exercise.lessondetail.lesson.lesson_name}'
            message = f"""
Kính gửi {submission.userclass.user.get_full_name},

Bài tập "{submission.exercise.lessondetail.lesson.lesson_name}" của bạn đã được chấm. Dưới đây là nhận xét từ giáo viên:

{review}

Trân trọng,
Hệ thống quản lý lớp học
"""
            messages.success(request, "Nhận xét bài tập đã được gửi tới học viên!")

        submission.save()

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[submission.userclass.user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Lỗi khi gửi email: {str(e)}")
            return redirect('exercise_detail', class_id=class_id, submission_id=submission_id)

        return redirect('class_exercise', class_id=class_id)

    return render(request, 'exercise_detail.html', {
        'class_instance': class_instance,
        'submission': submission,
    })

