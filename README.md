
# 🔐 CyberSecureX — Web-Based Personal & Network Security Toolkit

CyberSecureX is a modern, lightweight, and accessible **personal & small-business security toolkit**.  
Built using **FastAPI**, it provides intuitive web-based tools for everyday security tasks like:

- 🔍 Website vulnerability scanning  
- 🖧 Local network device discovery  
- 🛡️ Password strength & breach checking  
- 📁 Secure file sharing with password protection, expiry, and download limits  

---

## 📸 Features

| Feature                     | Description                                                                 |
|:----------------------------|:----------------------------------------------------------------------------|
| **Website Scanner**         | Check for open ports & common vulnerabilities on any public website.        |
| **LAN Device Discovery**    | Discover active devices on your local network, along with open ports.        |
| **Password Strength Checker** | Evaluate your password’s strength & check if it’s been breached online.     |
| **Secure File Transfer**    | Upload files securely with expiry time, max download limits, and optional password protection.|

---

## ⚙️ Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Database:** SQLite (via sqlite3)
- **Network Tools:** `nmap`, `scapy`, `httpx`, `socket`, `ssl`

---

## 🚀 Getting Started

### 📦 Requirements

- Python 3.9+
- `pip` (Python package manager)

### 📥 Install Dependencies

```bash
pip install -r requirements.txt
```

### ⚙️ Run the Application

```bash
python run.py
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 📂 Project Structure

```
CyberSecureX/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app startup
│   ├── database.py            # SQLite DB init + functions
│   ├── utils/
│   │   ├── scanner.py         # website vulnerability scanner logic
│   │   ├── lan_scan.py        # LAN device discovery logic
│   │   ├── password_checker.py# password strength & pwned check
│   │   └── file_share.py      # file sharing logic
│   ├── static/                # css, js, images, icons if any
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── scanner.html
│   │   ├── lan.html
│   │   ├── password.html
│   │   ├── secure_share.html
│   │   └── download_form.html
│   └── uploads/               # uploaded files storage
├── requirements.txt
└── run.py                     # entry point to run uvicorn
```

---

## 🔒 Security Notice

- This tool is for **personal or educational use only**.  
- Scanning networks or websites without permission is unethical and illegal.  
- Use responsibly on your own devices and networks.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ✨ Credits

Built with ❤️ by **Charan Teja B S , Chandan R , Bhaskara U R , Abhishek P B**

---

## 📌 Upcoming Improvements

- Add JWT-based user accounts & authentication  
- Deployable Dockerized version  
- Real-time scan logs & progress  
- Mobile-friendly UI redesign  
- Add Nmap full scan option  
