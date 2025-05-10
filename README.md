# Daily Journal Proof-of-Concept

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
   
3. Copy all folders and source code into the folder containing the virtual environment.
   
4. Run the app:

   ```bash
   python diario.py
   ```

## Third-Party Licenses

The full list of third-party dependencies and their licenses can be found in [`DEPENDENCY_LICENSES.md`](DEPENDENCY_LICENSES.md).
