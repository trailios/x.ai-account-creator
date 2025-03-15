from multiprocessing import Process
from typing          import List, Dict
from curl_cffi       import requests
from temp_mail       import TempMail
from threading       import Thread
from Log             import Log

import os

log = Log()


def get_token(params: Dict[str, str]) -> str:
    """
    Gets CF turnstile token from a local server.

    Args:
        params (Dict[str, str]): Parameters to send to the server.

    Returns:
        str: The token.
    """
    try:
        resp: requests.Response = requests.get(
            "http://127.0.0.1:5000/turnstile", # https://github.com/Theyka/Turnstile-Solver should work
            params=params
        )
        return resp.json()["result"]
    except:
        return None


def main() -> None:
    """
    Main function of handling, generating and verifying accounts.
    """
    while True:
        try:
            session: requests.Session = requests.Session()
            session.impersonate = "chrome"
            session.allow_redirects = True

            session.cookies = {
                "cf_clearance": "i aint reversing this.",
            }

            session.headers = {
                "accept": "text/x-component",
                "accept-language": "de,de-DE;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "content-type": "text/plain;charset=UTF-8",
                "next-action": "4980d9ce0fd45632300c227043854174d46daf65",
                "origin": "https://accounts.x.ai",
                "priority": "u=1, i",
                "referer": "https://accounts.x.ai/sign-up",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            }

            mail: TempMail = TempMail()

            email: str = mail.create_mail()

            if email == None:
                continue

            params: Dict[str, str] = {
                "url": "https://accounts.x.ai/sign-up",
                "sitekey": "0x4AAAAAAAhr9JGVDZbrZOo0",
            }

            turnstile_token: str = get_token(params)

            if turnstile_token == None:
                log.Error("Failed to solve Turnstile")
                return

            log.Success(f"Solved Turnstile: {turnstile_token[:25]}...")

            data: str = (
                f'[{{"createUserAndSessionRequest":{{"email":"{email}","givenName":"REDACTED","familyName":"REDACTED","clearTextPassword":"1122qqww**?A","tosAcceptedVersion":true}},"redirectLocation":"$undefined","turnstileToken":"{turnstile_token}"}}]'
            )

            response: requests.models.Response = session.post(
                "https://accounts.x.ai/sign-up", data=data, impersonate="chrome"
            )

            session.cookies.update(response.cookies)
            rt: str = response.text

            if '1:"https://auth.grok.com/set-cookie?q=ey' in rt:
                log.Success("Successfully signed up")
                token_url: str = rt.split('1:"')[1].split('"')[0]
                r: requests.Response = session.get(token_url, impersonate="chrome")

                session.cookies.update(r.cookies)

                verif: str = mail.get_mail()

                if verif:
                    r: requests.Response = session.get(verif, impersonate="chrome", allow_redirects=True)

                    if r.status_code == 200:
                        log.Success("Successfully verified")

                        sso: str = r.cookies.get("sso")
                        with open("sso.txt", "a") as f:
                            f.write(sso + "\n")

                    else:
                        log.Error("Failed to verify.")

            else:
                try:
                    error: str = rt.split("1:")[1]
                    print(error)

                except:
                    print("CF blocked.")
                    os._exit(1)

        except Exception as e:
            log.Error(e)


def threads():
    threads: List[Thread] = []
    for i in range(5):
        t = Thread(target=main)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    procceses: List[Process] = []
    for i in range(5):
        p = Process(target=threads)
        p.start()
        procceses.append(p)

    for p in procceses:
        p.join()
