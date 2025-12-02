def right_triangle(base):
    for i in range(1, base + 1):
        stars = '*' * i
        print(stars)

def inverted_triangle(base):
    for i in range(base, 0, -1):
        stars = '*' * i
        print(stars)

def pyramid(base):
    for i in range(1, base + 1):
        stars = '*' * (2 * i - 1)
        print(stars.center(2 * base - 1))

def inverted_pyramid(base):
    for i in range(base, 0, -1):
        stars = '*' * (2 * i - 1)
        print(stars.center(2 * base - 1))

def diamond(base):
    pyramid(base)
    inverted_triangle(base - 1)

def hollow_right_triangle(base):
    for i in range(1, base + 1):
        if i == base:
            stars = '*' * i
        else:
            stars = '*' + ' ' * (i - 2) + '*' if i > 1 else '*'
        print(stars)

def hollow_pyramid(base):
    for i in range(1, base + 1):
        if i == base:
            stars = '*' * (2 * base - 1)
        else:
            stars = '*' + ' ' * (2 * i - 3) + '*' if i > 1 else '*'
        print(stars.center(2 * base - 1))

def hollow_diamond(base):
    hollow_pyramid(base)
    for i in range(base - 1, 0, -1):
        if i == 1:
            stars = '*'
        else:
            stars = '*' + ' ' * (2 * i - 3) + '*' if i > 1 else '*'
        print(stars.center(2 * base - 1))

# Accept user input for base number and pattern type
base = int(input("Enter the base number: "))
pattern_name = input("Enter the star pattern (right_triangle, inverted_triangle, pyramid, inverted_pyramid, diamond, hollow_right_triangle, hollow_pyramid, hollow_diamond): ").strip().lower()

if pattern_name == "right_triangle":
    right_triangle(base)
elif pattern_name == "inverted_triangle":
    inverted_triangle(base)
elif pattern_name == "pyramid":
    pyramid(base)
elif pattern_name == "inverted_pyramid":
    inverted_pyramid(base)
elif pattern_name == "diamond":
    diamond(base)
elif pattern_name == "hollow_right_triangle":
    hollow_right_triangle(base)
elif pattern_name == "hollow_pyramid":
    hollow_pyramid(base)
elif pattern_name == "hollow_diamond":
    hollow_diamond(base)
else:
    print("Invalid pattern name.")