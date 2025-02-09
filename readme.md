# eCFR Analyzer

A robust Python Flask application for analyzing the Electronic Code of Federal Regulations (eCFR). This tool enables users to download, parse, and analyze eCFR content through an intuitive web interface.

## Features

- **Snapshot Analysis**: Extract and analyze specific versions of eCFR titles by date
  - Word count analysis
  - Agency mention tracking
  - Top word frequency analysis
  
- **Temporal Comparison**: Compare two versions of the same title across different dates
  - Track changes in word count
  - Monitor shifts in agency references
  
- **Latest Content Access**: Automatically fetch and analyze the most recent eCFR snapshot
- **Custom Keyword Analysis**: Search for and quantify specific terms within the regulations

## Getting Started

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/ecfr_analyzer.git
cd ecfr_analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Access the web interface:
```
http://127.0.0.1:5000
```

## Project Structure

```
ecfr_analyzer/
├── app.py              # Flask application core
├── requirements.txt    # Project dependencies
├── templates/
│   └── index.html     # Main web interface
└── static/
    └── main.js        # Frontend functionality
```

## API Endpoints

### Snapshot Analysis
```
GET /analyze
Parameters:
- date: YYYY-MM-DD
- title: 1-50
Returns: JSON with word_count, agencies, top_words
```

### Latest Snapshot
```
GET /latest_analyze
Parameters:
- title: 1-50
Returns: Analysis of most recent snapshot
```

### Snapshot Comparison
```
GET /compare
Parameters:
- date1: YYYY-MM-DD
- date2: YYYY-MM-DD
- title: 1-50
Returns: Difference analysis between snapshots
```

### Keyword Search
```
GET /keyword_search
Parameters:
- date: YYYY-MM-DD
- title: 1-50
- keywords: comma-separated list
Returns: Frequency count for each keyword
```

### Results Retrieval
```
GET /results
Returns: Most recent analysis results
```

## Web Interface Features

- **Interactive Analysis Tools**
  - Date and title selection
  - Snapshot comparison interface
  - Agency reference visualization
  - Top word frequency display

- **Data Visualization**
  - Agency reference bar charts (Chart.js)
  - Word frequency listings
  - Comparative analysis displays

## Technical Considerations

### Performance Notes
- Large titles (e.g., Title 40) may experience longer processing times
- API timeouts possible for extensive documents
- Memory usage scales with document size

### Analysis Limitations

- **Agency Detection**: Simple string matching approach
  - Does not parse official CFR structure
  - May include false positives
  
- **Content Availability**
  - Not all dates have available snapshots
  - API may return 404/503 for invalid dates
  
- **Text Analysis**
  - Basic stopword filtering
  - Case-insensitive matching
  - No advanced linguistic processing

