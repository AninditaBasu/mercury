from flask import Flask
from flask import request
from flask import render_template
import requests
import json

api_base_url = 'https://od-api.oxforddictionaries.com/api/v2/'
target_language = 'en'

with open('./static/config.json', encoding="utf8") as configjsn:
    credentials = json.load(configjsn)
for key, value in credentials.items():
    if key == "app_id":
        app_id = value
    if key == "app_key":
        app_key = value
    if key == "source_language":
        source_language = value

with open('./static/interface.json', encoding="utf8") as interfacejsn:
    interfacetext = json.load(interfacejsn)
for key, value in interfacetext.items():
    if key == "title":
        title = value
    if key == "language_pair":
        language_pair = value
    if key == "translate_label":
        translate_label = value
    if key == "translate_button":
        translate_button = value
    if key == "translation_error":
        translation_error = value
    if key == "audio_error":
        audio_error = value
    if key == "example_sentences":
        example_sentences = value
    if key == "back_message":
        back_message = value
    if key == "pronunciation":
        pronunciation = value

print('Mercury is running.')

app = Flask(__name__)

@app.route('/')
def word_get():
    return render_template("word_enter.html", title=title, language_pair=language_pair, translate_label=translate_label, translate_button=translate_button)

@app.route('/', methods=['POST'])
def word_process():
    word_id = request.form['sourceword']
    url = api_base_url + 'translations/' + source_language + '/' + target_language + '/' + word_id
    trans = []
    trans_mini = {}
    plain_list = ''
    try:
        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
        json_data = json.loads(json.dumps(r.json()))
        target_word_trans = json_data['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
        for item in target_word_trans:
            for entry in item['translations']:
                word_en = entry['text']
                trans_mini.update({'word_en': word_en})
                print('- - -', word_en)
                if ' ' in word_en:
                    print('no sound file')
                    trans_mini.update({'sound': ''})
                elif '-' in word_en:
                    print('no sound file')
                    trans_mini.update({'sound': ''})
                else:
                    url = api_base_url + 'entries/en-gb/' + word_en.lower() + '?fields=pronunciations&strictMatch=false'
                    try:
                        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
                        json_data = json.loads(json.dumps(r.json()))
                        # print(json_data)
                        target_word_sound = json_data['results'][0]['lexicalEntries'][0]['pronunciations'][0][
                            'audioFile']
                        print('This is how you pronounce', word_en, ":", target_word_sound)
                        trans_mini.update({'sound': target_word_sound})
                    except:
                        print('No sound file')
                        trans_mini.update({'sound': ''})
                example_list = []
                try:
                    url = api_base_url + 'sentences/en/' + word_en + '?strictMatch=true'
                    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
                    json_data = json.loads(json.dumps(r.json()))
                    target_word_sentences = json_data['results'][0]['lexicalEntries'][0]['sentences']
                    counter = 0
                    while counter < 3:
                        example = target_word_sentences[counter]['text']
                        print(example)
                        example_list.append(example)
                        counter = counter + 1
                except:
                    print('No example sentences')
                    example_list.append('')
                trans_mini.update({'example': example_list})
                print(trans_mini)
                trans.append(trans_mini)
                print(trans)
                trans_mini = {}
        for item in trans:
            plain_list = plain_list + (item['word_en']) + '; '
        plain_list = plain_list[: -2]
    except:
        print('There was an error. Go back to the previous page and try with another word.')
        trans_mini.update({'Error': translation_error})
        trans.append(trans_mini)
        plain_list = '------'
    print(trans)
    print(plain_list)
    return render_template('word_out.html', trans=trans, word_id=word_id, plain_list=plain_list, title=title, language_pair=language_pair, audio_error=audio_error, back_message=back_message, example_sentences=example_sentences, pronunciation=pronunciation)

if __name__ == "__main__":
        #port = int(os.environ.get("PORT", 5000))
        #app.run(host='0.0.0.0', port=port)
        app.run() #for local