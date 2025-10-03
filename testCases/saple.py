def count_int_and_char(s):
    num_count = 0
    char_count = 0
    for ch in s:
        if ch.isdigit():
            num_count += 1
        elif ch.isalpha():
            char_count += 1
    print(f"Number of integers: {num_count}")
    print(f"Number of characters: {char_count}")

# Example usage
input_str = "abc123xyz45"
count_int_and_char(input_str)
