import requests
from flask import Flask, jsonify, render_template, request
from lxml import etree
from collections import Counter
import re

app = Flask(__name__)

analysis_result = None  # Store last analysis for "Get Latest Results"

# ----------------------------------
# 1. Fetch eCFR Data (XML)
# ----------------------------------

def fetch_ecfr_xml(date_str, title_num="1"):
    """
    Fetch a point-in-time version of a given title from eCFR's Versioner Service as XML.
    Example endpoint:
      GET /api/versioner/v1/full/{date}/title-{title}.xml
    """
    base_url = "https://www.ecfr.gov/api/versioner/v1/full"
    url = f"{base_url}/{date_str}/title-{title_num}.xml"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()  # Raise an HTTPError if the status is 4xx or 5xx
    return resp.text  # Raw XML string

def fetch_latest_snapshot_date(title_num="1"):
    """
    Queries the eCFR versions endpoint to find the most recent (latest) snapshot date for a given title.
    Example: GET /api/versioner/v1/versions/title-1.json
    Returns a string like '2025-02-08'.
    """
    url = f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title_num}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # Data is typically a list of objects, sorted oldest->newest or newest->oldest (depends on eCFR).
    # We'll assume the last element is the newest. If it's sorted oldest to newest, we pick data[-1].
    # If sorted newest to oldest, we pick data[0].
    if not data:
        raise ValueError("No version data found for this title.")
    # Inspect the data structure to pick the correct snapshot. 
    # If it's sorted newest first, do:
    latest_date = data[0]["date"]  # or data[-1]["date"] if reversed
    return latest_date

# ----------------------------------
# 2. Parse & Analyze (Word Count + Agencies + Top Words)
# ----------------------------------

def parse_ecfr_xml(xml_string):
    """
    Converts eCFR XML into a plain text string.
    """
    root = etree.fromstring(xml_string.encode("utf-8"))
    text_fragments = []
    for elem in root.iter():
        if elem.text:
            text_fragments.append(elem.text.strip())
    full_text = " ".join(text_fragments)
    return full_text

def analyze_ecfr_text(text):
    """
    Given plain text, return:
      - word_count
      - agency_counts
      - top_words (custom metric)
    """
    # 1. Word Count (naive)
    words = text.split()
    word_count = len(words)

    # 2. Agency references
    agencies_to_check = ["NCPC", "OMB", "OPM", "NARA", "CIO"]
    agency_counts = {}
    for agency in agencies_to_check:
        agency_counts[agency] = text.count(agency)

    # 3. Extract top words, ignoring minimal stopwords
    top_words = get_top_words(text, n=10)

    return {
        "word_count": word_count,
        "agencies": agency_counts,
        "top_words": top_words
    }

def get_top_words(text, n=10):
    """
    Return the top N most frequent words in the text, ignoring basic stopwords.
    This is a simple demonstration of a 'custom metric.'
    """
    # Lowercase
    text_lower = text.lower()
    # Remove non-alpha (optional) and split
    tokens = re.findall(r"[a-zA-Z]+", text_lower)

    # Minimal stopwords
    stopwords = set(["the","and","of","to","in","a","for","on","is","that","with","by","at","an","be","are","as","or","this"])
    
    filtered = [t for t in tokens if t not in stopwords and len(t) > 1]
    counts = Counter(filtered)
    # Return a list of (word, frequency) for top N
    return counts.most_common(n)

# Helper to do "full" analysis
def parse_and_analyze_ecfr_xml(xml_string):
    text = parse_ecfr_xml(xml_string)
    return analyze_ecfr_text(text)

# ----------------------------------
# 3. Compare Snapshots
# ----------------------------------

def compare_two_snapshots(snapshot_a, snapshot_b):
    """
    Compare two snapshots, returning a naive difference
    in word_count and agencies. (top_words not included in diff).
    """
    diff = {}
    diff["word_count_change"] = snapshot_b["analysis"]["word_count"] - snapshot_a["analysis"]["word_count"]

    agencies_diff = {}
    all_agencies = set(snapshot_a["analysis"]["agencies"].keys()) | set(snapshot_b["analysis"]["agencies"].keys())
    for agency in all_agencies:
        old_count = snapshot_a["analysis"]["agencies"].get(agency, 0)
        new_count = snapshot_b["analysis"]["agencies"].get(agency, 0)
        agencies_diff[agency] = new_count - old_count

    diff["agencies_diff"] = agencies_diff
    return diff

# ----------------------------------
# Flask Routes
# ----------------------------------

@app.route("/")
def home():
    """Serve a simple HTML front-end (see index.html)."""
    return render_template("index.html")

@app.route("/latest_analyze", methods=["GET"])
def latest_analyze():
    """
    Fetch the latest available snapshot for a given title, parse, analyze, and return JSON.
    Example usage: /latest_analyze?title=10
    """
    global analysis_result
    title_num = request.args.get("title", "1")
    try:
        latest_date = fetch_latest_snapshot_date(title_num)
        xml_data = fetch_ecfr_xml(latest_date, title_num)
        analysis_data = parse_and_analyze_ecfr_xml(xml_data)
        analysis_result = {
            "date": latest_date,
            "title": title_num,
            "analysis": analysis_data
        }
        return jsonify({"success": True, "analysisResult": analysis_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/analyze", methods=["GET"])
def analyze():
    """
    Fetch eCFR data by date/title from query params, parse and analyze it.
    Store the results in memory. Return JSON with the analysis.
    """
    global analysis_result

    date_str = request.args.get("date", "2025-01-01")
    title_num = request.args.get("title", "1")
    try:
        xml_data = fetch_ecfr_xml(date_str, title_num)
        analysis_data = parse_and_analyze_ecfr_xml(xml_data)
        analysis_result = {
            "date": date_str,
            "title": title_num,
            "analysis": analysis_data
        }
        return jsonify({"success": True, "analysisResult": analysis_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/results", methods=["GET"])
def results():
    """Return the last computed analysis result in JSON."""
    if analysis_result is None:
        return jsonify({"success": False, "message": "No results yet—please run /analyze or /latest_analyze"}), 404
    return jsonify({"success": True, "analysisResult": analysis_result})

@app.route("/compare", methods=["GET"])
def compare():
    """
    Naive 'historical comparison' between two different date snapshots for the same title.
    Usage: /compare?date1=2022-01-01&date2=2023-01-01&title=1
    """
    date1 = request.args.get("date1", "2022-01-01")
    date2 = request.args.get("date2", "2023-01-01")
    title_num = request.args.get("title", "1")

    try:
        # Snapshot A
        xml_a = fetch_ecfr_xml(date1, title_num)
        analysis_a = parse_and_analyze_ecfr_xml(xml_a)
        snapshot_a = {
            "date": date1,
            "title": title_num,
            "analysis": analysis_a
        }

        # Snapshot B
        xml_b = fetch_ecfr_xml(date2, title_num)
        analysis_b = parse_and_analyze_ecfr_xml(xml_b)
        snapshot_b = {
            "date": date2,
            "title": title_num,
            "analysis": analysis_b
        }

        # Compare
        diff_result = compare_two_snapshots(snapshot_a, snapshot_b)
        return jsonify({
            "success": True,
            "snapshotA": snapshot_a,
            "snapshotB": snapshot_b,
            "comparison": diff_result
        })
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route("/keyword_search", methods=["GET"])
def keyword_search():
    """
    3rd analyze feature: Return how many times each keyword appears in the eCFR text (case-insensitive).
    Usage: /keyword_search?date=2025-01-01&title=1&keywords=privacy,information,records
    """
    try:
        date_str = request.args.get("date", "2025-01-01")
        title_num = request.args.get("title", "1")
        keywords_param = request.args.get("keywords", "")
        
        # Split on commas, strip whitespace
        keywords_list = [k.strip() for k in keywords_param.split(",") if k.strip()]

        # Fetch and parse
        xml_data = fetch_ecfr_xml(date_str, title_num)
        text_data = parse_ecfr_xml(xml_data)  # Reuse our parse function
        text_lower = text_data.lower()

        frequencies = {}
        for kw in keywords_list:
            kw_lower = kw.lower()
            freq = text_lower.count(kw_lower)
            frequencies[kw] = freq

        result = {
            "success": True,
            "date": date_str,
            "title": title_num,
            "keywords": keywords_list,
            "frequencies": frequencies
        }
        return jsonify(result)
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

if __name__ == "__main__":
    app.run(debug=True)