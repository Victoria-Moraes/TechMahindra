#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys
import requests

def main(dict):
    
    response = requests.get('git.git-run-220903-1846220.private.br-sao.codeengine.appdomain.cloud/api/v2/remember_managers')
    response = response.content.decode()
    return {"message":response}
