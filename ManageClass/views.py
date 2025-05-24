from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import modelformset_factory
from django.core.mail import send_mail
from django.conf import settings

from ManageClass.forms import ClassUpdateForm, LessonDetailForm, ClassForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER, SUBMISSION, EXERCISE,
    LESSON, LESSON_DETAIL
)

from english.views import is_admin, is_staff
from django.db.models import Count, ProtectedError, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.utils.timezone import now
from django.contrib.auth.models import User

# Định nghĩa LessonDetailFormSet ở đây để tránh trùng lặp
LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    fields=['date'],
    extra=0
)

@login_required
@user_passes_test(is_staff)
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

@login_required
@user_passes_test(is_admin)
def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                class_instance = form.save()
                lessons = LESSON.objects.filter(
                    course=class_instance.course,
                    class_specific_id=0
                ).order_by('session_number')

                lesson_details = [
                    LESSON_DETAIL(lesson=lesson, classes=class_instance, date=None)
                    for lesson in lessons
                ]
                lesson_details = LESSON_DETAIL.objects.bulk_create(lesson_details)

                exercises = []
                for lesson_detail in lesson_details:
                    default_duedate = class_instance.begin_time + timedelta(days=7)
                    exercise = EXERCISE(
                        lessondetail=lesson_detail,
                        duedate=default_duedate
                    )
                    exercises.append(exercise)
                EXERCISE.objects.bulk_create(exercises)

                messages.success(request, "Thêm lớp học thành công! Đã tạo lịch học và bài tập mặc định.")
                return redirect('class_list')
        else:
            messages.error(request, "Có lỗi khi thêm lớp học.")
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def class_detail(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Lấy LESSON phù hợp: mặc định (class_specific_id=0) hoặc riêng cho lớp này (class_specific_id=class_id)
    lessons = LESSON.objects.filter(
        Q(course=class_instance.course, class_specific_id=0) |
        Q(class_specific_id=class_id)
    ).order_by('session_number')

    # Lấy hoặc tạo LESSON_DETAIL cho mỗi LESSON phù hợp
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson')
    lesson_detail_dict = {ld.lesson_id: ld for ld in lesson_details}

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
            print(f"Formset is_valid: {lesson_detail_formset.is_valid()}")  # Debug
            if lesson_detail_formset.is_valid():
                try:
                    with transaction.atomic():
                        instances = lesson_detail_formset.save(commit=False)
                        print(f"Number of instances: {len(instances)}")  # Debug
                        created_exercises = 0
                        updated_exercises = 0
                        total_forms = int(request.POST.get('form-TOTAL_FORMS', 0))

                        for i in range(total_forms):
                            lessondetail_id = request.POST.get(f'form-{i}-lessondetail_id')
                            if lessondetail_id:
                                lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lessondetail_id)
                                date_str = request.POST.get(f'form-{i}-date')
                                duedate_str = request.POST.get(f'form-{i}-duedate')

                                # Cập nhật date cho LESSON_DETAIL
                                if date_str:
                                    try:
                                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                        if lesson_detail.date != date:
                                            lesson_detail.date = date
                                            lesson_detail.save()
                                            print(f"Updated LESSON_DETAIL {lessondetail_id} with date {date}")  # Debug
                                    except ValueError:
                                        messages.error(request, f"Ngày học không hợp lệ cho buổi '{lesson_detail.lesson.lesson_name}'.")
                                        continue

                                # Xử lý duedate (giống cách form cho phép nhập hoặc để trống)
                                if duedate_str:
                                    try:
                                        duedate = datetime.strptime(duedate_str, '%Y-%m-%d').date()
                                        print(f"Using user-provided duedate for {lessondetail_id}: {duedate}")
                                    except ValueError:
                                        messages.error(request, f"Ngày hạn nộp không hợp lệ cho buổi '{lesson_detail.lesson.lesson_name}'.")
                                        continue
                                else:
                                    # Nếu không có duedate, dùng date + 7 ngày nếu date tồn tại, hoặc begin_time + 7 ngày
                                    if lesson_detail.date:
                                        duedate = lesson_detail.date + timedelta(days=7)
                                        print(f"Using date-based duedate for {lessondetail_id}: {duedate}")
                                    else:
                                        duedate = class_instance.begin_time + timedelta(days=7) if class_instance.begin_time else datetime.now().date() + timedelta(days=7)
                                        print(f"Using default duedate for {lessondetail_id}: {duedate}")

                                try:
                                    exercise, created = EXERCISE.objects.get_or_create(
                                        lessondetail=lesson_detail,
                                        defaults={'duedate': duedate}
                                    )
                                    if created:
                                        created_exercises += 1
                                        print(f"Created EXERCISE for lessondetail_id {lessondetail_id} with duedate {duedate}")
                                    else:
                                        if exercise.duedate != duedate:
                                            exercise.duedate = duedate
                                            exercise.save()
                                            updated_exercises += 1
                                            print(f"Updated EXERCISE for lessondetail_id {lessondetail_id} with new duedate {duedate}")
                                except Exception as e:
                                    messages.error(request, f"Lỗi khi tạo/cập nhật bài tập cho buổi '{lesson_detail.lesson.lesson_name}': {str(e)}")
                                    print(f"Error creating/updating EXERCISE for {lessondetail_id}: {str(e)}")
                                    continue

                        lesson_detail_formset.save_m2m()
                        messages.success(request, f"Cập nhật ngày học thành công. Đã tạo {created_exercises} và cập nhật {updated_exercises} bài tập.")
                        return redirect('class_detail', class_id=class_instance.class_id)
                except Exception as e:
                    print(f"Error saving formset: {str(e)}")
                    messages.error(request, f"Có lỗi khi lưu ngày học: {str(e)}")
            else:
                print(f"Formset errors: {lesson_detail_formset.errors}")
                for i, form in enumerate(lesson_detail_formset):
                    print(f"Form {i} errors: {form.errors}")
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

@login_required
@user_passes_test(is_staff)
def class_exercise(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    students = USER_CLASS.objects.filter(classes=class_instance).select_related('user')
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson').order_by(
        'lesson__session_number')

    total_students = students.count()

    lesson_data = []
    for lesson_detail in lesson_details:
        exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
        student_submissions = []

        submission_stats = {
            'submitted_count': 0,
            'not_submitted_count': total_students,
            'checked_count': 0,
            'unchecked_count': 0,
        }

        if exercise:
            submissions = SUBMISSION.objects.filter(exercise=exercise)
            submitted_count = submissions.count()
            submission_stats['submitted_count'] = submitted_count
            submission_stats['not_submitted_count'] = total_students - submitted_count
            checked_count = submissions.filter(status='Done').count()
            submission_stats['checked_count'] = checked_count
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
            'submission_stats': submission_stats,
        })

    return render(request, 'class_exercise.html', {
        'class_instance': class_instance,
        'class_id': class_id,
        'lesson_data': lesson_data,
    })

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def class_rollcall(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    user_classes = USER_CLASS.objects.filter(classes=class_instance).select_related('user')
    lesson_details = LESSON_DETAIL.objects.filter(
        classes=class_instance
    ).select_related('lesson').order_by('lesson__session_number')

    if request.method == "POST":
        lesson_detail_id = request.POST.get('lesson_detail_id')
        if not lesson_detail_id:
            messages.error(request, "Không xác định được buổi học để lưu điểm danh.")
            return redirect('class_rollcall', class_id=class_id)

        lesson_detail = get_object_or_404(
            LESSON_DETAIL,
            pk=lesson_detail_id,
            classes=class_instance
        )
        rollcall, _ = ROLLCALL.objects.get_or_create(lessondetail=lesson_detail)

        total_changes = 0
        for uc in user_classes:
            uc_id = uc.userclass_id
            field_name = f"status_{lesson_detail_id}_{uc_id}"
            status_value = request.POST.get(field_name)
            if status_value not in ['present', 'absent']:
                continue

            ru, created = ROLLCALL_USER.objects.get_or_create(
                rollcall=rollcall,
                userclass=uc,
                defaults={'status': status_value}
            )
            if created:
                total_changes += 1
            else:
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

    rollcall_data = []
    for ld in lesson_details:
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

# @require_http_methods(["POST"])
# @csrf_exempt
# def update_rollcall(request):
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         if request.POST.get('create_rollcall'):
#             lesson_detail_id = request.POST.get('lesson_detail_id')
#             if not lesson_detail_id:
#                 return JsonResponse({'error': 'Missing lesson_detail_id'}, status=400)
#
#             lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
#             rollcall, created = ROLLCALL.objects.get_or_create(lessondetail=lesson_detail)
#
#             user_classes = USER_CLASS.objects.filter(classes=lesson_detail.classes)
#             new_rollcall_users = []
#             for uc in user_classes:
#                 if not ROLLCALL_USER.objects.filter(rollcall=rollcall, userclass=uc).exists():
#                     new_rollcall_users.append(
#                         ROLLCALL_USER(rollcall=rollcall, userclass=uc, status='absent')
#                     )
#
#             if new_rollcall_users:
#                 ROLLCALL_USER.objects.bulk_create(new_rollcall_users)
#
#             return JsonResponse({'message': 'Tạo điểm danh thành công.'})
#
#         elif request.POST.get('rollcall_data'):
#             try:
#                 data = json.loads(request.POST.get('rollcall_data'))
#             except json.JSONDecodeError:
#                 return JsonResponse({'error': 'Dữ liệu rollcall_data không hợp lệ.'}, status=400)
#
#             first_item = next(iter(data.values()), None)
#             if not first_item or 'lesson_detail_id' not in first_item:
#                 return JsonResponse({'error': 'Không tìm thấy lesson_detail_id trong dữ liệu.'}, status=400)
#
#             lesson_detail_id = first_item['lesson_detail_id']
#             lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
#
#             try:
#                 rollcall = ROLLCALL.objects.get(lessondetail=lesson_detail)
#             except ROLLCALL.DoesNotExist:
#                 return JsonResponse({'error': 'Rollcall chưa được tạo trước đó.'}, status=400)
#
#             updated_instances = []
#             for uc_id_str, item in data.items():
#                 try:
#                     uc_id = int(uc_id_str)
#                     status = item.get('status')
#                 except (ValueError, KeyError):
#                     continue
#
#                 uc = get_object_or_404(USER_CLASS, pk=uc_id)
#                 ru, created = ROLLCALL_USER.objects.get_or_create(
#                     rollcall=rollcall,
#                     userclass=uc,
#                     defaults={'status': status}
#                 )
#                 if not created and ru.status != status:
#                     ru.status = status
#                     updated_instances.append(ru)
#
#             if updated_instances:
#                 ROLLCALL_USER.objects.bulk_update(updated_instances, ['status'])
#
#             return JsonResponse({'message': 'Cập nhật điểm danh thành công.'})
#
#     return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=400)

@login_required
@user_passes_test(is_staff)
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