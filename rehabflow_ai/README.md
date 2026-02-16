# RehabFlow AI

AI-Powered Physiotherapy Management System using Google's MedGemma

## Overview

RehabFlow AI is a production-grade physiotherapy management system that leverages Google's MedGemma medical AI model to provide intelligent treatment planning, progress tracking, and patient assessment capabilities.

## Features

- **AI-Powered Assessment**: Automated patient evaluation using MedGemma
- **Treatment Plan Generation**: AI-generated personalized rehabilitation plans
- **Session Management**: Real-time physiotherapy session tracking
- **Progress Analytics**: Comprehensive progress visualization and reporting
- **Medical-Grade Security**: Input sanitization and validation
- **Concurrent Processing**: Thread-safe operations for high performance

## Architecture

```
rehabflow_ai/
├── app.py                  # Main application entry point
├── ai/                     # AI model integration
│   ├── medgemma.py        # MedGemma model wrapper
│   ├── prompt_builder.py  # Medical prompt construction
│   ├── plan_generator.py  # Treatment plan generation
│   ├── plan_adapter.py    # Plan standardization
│   └── image_analysis.py  # Exercise form analysis
├── core/                   # Core business logic
│   ├── database.py        # SQLAlchemy database management
│   ├── session_engine.py  # Session lifecycle management
│   ├── concurrency.py     # Thread pool executor
│   └── report_generator.py # Report generation
├── ui/                     # Gradio user interfaces
│   ├── home.py            # Dashboard
│   ├── assessment.py      # Patient assessment
│   ├── session.py         # Session management
│   ├── plan.py            # Treatment planning
│   ├── progress.py        # Progress tracking
│   └── report.py          # Report generation
├── security/              # Security layer
│   ├── sanitizer.py      # Input sanitization
│   └── validator.py      # Data validation
├── utils/                 # Utilities
│   ├── config.py         # Configuration management
│   └── logger.py         # Structured logging
└── models/               # Database models (to be defined)
```

## Installation

### Prerequisites

- Python 3.11+
- uv package manager

### Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment:**
   Edit `.env` file to customize settings:
   ```env
   MEDGEMMA_MODEL_NAME=google/medgemma-2b
   GRADIO_SERVER_PORT=7860
   DATABASE_URL=sqlite:///data/rehabflow.db
   ```

3. **Run the application:**
   ```bash
   uv run python app.py
   ```

## Usage

1. Navigate to `http://127.0.0.1:7860` in your browser
2. Start with the Assessment tab to evaluate a new patient
3. Generate AI-powered treatment plans in the Plans tab
4. Track sessions in real-time using the Sessions tab
5. Monitor progress and generate reports

## Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MEDGEMMA_MODEL_NAME` | `google/medgemma-2b` | MedGemma model identifier |
| `MEDGEMMA_DEVICE` | `cpu` | Device for model inference |
| `GRADIO_SERVER_PORT` | `7860` | Web interface port |
| `DATABASE_URL` | `sqlite:///data/rehabflow.db` | Database connection string |
| `MAX_WORKERS` | `4` | Thread pool size |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Development

### Code Structure

- **Modular Design**: Clean separation of concerns across modules
- **Type Hints**: Full type annotations for better IDE support
- **Logging**: Structured logging throughout the application
- **Thread Safety**: All database operations are thread-safe
- **Error Handling**: Comprehensive error handling and validation

### Adding New Features

1. Define models in `models/`
2. Add business logic in `core/`
3. Create UI components in `ui/`
4. Ensure security validation in `security/`

## Security

- Input sanitization on all user inputs
- Data validation against business rules
- Medical-grade error handling
- Secure database operations with SQLAlchemy

## Performance

- ThreadPoolExecutor for concurrent operations
- SQLite WAL mode for better concurrency
- Efficient database connection pooling
- Optimized model inference

## License

[Add your license here]

## Credits

Built with:
- [Gradio](https://gradio.app/) - UI framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Google MedGemma](https://huggingface.co/google/medgemma-2b) - Medical AI model
- [Transformers](https://huggingface.co/transformers) - Model inference

## Contact

[Add your contact information here]
