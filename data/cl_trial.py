#import library Regex, SQLite, Pandas
import re
import sqlite3
import pandas as pd
#import library untuk Flask
from flask import Flask, jsonify
from flask import request, make_response
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from #untuk memanggil file dari luar

#define deskripsi dari Swagger UI
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title' : LazyString(lambda: 'API Dokumentasi Data Preprocessing'),
    'version' : LazyString(lambda: '1.0.0'),
    'description' : LazyString(lambda: 'Dokumentasi preprocessing data text dan file'),    
},
    host = LazyString(lambda: request.host)
)

swagger_config ={
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flassger_static",
    "swagger_ui": True,
    "specs_route":"/docs/"
}

swagger = Swagger(app, template=swagger_template,
                 config=swagger_config)
#welcomepage
@app.route('/', methods=['GET'])
def get():
  return "Presenting API for text and file cleansing!"

#connect ke database
conn = sqlite3.connect('record.db', check_same_thread=False)

#mendefinisikan dan mengeksekusi query untuk tabel data kalau belum ada
#tabel data berisi kolom text kotor dan yang sudah dibersihkan 
conn.execute('''CREATE TABLE IF NOT EXISTS record(text varchar(255), text_clean varchar(255));''')


#mendefine endpoint, bahwa data yang diambil dari form yg diisi user
@swag_from("docs/hint.yml", methods=['POST'])
@app.route('/text', methods=['POST'])
def text_preprocessing():
    
    #mendapatkan inputan text
    text = request.form.get('text')
    
    #proses cleansing dengan regex

    text_clean = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))|\s|\W|rt|RT|USER|user|xfxfxx[\s]+|@[^s]+|\d|_', ' ', text)
    #\s untuk whitespace character [ \t\r\n\f]
    #\d untuk angka
    #\W untuk simbol

    #mendefinisikan dan melakukan eksekusi query dari original text ke yang sudah bersih
    conn.execute("INSERT INTO record (text, text_clean) VALUES ('"+ text +"', '"+ text_clean +"')")
    conn.commit()


    #Define response API
    json_response={
        'status_code': 200,
        'description': 'text cleanse',
        'data': text_clean, 
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/hint2.yml", methods=['POST'])
@app.route('/upload_file', methods=['POST'])

def upload_file():
  if request.method == 'POST':
    #import file
    file = pd.read_csv(request.files['file'], encoding='iso-8859-1')
    #regex file
    file_clean = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))|\s|\W|rt|RT|USER|user|xfxfxx[\s]+|@[^s]+|\d|_', ' ', str(file))
    
    conn.execute("INSERT INTO record (text, text_clean) VALUES ('"+ str(file) +"', '"+ str(file_clean) +"')")
    conn.commit()


    #Define response API
    json_response={
        'status_code': 200,
        'description': 'file cleanse',
        'data': file_clean, 
    }
    response_data = jsonify(json_response)
    return response_data
  
    
if __name__ == '__main__':
    app.run(debug = True)
