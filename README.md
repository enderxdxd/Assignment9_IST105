# Assignment 9 - IST105

Django application for Cisco DNA Center integration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Configuration

Edit `dnac_config.py` to configure your DNA Center connection settings.

## Features

- DNA Center authentication
- Device management
- Interface monitoring
