import re
import pyperclip  # For copying output to clipboard


def hex_to_rgb_tuple(hex_color):
    """Converts HEX format to an RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def hsl_to_rgb(h, s, l):
    """Converts HSL to RGB format."""
    s = s / 100
    l = l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    return r, g, b


def process_css_line(line):
    """Processes a line of CSS, converting HEX or HSL colors to RGB triplets and adding the `rgb(var())` line."""
    if line.strip() == "":
        return line

    # Match HEX color format
    match_hex = re.match(r"^\s*(--[\w-]+-x)\s*:\s*#([0-9a-fA-F]{6})\s*;\s*$", line)
    if match_hex:
        var_name = match_hex.group(1)
        hex_color = f"#{match_hex.group(2)}"
        rgb_tuple = hex_to_rgb_tuple(hex_color)

        processed_line = f"{var_name}: {rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]};\n"
        second_line = f"{var_name[:-2]}: rgb(var({var_name}));\n"
        return processed_line + second_line

    # Match HSL color format
    match_hsl = re.match(r"^\s*(--[\w-]+-x)\s*:\s*hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)\s*;\s*$", line)
    if match_hsl:
        var_name = match_hsl.group(1)
        h, s, l = map(int, match_hsl.groups()[1:])
        rgb_tuple = hsl_to_rgb(h, s, l)

        processed_line = f"{var_name}: {rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]};\n"
        second_line = f"{var_name[:-2]}: rgb(var({var_name}));\n"
        return processed_line + second_line

        # Log the line that failed to match
    raise ValueError(f"Line did not match expected format: {line.strip()}")


def ignore_comments(content):
    """Removes all multi-line comments from the input content."""
    return re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)


def process_css_file_with_output(file_path, output_path):
    """Reads the CSS file, processes lines, outputs the result, and writes to an output file."""
    processed_lines = []
    with open(file_path, "r") as f:
        content = f.read()

    # Remove multi-line comments
    content = ignore_comments(content)

    # Process each line while keeping empty lines intact
    for line in content.splitlines(keepends=True):
        try:
            processed_lines.append(process_css_line(line))
        except ValueError as e:
            # Log or print the error
            print(e)

    # Join the processed lines with ":root { }" block
    result = ":root {\n" + r"   /* DEFAULTS */" + "".join(processed_lines)

    # Copy the final result to the clipboard
    pyperclip.copy(result)

    result += "\n}\n"

    # Write to the output file
    with open(output_path, "w") as output_file:
        output_file.write(result)

    return result


# Path to the base_colors.css file (replace with the actual path)
file_path = "base_colors.css"
output_path = "results.css"

# Process the file, output the result, and write to results.css
output = process_css_file_with_output(file_path, output_path)
print(f"Processed CSS has been copied to clipboard and written to {output_path}:")
print(output)
