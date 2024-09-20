from flask import Flask, request, render_template, send_from_directory
import tempfile
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

app = Flask(__name__)

def generate_id_card(name, roll_no, distance_learning, city, center, campus, days_time, batch, user_image_path, logo_image_path, output_file):
    # Create the base card with a border
    card_width, card_height = 1000, 600
    border_color = (0, 153, 0)  # Green border color
    border_thickness = 10
    id_card = Image.new('RGB', (card_width, card_height), color='white')

    # Create a drawing context for adding borders
    draw = ImageDraw.Draw(id_card)
    draw.rectangle([(0, 0), (card_width - 1, card_height - 1)], outline=border_color, width=border_thickness)

    # Load the font (only Arial.ttf)
    font_path = "static/fonts/arial.ttf"  # Update this path if needed

    # Colors
    green_color = (0, 153, 0)  # Green color for labels
    black_color = (0, 0, 0)  # Black color for details
    red_color = (255, 0, 0)

    # Load font
    try:
        font_large = ImageFont.truetype(font_path, 40)  # For 'ID CARD' text
        font_medium = ImageFont.truetype(font_path, 30)  # For details
        font_small = ImageFont.truetype(font_path, 25)  # For smaller details
    except IOError:
        print("Font file not found. Please check the path.")
        return  # Exit if font is not found

    # Add logo to the background, centered
    if logo_image_path:
        logo_img = Image.open(logo_image_path).convert("RGBA")  # Ensure transparency
        logo_img = logo_img.resize((600, 300))
        logo_width, logo_height = logo_img.size
        position = ((card_width - logo_width) // 2, (card_height - logo_height) // 2)
        id_card.paste(logo_img, position, logo_img)

    # Draw ID card title
    draw.text((20, 20), "ID CARD", fill=green_color, font=font_large)

    # Adding details with labels in green and details in black
    draw.text((20, 100), "Name:", fill=green_color, font=font_medium)
    draw.text((150, 100), f"{name}", fill=black_color, font=font_medium)

    draw.text((20, 150), "Roll No:", fill=green_color, font=font_medium)
    draw.text((150, 150), f"{roll_no}", fill=black_color, font=font_medium)

    draw.text((20, 200), "Distance Learning:", fill=green_color, font=font_medium)
    draw.text((250, 200), f"{distance_learning}", fill=black_color, font=font_medium)

    draw.text((20, 250), "City:", fill=green_color, font=font_medium)
    draw.text((150, 250), f"{city}", fill=black_color, font=font_medium)

    draw.text((20, 300), "Center:", fill=green_color, font=font_medium)
    draw.text((150, 300), f"{center}", fill=black_color, font=font_medium)

    draw.text((20, 350), "Campus:", fill=green_color, font=font_medium)
    draw.text((150, 350), f"{campus}", fill=black_color, font=font_medium)

    draw.text((20, 400), "Days/Time:", fill=green_color, font=font_medium)
    draw.text((200, 400), f"{days_time}", fill=black_color, font=font_medium)

    draw.text((20, 450), "Batch:", fill=green_color, font=font_medium)
    draw.text((150, 450), f"{batch}", fill=black_color, font=font_medium)

    # Add user picture to the right side and apply a green border
    user_img = Image.open(user_image_path).convert("RGBA")  # Ensure transparency
    user_img = user_img.resize((150, 200))

    # Calculate the position for the image and border
    img_x, img_y = 800, 100
    id_card.paste(user_img, (img_x, img_y))

    # Draw a green border around the image
    draw.rectangle([(img_x - 5, img_y - 5), (img_x + 150 + 5, img_y + 200 + 5)], outline=green_color, width=5)

    # Add QR code below the details section
    qr_data = f"Name: {name}\nRoll No: {roll_no}\nBatch: {batch}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill='black', back_color='white').convert("RGBA")  # Ensure transparency
    qr_image = qr_image.resize((150, 150))
    id_card.paste(qr_image, (800, 400))

    # Add authorized signature text
    draw.text((700, 550), "Authorized Signature", fill="black", font=font_small)

    # Add a footer in red text with instructions
    draw.text((20, 550), "You must print color copy of voucher and ID card", fill=red_color, font=font_small)

    # Save the ID card to the output file
    id_card.save(output_file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        user_image = request.files['user_image']

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            user_image_path = temp_file.name
            user_image.save(user_image_path)

            # Static info
            distance_learning = "   No"
            city = "Karachi"
            center = "Bahria Auditorium"
            campus = "Karsaz"
            days_time = "Sunday - 09:00 AM to 01:00 PM"
            batch = "61"
            logo_image_path = "static/logo.png"  # Adjust this path
            output_file = os.path.join(tempfile.gettempdir(), 'id_card_output.png')

            generate_id_card(
                name=name,
                roll_no=roll_no,
                distance_learning=distance_learning,
                city=city,
                center=center,
                campus=campus,
                days_time=days_time,
                batch=batch,
                user_image_path=user_image_path,
                logo_image_path=logo_image_path,
                output_file=output_file
            )

            return send_from_directory(tempfile.gettempdir(), 'id_card_output.png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
