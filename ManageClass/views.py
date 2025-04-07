from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from .models import LopHoc, KhoaHoc


class DanhSachLopHocView(ListView):
    model = LopHoc
    template_name = 'ql_lophoc.html'
    context_object_name = 'danh_sach_lop'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('search', '')
        if search_term:
            queryset = queryset.filter(
                Q(ten_lop__icontains=search_term) |
                Q(khoa_hoc__ten_khoa_hoc__icontains=search_term)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search', '')
        context['khoa_hoc_list'] = KhoaHoc.objects.all()
        return context


def them_lop_hoc_view(request):
    if request.method == 'POST':
        ten_lop = request.POST.get('ten_lop')
        khoa_hoc_id = request.POST.get('khoa_hoc')
        ngay_bat_dau = request.POST.get('ngay_bat_dau')
        ngay_ket_thuc = request.POST.get('ngay_ket_thuc')
        si_so = request.POST.get('si_so')
        trang_thai = request.POST.get('trang_thai')

        try:
            khoa_hoc = KhoaHoc.objects.get(id=khoa_hoc_id)

            LopHoc.objects.create(
                ten_lop=ten_lop,
                khoa_hoc=khoa_hoc,
                so_luong_hoc_vien=si_so,
                ngay_bat_dau=ngay_bat_dau,
                ngay_ket_thuc=ngay_ket_thuc,
                trang_thai=trang_thai
            )

            messages.success(request, f'Lớp học "{ten_lop}" đã được tạo thành công!')
            return redirect('ManageClass:danh_sach_lop')
        except KhoaHoc.DoesNotExist:
            messages.error(request, 'Khóa học không tồn tại.')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    context = {
        'khoa_hoc_list': KhoaHoc.objects.all().order_by('ten_khoa_hoc')
    }
    return render(request, 'them_lop_hoc.html', context)


def chi_tiet_lop_hoc(request, lop_id):
    lop = get_object_or_404(LopHoc, id=lop_id)
    return render(request, 'chi_tiet_lop_hoc.html', {'lop': lop})


class CapNhatLopHocView(UpdateView):
    model = LopHoc
    template_name = 'cap_nhat_lop_hoc.html'
    fields = ['ten_lop', 'khoa_hoc', 'so_luong_hoc_vien', 'trang_thai', 'ngay_bat_dau', 'ngay_ket_thuc']
    success_url = reverse_lazy('ManageClass:danh_sach_lop')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['khoa_hoc_list'] = KhoaHoc.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Lớp học "{form.instance.ten_lop}" đã được cập nhật thành công!')
        return super().form_valid(form)


def xoa_lop_hoc(request, lop_id):
    if request.method == 'POST':
        lop = get_object_or_404(LopHoc, id=lop_id)
        ten_lop = lop.ten_lop
        lop.delete()
        messages.success(request, f'Lớp học "{ten_lop}" đã được xóa thành công!')
        return redirect('ManageClass:danh_sach_lop')
    return redirect('ManageClass:danh_sach_lop')


def xoa_lop_hoc_ajax(request, lop_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            lop = get_object_or_404(LopHoc, id=lop_id)
            ten_lop = lop.ten_lop
            lop.delete()
            return JsonResponse({'success': True, 'message': f'Lớp học "{ten_lop}" đã được xóa thành công!'})
        except LopHoc.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Lớp học không tồn tại.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'}, status=405)
