################################################################################
#                                                                              #
#   Coauthors: Antoine Eddi (@antoeddi) & Philippe Desmaison (@desmaisn)       #
#                                                                              #
#   Team: EMEA Partner Solutions Architects                                    #
#   Date: March 2016                                                           #
#                                                                              #
################################################################################

## Import ##
from flask import Flask, jsonify, request, send_from_directory, make_response
from itsdangerous import Signer
import urllib2

from geopy.geocoders import Nominatim

from PIL import Image
import cv2, numpy

import uuid, os, random, time, json


## Init ##
# Init flask object
app = Flask(__name__)

# Init geopy object
geolocator = Nominatim()

# Init cookie signer with our secret key
signer = Signer("*{0!0C}]P1>12&y,(r*(8K :z*q43&\>8d+&P{g0_1'OU*U+<3'~'V0D:\*pY1!Z")

# Get useful directories path
current_dir = os.path.dirname(os.path.realpath(__file__))
process_dir = current_dir + '/process_img/'
assets_dir = process_dir + 'assets/'


## Aux. functions - image processing / mustache part ##
# Get noses coordinates with OpenCV
def get_noses_coord(image):
    cascades_dir = current_dir + '/haarcascades/'
    face_cascade = cv2.CascadeClassifier(cascades_dir + 'frontalface_default.xml')
    nose_cascade = cv2.CascadeClassifier(cascades_dir + 'mcs_nose.xml')
    img_gray = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(
        img_gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100, 100),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    noses_coord = []
    for face in faces:
        x, y, w, h = face
        roi = img_gray[y: y + h, x: x + w]
        noses = nose_cascade.detectMultiScale(
            roi,
            scaleFactor=1.2,
            minNeighbors=8,
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        if len(noses):
            nx, ny, nw, nh = noses[0]
            noses_coord.append((nx + x, ny + y, nw, nh))
    return noses_coord

# Calculate mustache size and position
def calc_mustache_coord(nose_coord, must_img_size):
    x, y, w, h = nose_coord
    ratio = (w * 3) / float(must_img_size[0])
    mx = x - w
    my = ((65 * h) / 100) + y
    mw = int(must_img_size[0] * ratio)
    mh = int(must_img_size[1] * ratio)
    return ((mw, mh), (mx, my))

# Paste mustache(s) on the top layer
def add_mustaches(image, top_layer):
    noses_coord = get_noses_coord(image)
    for nose_coord in noses_coord:
        random_num = str(random.randint(1, 11))
        mustache_img = Image.open(assets_dir + 'mustaches/' + random_num + '.png')
        size, offset = calc_mustache_coord(nose_coord, mustache_img.size)
        img_paste = mustache_img.resize(size)
        top_layer.paste(img_paste, offset)
    return len(noses_coord)


## Aux. functions - image processing / logo part ##
# Calculate logo size
def calc_logo_size(image_size, logo_size):
    ratio = float(image_size[0] / 4) / logo_size[0]
    new_size = [0, 0]
    new_size[0] = int(logo_size[0] * ratio);
    new_size[1] = int(logo_size[1] * ratio);
    return (new_size[0], new_size[1])

# Calculate logo offset
def calc_logo_offset(image_size, logo_size):
    margin = int(logo_size[1] / 3)
    offset = [0, 0]
    offset[0] = image_size[0] - logo_size[0] - margin
    offset[1] = image_size[1] - logo_size[1] - margin
    return (offset[0], offset[1])

# Paste AWS logo on the top layer
def add_logo(image, top_layer):
    logo = Image.open(assets_dir + 'logo.jpg')
    size = calc_logo_size(image.size, logo.size)
    offset = calc_logo_offset(image.size, size)
    logo = logo.resize(size)
    top_layer.paste(logo, offset)

# Resize image if (H or W > 1200), add logo and mustaches to a top layer then return image merged with top layer
def process_image(base_file):
    image = Image.open(base_file).convert('RGB')
    if image.size[0] > 1200 or image.size[1] > 1200:
        ratio = min(1200./image.size[0], 1200./image.size[1])
        image = image.resize((int(image.size[0] * ratio), int(image.size[1] * ratio)))
    top_layer = Image.new('RGBA', image.size, (0,0,0,0))
    add_logo(image, top_layer)
    count = add_mustaches(image, top_layer)
    processed = Image.composite(top_layer, image, top_layer)
    return processed, count


## Aux. functions - image saving ##
# Check if filename already exist, until is unavailable append '-2'
def get_valid_save_filename(current_filename, save_dir):
    split = current_filename.split('.')
    current_filename = '.'.join(split[:-1])
    extension = split[-1]
    list_dir = os.listdir(save_dir)
    while 42:
        if any(item.startswith(current_filename) for item in list_dir):
            current_filename += '-2'
        else:
            break
    save_filename = current_filename + '.' + extension
    return save_filename

# Save image file into the right folder
def save_image(uuid, image, filename, extension):
    save_dir = process_dir + 'processed/' + uuid + '/'
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    save_filename = get_valid_save_filename(filename, save_dir)
    image.save(save_dir + save_filename, extension)
    return save_filename


## Main functions - image related ##
# POST handler for image uploading / processing, GET handler for image downloading
@app.route('/image', methods=['GET', 'POST'])
def image_handling():
    if request.method == 'POST':
        file = request.files['file']
        image, count = process_image(file)
        extension = file.content_type.split('/')[1]
        filename = file.filename
        cookie = get_cookie_data(request)
        save_filename = save_image(cookie['uuid'], image, filename, extension)
        total = count + cookie['count']
        response = make_response(jsonify(filename=save_filename, count=total))
        set_cookie(response, cookie['uuid'], total)
        return response
    elif request.method == 'GET':
        filepath = request.args.get('filepath')
        return send_from_directory(process_dir + 'processed/', filepath)

# GET handler for images listing
@app.route('/images/list', methods=['GET'])
def list_images():
    cookie = get_cookie_data(request)
    user_dir = process_dir + 'processed/' + cookie['uuid'] + '/'
    img_list = []
    if os.path.isdir(user_dir):
        img_list = os.listdir(user_dir)
        img_list.sort(key=lambda x: os.path.getctime(os.path.join(user_dir, x)) * -1)
    return jsonify(list=img_list)


## Main functions - info related ##
# GET handlers returning public IP, postal address from GPS point and instance meta-data
@app.route('/infos/<param>', methods=['GET'])
def get_infos(param):
    if param == 'ip':
        return jsonify(public_ip=request.remote_addr)
    elif param == 'location':
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        location = geolocator.reverse(latitude + "," + longitude)
        splits = location.address.split(', ')
        if 8 <= len(splits) <= 9:
            x = len(splits) - 9
            address = " ".join((splits[1 + x] + " -", splits[7 + x], splits[2 + x] + ",", splits[8 + x]))
        else:
            address = location.address
        return jsonify(address=address)
    elif param == 'instance':
        az = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()
        instance = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
        return jsonify(az=az, instance=instance)


# POST handler storing client infos into local file
@app.route('/infos', methods=['POST'])
def send_infos():
    cookie = get_cookie_data(request)
    infos = request.json
    save_dir = current_dir + '/logs/' + cookie['uuid'] + '/'
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    filename = time.strftime("%Y-%m-%d_%H%M:%S", time.gmtime())
    with open(save_dir + filename + '.json', 'w') as outfile:
        json.dump(infos, outfile)
    return ''


## Aux. functions - managing cookie ##
# Check if cookie contain valid signed values
def is_valid_cookie(cookie):
    try:
        unsigned = signer.unsign(cookie)
        return unsigned
    except:
        return ''

# Generate a new uuid that is not used already
def get_available_uuid():
    processed_dir = process_dir + 'processed/'
    if not os.path.isdir(processed_dir):
        os.makedirs(processed_dir)
    uuid_unavailable = os.listdir(processed_dir);
    while 42:
        new_uuid = str(uuid.uuid1())
        if new_uuid not in uuid_unavailable:
            return new_uuid

# Get cookie values
def get_cookie_data(request):
    cookie = request.cookies.get('Session')
    cookie_raw = is_valid_cookie(cookie).split('.')
    cookie_data = {'uuid':cookie_raw[0], 'count':int(cookie_raw[1])}
    return cookie_data

# Generate cookie that expire in 2 weeks
def set_cookie(response, uuid, count):
    signed = signer.sign(uuid + '.' + str(count))
    expires_date = time.time() + 14 * 24 * 3600
    expires_date = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expires_date))
    response.set_cookie('Session', signed, expires=expires_date)


## Main functions - cookie related ##
# Check if cookie from request is valid, if not generate a new one
@app.route('/cookie', methods=['GET'])
def get_cookie():
    cookie = request.cookies.get('Session')
    if not cookie or not is_valid_cookie(cookie):
        uuid = get_available_uuid()
        count = 0
    else:
        valid_data = get_cookie_data(request)
        uuid = valid_data['uuid']
        count = valid_data['count']
    response = make_response(jsonify(uuid=uuid, count=count))
    set_cookie(response, uuid, count)
    return response


if __name__ == '__main__':
    app.run()
