# users/utils.py
def get_effective_user(user):
    """
    Returns the actual 'owner' user — either the user themselves if they're a lawyer,
    or their parent user if they're an assistant.
    """
    if user.role == 'assistant':
        return user.parent_user
    return user
