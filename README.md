# Scalable Thread Management Library Website

A modern, interactive website showcasing the capabilities of the Scalable Thread Management Library. The website features real-time performance monitoring, interactive charts, and a clean, responsive design.

## Features

- Real-time thread performance monitoring
- Interactive dashboard with live metrics
- Dynamic charts for CPU and memory usage
- Thread control interface
- Responsive design for all devices
- Modern UI with Bootstrap 5
- Real-time updates using Socket.IO

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd thread-management-website
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
thread-management-website/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/
│   └── css/
│       └── style.css     # Custom styles
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── dashboard.html    # Performance dashboard
    ├── features.html     # Features page
    ├── documentation.html # Documentation page
    └── contact.html      # Contact page
```

## API Endpoints

- `GET /` - Home page
- `GET /dashboard` - Performance dashboard
- `GET /features` - Features page
- `GET /documentation` - Documentation page
- `GET /contact` - Contact page
- `POST /api/start_threads` - Start new threads
- `POST /api/stop_threads` - Stop all threads
- `GET /api/performance` - Get performance metrics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask for the web framework
- Bootstrap for the UI components
- Plotly for interactive charts
- Socket.IO for real-time communication 