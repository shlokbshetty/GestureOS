# Gesture Control Desktop Application

> A comprehensive gesture recognition and control system for hands-free human-computer interaction

## Overview

This repository contains a modular, production-ready gesture recognition system that enables users to control their desktop through hand gestures captured via webcam. The project has evolved from a legacy CNN-based gesture classification model to a scalable architecture with backend services, desktop applications, and web interfaces.

---

## Project Evolution

### Legacy Architecture

The original implementation was a simple identification and classification model built with a 2D Convolutional Neural Network (CNN). This model was trained to recognize nine distinct static hand gestures and execute corresponding system-level actions:

- Scrolling
- Switching applications
- Adjusting volume
- Controlling media playback
- Taking screenshots

The legacy system achieved **100% accuracy** on the test set using YCrCb color-space segmentation and morphological filtering for hand detection.

**Research Documentation:** The legacy CNN model and its associated research are documented in `AIML-Research-Paper.pdf`. This paper represents the previous phase of the project and details the original gesture-recognition architecture, not the current implementation.

### Current Architecture

The system has undergone significant structural evolution to support scalability, modularity, and enhanced functionality:

- **Backend Services** - Modular Python backend with gesture recognition engine, state management, and controller logic
- **Desktop Application** - Cross-platform interface for real-time gesture recognition and system control
- **Frontend Web Interface** - Web-based dashboard for monitoring and configuration
- **Gesture Registry** - Centralized management of gesture definitions and mappings
- **Logging & Configuration** - Comprehensive logging infrastructure and environment-based configuration

---

## Current Implementation Status

### Fully Operational Modules

#### Backend Core
| Module | Purpose |
|--------|---------|
| `controller.py` | Orchestrates gesture recognition workflows and command execution |
| `engine.py` | Core gesture recognition engine with real-time processing |
| `gesture_registry.py` | Centralized registry for gesture definitions and mappings |
| `state_manager.py` | Manages application state and gesture recognition context |

#### Backend Utilities
| Module | Purpose |
|--------|---------|
| `config.py` | Environment-based configuration management |
| `logger.py` | Structured logging system with multiple output handlers |

#### Testing Infrastructure
Comprehensive test suites covering all backend modules:
- `test_controller.py` - Controller logic validation
- `test_engine.py` - Engine functionality and accuracy tests
- `test_gesture_registry.py` - Registry operations and gesture mapping tests
- `test_state_manager.py` - State management and context handling tests
- Utility tests for configuration and logging systems

#### Legacy Components
- `legacy-cnn-model/` - Original CNN-based gesture recognition model with dataset and training scripts

---

## Pending Tasks & In-Progress Work

- Desktop Application Enhancement - Expanding interface capabilities for improved UX
- Frontend Web Dashboard - Web-based monitoring and configuration interface
- Multi-Gesture Support - Dynamic gesture sequence recognition
- Cross-Platform Optimization - Windows, macOS, and Linux support
- Performance Optimization - Reduced latency and improved real-time processing

---

## Documentation

### Research Paper

A detailed research paper documenting the legacy CNN gesture-recognition architecture is available as `AIML-Research-Paper.pdf`. This paper includes:

- Literature survey on gesture recognition and human-computer interaction
- Methodology for CNN model design and training
- Dataset creation and preprocessing techniques
- Experimental results and performance metrics
- Future research directions

**Note:** This paper represents the previous phase of the project and documents the legacy CNN model, not the current modular architecture.

---

## Project Structure

```
.
├── backend/                          # Backend services and core logic
│   ├── controller.py                 # Gesture workflow orchestration
│   ├── engine.py                     # Recognition engine
│   ├── gesture_registry.py           # Gesture definitions and mappings
│   ├── state_manager.py              # State management
│   ├── models/                       # ML model storage
│   ├── utils/                        # Utility modules
│   │   ├── config.py                 # Configuration management
│   │   ├── logger.py                 # Logging infrastructure
│   │   └── test_*.py                 # Utility tests
│   └── test_*.py                     # Backend tests
├── desktop/                          # Desktop application
├── frontend/                         # Web-based interface
├── legacy-cnn-model/                 # Original CNN model and dataset
│   ├── cnn_model_train.py            # Model training script
│   ├── create_gestures.py            # Dataset creation
│   ├── display_gestures.py           # Gesture visualization
│   ├── gestures/                     # Gesture image dataset
│   └── confusion_matrix.png          # Model performance visualization
├── logs/                             # Application logs
├── venv/                             # Python virtual environment
├── .env                              # Environment variables
├── config.json                       # Configuration file
├── requirements.txt                  # Python dependencies
└── AIML-Research-Paper.pdf           # Legacy architecture research paper
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/gesture-control.git
cd gesture-control
```

**2. Create and activate virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure environment variables:
```bash
cp .env .env
```

Update `config.json` with system-specific settings.

---

## Running the System

### Backend Services
```bash
python -m backend.controller
```

### Desktop Application
```bash
python -m desktop.app
```

### Web Interface
```bash
python -m frontend.app
```

---

## Testing

### Run all tests
```bash
pytest
```

### Run specific test suite
```bash
pytest backend/test_engine.py -v
```

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Create a feature branch for new work
2. Write tests for new functionality
3. Ensure all tests pass before submitting a pull request
4. Follow PEP 8 style guidelines

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

## Acknowledgments

**Research Team:** Shashank Tandan, Shlok Shetty, Shree Santosh Yadav, Siddharth S Gadekar

**Institution:** School of Computer Science and Engineering, RV University, Bengaluru

---

## Contact

For questions or support, please open an issue on the repository or contact the development team.

