import requests


class RebootClient():
    def __init__(self) -> None:
        self.token_url = "https://qa2-accounts-onecloud.rakuten-it.com/auth/realms/roc"

    def get_token(self, hostname, region):

        bmaas_region = {
            "jpe2z" : "https://jpe2z-talaria1.bmaas.jpe2z.dcnw.rakuten/talaria/api/1.0/servers",
            "jpe1z" : "https://jpe1z-maas01.bmaas.jpe1z.dcnw.rakuten/talaria/"
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'client_credentials',
            'client_id': 'rns:roc:caas-k8s-master',
            'client_secret': '1b93ef57-7277-466c-a1d3-f199cca8b9fc'
        }

        response = requests.post(
            self.token_url + '/protocol/openid-connect/token', headers=headers, data=data, verify=True)

        server_headers = {
            'Authorization': f'Bearer {response.json()["access_token"]}',
        }

        params = (
            ('hostname', hostname),
        )

        server_response = requests.get(bmaas_region[region], headers=server_headers, params=params, verify=False)

        return {"id": server_response.json()["servers"][0]["id"]}