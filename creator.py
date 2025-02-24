from curl_cffi      import requests
from temp_mail      import Fetch
from threading      import Thread
from Log            import Log

mail = Fetch()
log = Log()

def get_token(params: dict[str, str]) -> str:
    resp: requests.Response = requests.get('http://127.0.0.1:5000/turnstile', params=params) # https://github.com/sexfrance/Turnstile-Solver
    return resp.json()["result"]

def main() -> None:

    session = requests.Session()
    session.impersonate = "chrome"
    session.allow_redirects = True


    session.cookies = {
        'cf_clearance': "hvenv3mkYoDzRBCE_kdXV6Zf_RbmtXh7DJgcKSSSKDc-1740421507-1.2.1.1-etAQTFwJJhc1Yn4ZyVuIdEYPjmTuOUvOyKC5l_IPNo6DaCMAL5CbcywEan_Ssy.GFBtI1jeVe.v6xpLSvTNnWUACyQBjyrr30wv.sgsmNJMoXHRKicUOrEikzbAwCbHFXmMt2gx7mzdCnj9yKaXX0v_WI44xNR8zoRgc8WN8yPUTRznCN4w1.l1L8xDCN.WTK4Dz0D2ZN2mXLvTesterVpgh2odCe0o1lzAeQ07pOxpn8gYjQAGaEh2jcRAa2X0IfqWaLvoUVan1owixzLbc16AsrzFn2HteEEtyHufJ2GLFz0Q7yVTpcnflcSifDOsISMKOxI5KYLOazXPqkbzJIQ",
    } # dont look at me... (replace if "Just a moment..")

    session.headers = {
        'accept': 'text/x-component',
        'accept-language': 'de,de-DE;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'text/plain;charset=UTF-8',
        'next-action': '4980d9ce0fd45632300c227043854174d46daf65',
        'origin': 'https://accounts.x.ai',
        'priority': 'u=1, i',
        'referer': 'https://accounts.x.ai/sign-up',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    }

    params: dict[str, str] = {
        "url": "https://accounts.x.ai/sign-up",
        "sitekey": "0x4AAAAAAAhr9JGVDZbrZOo0",
    }

    turnstile_token: str = get_token(params)

    if turnstile_token == None:
        log.Error("Failed to solve Turnstile")
        return
    
    log.Success(f"Solved Turnstile: {turnstile_token[:25]}...")

    email = mail.get_email()

    log.Info(f"Email: {email}")

    data: str = f'[{{"createUserAndSessionRequest":{{"email":"{email}","givenName":"traili","familyName":"cowyak","clearTextPassword":"12qw12qw**?A","tosAcceptedVersion":true}},"redirectLocation":"$undefined","turnstileToken":"{turnstile_token}"}}]'

    response: requests.Response = session.post(
        'https://accounts.x.ai/sign-up', data=data, impersonate="chrome"
    )

    session.cookies.update(response.cookies)
    rt: str = response.text

    if '1:"https://auth.grok.com/set-cookie?q=ey' in rt:
        log.Success("Successfully signed up")
        token_url: str = rt.split('1:"')[1].split('"')[0]
        r: requests.Response = session.get(token_url, impersonate="chrome")

        session.cookies.update(r.cookies)

        verif = mail.get_email_code(email).split("<p>")[1].split("</p>")[0].replace("amp;", "")

        if verif:
            log.Info(f"Verifying...")

            r = session.get(verif, impersonate="chrome", allow_redirects=True)

            r.raise_for_status()

            log.Success("Successfully verified")

            sso = r.cookies.get("sso")
            with open("sso.txt", "a") as f:
                f.write(sso + "\n")
    else:
        try:
            error: str = rt.split('1:')[1]
            print(error)
        except:
            print("CF blocked.")

if __name__ == "__main__":
    threads = []
    for i in range(10):
        t = Thread(target=main)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
