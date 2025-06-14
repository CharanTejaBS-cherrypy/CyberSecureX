import hashlib
import aiohttp

# ------------------- Password Strength Evaluation -------------------

def evaluate_strength(password: str) -> str:
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?`~" for c in password)

    score = sum([length >= 8, has_upper, has_lower, has_digit, has_special])

    if score <= 2:
        return "Weak"
    elif score in [3, 4]:
        return "Moderate"
    else:
        return "Strong"

# ------------------- Pwned Passwords API Check -------------------

async def check_pwned(password: str) -> int:
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return 0

            text = await response.text()
            hashes = (line.split(":") for line in text.splitlines())

            for h, count in hashes:
                if h == suffix:
                    return int(count)
    return 0
