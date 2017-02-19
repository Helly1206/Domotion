from flask import Flask, Blueprint, render_template, g, request
from frontend import basicwebaccess

web_bwa = Blueprint('web_bwa', __name__, template_folder='templates')

def get_basicwebaccess():
    bwa = getattr(g, '_basicwebaccess', None)
    if bwa is None:
        bwa = g_basicwebaccess = basicwebaccess()
    return bwa

@web_bwa.teardown_request
def teardown_request(exception):
    bwa = getattr(g, '_basicwebaccess', None)
    if bwa is not None:
        del bwa

@web_bwa.route('/get', methods=['GET'])
def bwa_get():
    if request.method == "GET":
        tag=request.args.get('tag')
        return get_basicwebaccess().get(tag)
    else:
        return 'Bad request: Incorrect use of  this URL'

@web_bwa.route('/set', methods=['GET'])
def bwa_set():
    if request.method == "GET":
        tag=request.args.get('tag')
        value=request.args.get('value')
        return get_basicwebaccess().set(tag,value)
    else:
        return 'Bad request: Incorrect use of  this URL'