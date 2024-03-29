import requests
import os
import json

CLIENT_SECRET_QA = os.environ.get('CLIENT_SECRET_QA')
CLIENT_SECRET_PROD = os.environ.get('CLIENT_SECRET_PROD')


class RebootClient():
    def __init__(self) -> None:
        self.token_url = "https://qa2-accounts-onecloud.rakuten-it.com/auth/realms/roc"
        self.token_url_prod = "https://accounts-onecloud.rakuten-it.com/auth/realms/roc"
        self.bmaas_api_url = "api/1.0/servers"
        self.bmaas_server_url = "#/servers/"

        self.bmaas_region = {
            "jpe2z": "https://jpe2z-talaria1.bmaas.jpe2z.dcnw.rakuten/talaria/",
            "jpe1z": "https://jpe1z-maas01.bmaas.jpe1z.dcnw.rakuten/talaria/",
            "jpe2c": "https://jpe2c-talaria1.bmaas.jpe2c.dcnw.rakuten/talaria/",
            "jpe2b": "https://jpe2b-talaria1.bmaas.jpe2b.dcnw.rakuten/talaria/",
            "jpe1a": "https://jpe1a-talaria1.bmaas.jpe1a.dcnw.rakuten/talaria/",
            "jpc1a": "https://jpc1a-talaria.bmaas.jpc1a.dcnw.rakuten/talaria/",
            "jpw1a": "https://jpw1a-talaria.bmaas.jpw1a.dcnw.rakuten/talaria/",
            "euc1a": "https://euw1a-talaria.bmaas.euw1a.dcnw.rakuten/talaria/",
            "use1a": "https://use1a-talaria.bmaas.use1a.dcnw.rakuten/talaria/",
            "usw1a": "https://usw1a-talaria1.bmaas.usw1a.dcnw.rakuten/talaria/",
            "euw1a": "https://euw1a-talaria.bmaas.euw1a.dcnw.rakuten/talaria/"
        }

    def get_token(self, region):

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        if region == "jpe2z" or region == "jpe1z":
            token = CLIENT_SECRET_QA
            token_url = self.token_url
        else:
            token = CLIENT_SECRET_PROD
            token_url = self.token_url_prod

        data = {
            'grant_type': 'client_credentials',
            'client_id': 'rns:roc:caas-k8s-master',
            'client_secret': token.strip()
        }

        response = requests.post(
            token_url + '/protocol/openid-connect/token', headers=headers, data=data, verify=False)

        return response.json()["access_token"]

    def get_talaria_url(self, hostname, region):
        try:
            token = self.get_token(region)

            server_headers = {
                'Authorization': f'Bearer {token}',
            }

            params = (
                ('hostname', hostname),
            )

            server_response = requests.get(
                self.bmaas_region[region] + self.bmaas_api_url, headers=server_headers, params=params, verify=False)

            bmaas_id = server_response.json()["servers"][0]["id"]

            return (self.bmaas_region[region] + self.bmaas_server_url + str(bmaas_id), bmaas_id)
        except:
            return ("cannotconnect.sample/url", 0000)

    def reboot_by_id(self, bmaas_id, region):
        try:
            token = self.get_token(region)

            headers = {
                'Authorization': f'Bearer {token}',
                'accept': 'application/json',
                'content-type': 'application/json',
            }

            data = {"force": "false", "ids": [bmaas_id]}
            data = json.dumps(data)

            server_response = requests.post(
                self.bmaas_region[region] + self.bmaas_api_url + '/powerrestart', headers=headers, data=data, verify=False)

            return server_response.json()["message"]

        except:
            return "Request failed, please check your token."
