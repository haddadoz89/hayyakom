# Hayyakom

## Overview
`Hayyakom` is a web project built with Python, HTML, and CSS.  
The purpose of this project is to provide a clean and simple web interface for users. 

## Screenshots  
![campaign_information_investor](https://github.com/user-attachments/assets/0b0ce20b-4ee3-450a-afa3-792ce05bff33)

## ِ About Hayyakom
This platform connects individuals who are interested in investing in **small and medium-sized projects** with projects proposed by **business owners and users**.

Payments can be made directly through an integrated payment channel, allowing investors to purchase shares with:
- **Minimum investment**: 2,000 BHD
- **Maximum investment**: 5,000 BHD

---

## User Roles & Features

### Investors
- Register on the platform as an investor.
- Browse currently available projects or upcoming ones to express interest.
- Make payments directly through the **Stripe** payment channel.
- Access project owner details after completing a payment.

### Project Owners / Companies
- Register on the platform by creating a company profile, including:
  - Commercial registration number
  - Project name
  - Target campaign amount
- Once the project is approved and published:
  - View investor details and corresponding investment amounts on the campaign page.
- Edit campaign details after publication, **except** for the target amount (which cannot be changed once approved).

---

## Features
- Simple and clean user interface design  
- Python backend for handling logic  
- Responsive layout that works across devices  
- Organized HTML and CSS for easy customization  

---

## 📌 Key Links
- **Figma Wireframe**: [View Design](https://www.figma.com/design/Duf0QtyIc9JFoXCGqwpI0R/hayyakom?node-id=8-32&t=U0Wb9db4h9humufb-1)  
- **Trello Board**: [Project Management](https://trello.com/invite/b/68d2f87fbbc41b563f787829/ATTIb55793a50ce5f5b4a30242f8b326987976D09F73/hayyakom)


---

## Technologies Used
| Technology | Purpose |
|---|---|
| Python | Backend logic/server |
| HTML | Page structure |
| CSS | Styling and design |

---

## Getting Started (Local Setup)

1. Clone the repository:
   ```bash
   git clone https://github.com/haddadoz89/hayyakom.git
   ```

2. Navigate to the project directory:
   ```bash
   cd hayyakom
   ```

3. Ensure Python is installed. It's recommended to use a **virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Unix/macOS
   venv\Scripts\activate   # On Windows
   ```

4. Run the project locally:
   ```bash
   python manage.py runserver
   ```

5. Open your browser at:
   ```
   http://127.0.0.1:8000
   ```
   (or whichever port the project is running on)

---

## Project Structure

```
hayyakom/
├── templates/        # HTML templates
├── static/           # CSS / Images / JS files
├── src/              # Python backend code
├── README.md         
├── requirements.txt  # Project dependencies
└── ...               # Other files

---

## Deployment
