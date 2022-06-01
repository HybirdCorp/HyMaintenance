from django.shortcuts import render


def base_error_handler(request, exception=None, template_name="high_ui/errors/404.html", status_code=404):
    context = {}
    user = request.user
    if user and not user.is_anonymous:
        context["user_is_operator"] = user.has_operator_or_admin_permissions
        if user.company:
            context["company"] = user.company

    response = render(request, template_name, context=context, content_type=None, status=status_code)

    return response


def not_found_handler(request, exception=None, template_name="high_ui/errors/404.html"):
    return base_error_handler(request, exception, template_name, 404)


def internal_error_handler(request, exception=None, template_name="high_ui/errors/500.html"):
    return base_error_handler(request, exception, template_name, 500)


def permission_denied_handler(request, exception=None, template_name="high_ui/errors/403.html"):
    return base_error_handler(request, exception, template_name, 403)


def bad_request_handler(request, exception=None, template_name="high_ui/errors/400.html"):
    return base_error_handler(request, exception, template_name, 400)
