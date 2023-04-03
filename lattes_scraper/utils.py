def fill_list(list_, object_, size):
    """Complements the list with the informed object until reaching the desired size."""
    while len(list_) < size:
        list_.append(object_)
    return list_