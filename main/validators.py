from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 25 * 1024 * 1024:  # 10 MiB in bytes
        raise ValidationError("The maximum file size that can be uploaded is 10 MiB")
    else:
        return value