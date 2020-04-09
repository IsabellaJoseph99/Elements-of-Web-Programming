import requests
from flask import Flask, request as flask_request
from flask import jsonify
import xml.etree.ElementTree as ET

app = Flask(__name__)

source = "https://raw.githubusercontent.com/devdattakulkarni/elements-of-web-programming/master/data/austin-pool-timings.xml"
data = requests.get(source)
root = ET.fromstring(data.text)

@app.route('/')
def website_display():
    return "Welcome to Austin Pool Information Website."

@app.route('/pools', methods=['GET'])
def get_all_pools_names():
    all_pool_names = []
    for pool in root.findall('row'):
        pool_name = pool.find('pool_name').text
        each_pool_dict = {'pool_name':pool_name}
        all_pool_names.append(each_pool_dict)
    pool_names_dict = {'pools':all_pool_names}
    return jsonify(pool_names_dict)

All_ETags = []

@app.route('/pools/<my_path_param>',methods=['GET'])
def get_one_pool_info(my_path_param):
    global All_ETags

    etag_req_header = flask_request.headers.get('If-None-Match')
    if etag_req_header in All_ETags:
        return "", 304

    for pool in root.findall('row'):
        pool_name = pool.find('pool_name').text
        if pool_name != my_path_param:
            continue
        if pool.find('status') is not None:
            status = pool.find('status').text
        if pool.find('phone') is not None:
            phone = pool.find('phone').text
        if pool.find('pool_type') is not None:
            pool_type = pool.find('pool_type').text
        pool_info_dict = {'pool_name': pool_name, 'status':status, 'phone':phone, 'pool_type':pool_type}

        ETag = {'ETag': pool_name}

        All_ETags.append(pool_name)
        return pool_info_dict, ETag

    return {'error': my_path_param + " not found"}, 404


if __name__ == '__main__':
    app.run()
