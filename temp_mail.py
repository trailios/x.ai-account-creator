import random, time

from typing     import Dict, List, Any
from curl_cffi  import requests

class TempMail:
    """
    A class to create a temporary email account and get the verification link from the email.
    """

    def __init__(self):
        """
        Initializes the class with a random email address and a session object.
        The session object is created with a proxy and headers.
        """
        self.id: str  
        self.email: str
        self.token: str
        self.jwt: str  

        self.session: requests.Session = requests.Session()
        
        proxy: str | None = None # Using proxy, is recommended

        if proxy:
            self.session.proxies = {"all": "http://" + proxy}

        self.session.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "de,de-DE;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://mail.gw",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://mail.gw/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
        }

    def create_mail(self) -> str:
        """
        Creates a new email account and returns the email address.

        Returns:
            str: The email address of the created email account
        """
        try:
            email: str = f"t{random.randint(1,99)}ra{random.randint(1, 99)}il{random.randint(1,99)}i@oakon.com"
            password: str = "1122qqww"

            data: Dict[str, str] = {"address": email, "password": password}
            resp: requests.Response = self.session.post("https://api.mail.gw/accounts", json=data)

            if resp.status_code == 201:
                rj: Dict[str, Any] = resp.json()
                self.id = rj["@id"].split("/")[-1]
                self.email = email

                resp2: requests.Response = self.session.post("https://api.mail.gw/token", json=data)
                if resp2.status_code == 200:
                    rj2: Dict[str, Any] = resp2.json()
                    self.token = rj2["token"]

                    self.session.headers.update(
                        {"authorization": f"Bearer {self.token}"}
                    )

                    return email
                
        except Exception as e:
            raise Exception("Failed to create email, most likely an proxy issue.")

    def get_mail(self) -> str:
        """
        Gets the verification link from the email.

        Returns:
            str: The verification link
        """
        while True:
            try:
                resp: requests.Response = self.session.get("https://api.mail.gw/messages")
                rj: Dict[str, Any] = resp.json()
                messageslist: List[Dict[str, Any]] = rj["hydra:member"]

                if messageslist:
                    message: Dict[str, Any] = messageslist[0]
                    msg_url: str = f"https://api.mail.gw{message["@id"]}"

                    msg: requests.Response = self.session.get(msg_url)
                    mj: Dict[str, Any] = msg.json()

                    r: str = mj["text"]

                    link: str = r.split(
                        "If this link does not work, navigate to this URL in your browser:"
                    )[1].split(
                        "If you did not create a new account, please ignore this email and don't tap"
                    )[
                        0
                    ]

                    return link.replace("\n", "")

                time.sleep(1)

            except Exception as e:
                raise Exception(
                    "Failed to get verification link, most likely an proxy issue."
                )

