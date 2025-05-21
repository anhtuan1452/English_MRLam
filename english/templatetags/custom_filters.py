from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Dùng để tách chuỗi theo ký tự phân tách (arg).
    Trả về chính giá trị nếu không phải là chuỗi để tránh lỗi.
    """
    if isinstance(value, str):
        return value.split(arg)
    return value  # hoặc return [] nếu bạn muốn luôn trả về danh sách

@register.filter
def zip_lists(list1, list2):
    """
    Gộp hai danh sách lại thành danh sách các tuple.
    """
    try:
        return zip(list1, list2)
    except TypeError:
        return []  # Trả về danh sách rỗng nếu có lỗi
