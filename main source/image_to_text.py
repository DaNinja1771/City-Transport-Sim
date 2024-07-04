from PIL import Image

# Open the image file
image = Image.open('map 25x25.png')

# Define color to letter mapping
color_to_letter = {
    (34, 177, 76): 'P',  # Green pixel
    (237, 28, 36): 'M',         # Red pixel
    (127, 127, 127): 'R',  # Grey pixel
    (0, 0, 0): 'F',         # Black pixel
    (255, 242, 0): 'H',         # Black pixel
    # Add more mappings as needed
}

# Open a text file for writing
with open('map 25x25.txt', 'w') as f:
    # Iterate over each pixel in the image
    for y in range(image.height):
        for x in range(image.width):
            # Get the RGB color of the pixel
            color = image.getpixel((x, y))
            # Map the color to a letter
            letter = color_to_letter.get(color, '?')
            # Write the letter to the text file
            f.write(letter)
        # Add a newline character at the end of each row
        f.write('\n')
