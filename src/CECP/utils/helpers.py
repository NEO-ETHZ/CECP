
def flatten(nested_list: list) -> list:
    """Flattens a list, unpacking all nested lists.
    
    Parameters
    ----------
    nested_list : list
        List potentially containing further lists as elements.
    Returns
    -------
    list of flatened elements
    """
    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list
            