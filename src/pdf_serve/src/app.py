import pickle
import os
import logging
from subprocess import Popen
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

@app.route('/', methods=['POST'])
def main():

    base_string = "http://localhost:8080/files/temp/"
    temp_directory = "/tmp"
    shared_loc = "/shared/temp"

    # logging.info(request)

    # with open('/shared/dump/req.pickle', 'wb') as pick:
    #     pickle.dump(request.get_data(), pick)

    if 'file' not in request.files:
        # with open('/shared/dump/nofile.txt', 'w') as f:
        #     f.write('nofile')
        new_filename = 'error.pdf'
        good_flag = False
    else:
        file = request.files['file']
        # with open('/shared/dump/fileinfo.txt', 'w') as f:
        #     f.write(f"{file.filename}\n")
        #     f.write(f"{file.mimetype}\n")
        #     f.write(f"{file.content_length}\n")

        # save to a local temp directory
        filename = os.path.split(file.filename)[1]
        temp_file_path = os.path.join(temp_directory, filename)

        file.save(temp_file_path)

        # check to see if the file already exists
        if filename.endswith('.pptx'):
            new_filename = filename.replace('.pptx', '.pdf')
        elif filename.endswith('.ppt'):
            new_filename = filename.replace('.ppt', 'pdf')
        else:
            new_filename = 'error.pdf'

        new_file_location = os.path.join(shared_loc, new_filename)
        if os.path.exists(new_file_location):
            os.remove(new_file_location)

        # do conversion
        conversion_command = [f"/usr/bin/soffice", "--headless", "--convert-to", "pdf",  "--outdir", f"{shared_loc}", f"{temp_file_path}"]

        try:
            p = Popen(conversion_command)
            p.wait(timeout=100)
            good_flag = True
        except Exception as e:
            logging.warning(e)
            good_flag = False

        # remove the temp copy
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # make sure the converted file exists
        if os.path.exists(new_file_location):
            good_flag = True
        else:
            good_flag = False

    # pass back the new filepath
    pass_back = base_string + new_filename

    return jsonify({'text': pass_back, 'good_flag': good_flag})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')