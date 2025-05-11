<div align="center">

  <img src="Images/App_Icon.ico" alt="logo" width="200" height="auto" />
  <h1>Awesome Readme Template</h1>
  
  <p>
    Daily Journal Proof-of-Concept 
  </p>
</div>

# :notebook_with_decorative_cover: Table of Contents

- [About the Project](#star2-about-the-project)
  * [Screenshots](#camera-screenshots)
  * [Tech Stack](#space_invader-tech-stack)
  * [Features](#dart-features)
  * [Color Reference](#art-color-reference)
  * [Environment Variables](#key-environment-variables)
- [Getting Started](#toolbox-getting-started)
  * [Installation](#gear-installation)
  * [Run Locally](#running-run-locally)
- [Usage](#eyes-usage)
- [Roadmap](#compass-roadmap)
- [Contributing](#wave-contributing)
  * [Code of Conduct](#scroll-code-of-conduct)
- [FAQ](#grey_question-faq)
- [License](#warning-license)
- [Contact](#handshake-contact)
- [Acknowledgements](#gem-acknowledgements)
  
## About the Project

This application is a digital diary developed entirely in Python, using CustomTkinter for the graphical interface and SQL for data management. Unlike traditional CustomTkinter-based applications, the pvInStyle library has been integrated here, enabling smooth animations such as fade-in and fade-out, as well as advanced page management. Thanks to this integration, each button can control entire pages with multiple complex elements instead of single widgets, making the interface more dynamic, modern, and structured. Additionally, by using SQL, the application supports multiple users, each with their own personal password to access the diary in a private and secure manner.

This application is not intended for distribution: it is a proof of concept developed to demonstrate to myself that Python is capable of handling lightweight yet functional GUIs, even with complex animations and pages.

Author: Alvise, 2025.

> **Note:** This project is provided as a **proof-of-concept** and is not intended for production use.

## Installation

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Copy the folders:
   
   ```bash
   Copy all the folders and the sourcecode into the same folder where the virtual environment was created.
   ```
4. Run the app:

   ```bash
   python diario.py
   ```

## Third-Party Licenses

The full list of third-party dependencies and their licenses can be found in [`DEPENDENCY_LICENSES.md`](DEPENDENCY_LICENSES.md).
