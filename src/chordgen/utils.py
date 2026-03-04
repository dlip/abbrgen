def find_combinations(s, prefix="", index=0):
    """
    Recursively find every combination of letters in a string from left to right
    starting with the first character.

    Args:
    - s: The input string.
    - prefix: The current combination being built.
    - index: The current index in the string.

    Returns:
    - result: A list containing all combinations starting with the first character
              and excluding the empty string, sorted by shortest string first.
    """
    result = []
    if index == len(s):
        if prefix:
            result.append(prefix)
        return result

    # Include the current character only if it's the first character or part of a previous combination
    if index == 0 or prefix:
        result.extend(find_combinations(s, prefix + s[index], index + 1))

    # Exclude the current character
    result.extend(find_combinations(s, prefix, index + 1))

    return result


def find_all_combinations(string):
    if len(string) == 1:
        return [string]
    else:
        combos = []
        for i, char in enumerate(string):
            remaining_chars = string[:i] + string[i + 1 :]
            sub_combos = find_all_combinations(remaining_chars)
            for sub_combo in sub_combos:
                combos.append(char + sub_combo)
        return combos
