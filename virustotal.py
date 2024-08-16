import requests
import json
import os

def upload_file(file_path :str, result_json_path :str = None):
    proxies = {'http': 'http://127.0.0.1:8081', 'https': 'http://127.0.0.1:8081'}
    headers = {'X-Apikey': '...'}

    analysis_id = requests.post('https://www.virustotal.com/api/v3/files',
                                headers = headers,
                                proxies = proxies,
                                files = {'file': (file_path, open(file_path, 'rb'))}
                                ).json()['data']['id']

    response = requests.get(f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
                            headers = headers,
                            proxies = proxies).json()
    
    responseJson = json.dumps(response, ensure_ascii = False, indent = 4)

    if result_json_path:
        with open(result_json_path, 'w', encoding = 'UTF-8') as f:
            f.write(responseJson)

    return response, responseJson

def show_results(results :dict):
    results = results['data']['attributes']['results']
    if not results:
        exit(f'apiKey missing.')
    
    for item in results:
        engine_name = item
        category = results[item]['category']
        result = results[item]['result']

        if not result:
            continue

        print(f"{engine_name:<21s}: Category[{category}], Result[{result}].")

results = upload_file(r"H:\腾讯QQ\Bin\QQ.exe")[0]
show_results(results)
