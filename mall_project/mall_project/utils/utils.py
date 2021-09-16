def get_user(request):
    # 获取用户信息
    try:
        user = request.user
    except Exception:
        user = None
    else:
        if user and user.is_authenticated:
            return user
