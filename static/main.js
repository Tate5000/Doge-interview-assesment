"use strict";

// -------------------------------------
// Single Snapshot Analysis (By Date)
// -------------------------------------
async function triggerAnalysis() {
  const output = document.getElementById("analysisOutput");
  output.textContent = "Analyzing...";

  const dateStr = document.getElementById("analyzeDate").value.trim();
  const titleNum = document.getElementById("analyzeTitle").value.trim();

  try {
    const res = await fetch(`/analyze?date=${encodeURIComponent(dateStr)}&title=${encodeURIComponent(titleNum)}`, {
      method: "GET",
      headers: {
        Accept: "application/json"
      }
    });
    if (!res.ok) {
      const errText = await res.text();
      output.textContent = `Analysis failed (HTTP ${res.status}):\n${errText}`;
      return;
    }
    const data = await res.json();
    if (data.success) {
      output.textContent = "Analysis complete!\n" + JSON.stringify(data.analysisResult, null, 2);
      // Update chart + top words
      updateAgencyChart(data.analysisResult.analysis.agencies);
      showTopWords(data.analysisResult.analysis.top_words);
    } else {
      output.textContent = `Analysis failed:\n` + JSON.stringify(data, null, 2);
    }
  } catch (error) {
    output.textContent = "Error: " + error.message;
  }
}

// -------------------------------------
// Fetch Most Recent Analysis Result
// -------------------------------------
async function fetchResults() {
  const output = document.getElementById("analysisOutput");
  output.textContent = "Fetching latest analysis...";

  try {
    const res = await fetch("/results", {
      method: "GET",
      headers: {
        Accept: "application/json"
      }
    });
    if (!res.ok) {
      const errText = await res.text();
      output.textContent = `Fetch failed (HTTP ${res.status}):\n${errText}`;
      return;
    }
    const data = await res.json();
    if (data.success) {
      output.textContent = "Last analysis result:\n" + JSON.stringify(data.analysisResult, null, 2);
      // Update chart + top words
      updateAgencyChart(data.analysisResult.analysis.agencies);
      showTopWords(data.analysisResult.analysis.top_words);
    } else {
      output.textContent = `No results yet or error:\n` + JSON.stringify(data, null, 2);
    }
  } catch (error) {
    output.textContent = "Error: " + error.message;
  }
}

// -------------------------------------
// Compare Two Snapshots
// -------------------------------------
async function compareSnapshots() {
  const output = document.getElementById("compareOutput");
  output.textContent = "Comparing snapshots...";

  const date1 = document.getElementById("compareDate1").value.trim();
  const date2 = document.getElementById("compareDate2").value.trim();
  const titleNum = document.getElementById("compareTitle").value.trim();

  try {
    const res = await fetch(`/compare?date1=${encodeURIComponent(date1)}&date2=${encodeURIComponent(date2)}&title=${encodeURIComponent(titleNum)}`, {
      method: "GET",
      headers: {
        Accept: "application/json"
      }
    });
    if (!res.ok) {
      const errText = await res.text();
      output.textContent = `Compare failed (HTTP ${res.status}):\n${errText}`;
      return;
    }
    const data = await res.json();
    if (data.success) {
      output.textContent = `Comparison:\n` + JSON.stringify(data, null, 2);
    } else {
      output.textContent = `Compare error:\n` + JSON.stringify(data, null, 2);
    }
  } catch (error) {
    output.textContent = "Error: " + error.message;
  }
}

// -------------------------------------
// Keyword Search
// -------------------------------------
async function searchKeywords() {
  const output = document.getElementById("keywordOutput");
  output.textContent = "Searching...";

  const dateStr = document.getElementById("keywordDate").value.trim();
  const titleNum = document.getElementById("keywordTitle").value.trim();
  const keywordList = document.getElementById("keywordList").value.trim();

  try {
    const res = await fetch(`/keyword_search?date=${encodeURIComponent(dateStr)}&title=${encodeURIComponent(titleNum)}&keywords=${encodeURIComponent(keywordList)}`, {
      method: "GET",
      headers: { Accept: "application/json" }
    });
    if (!res.ok) {
      const errText = await res.text();
      output.textContent = `Search failed (HTTP ${res.status}):\n${errText}`;
      return;
    }
    const data = await res.json();
    if (data.success) {
      output.textContent = `Keyword frequencies:\n` + JSON.stringify(data, null, 2);
    } else {
      output.textContent = `Error:\n` + JSON.stringify(data, null, 2);
    }
  } catch (err) {
    output.textContent = "Network or parsing error: " + err.message;
  }
}

// -------------------------------------
// Fetch Latest eCFR Snapshot
// -------------------------------------
async function fetchLatestAnalysis() {
  const output = document.getElementById("latestOutput");
  output.textContent = "Fetching latest eCFR snapshot...";

  const titleNum = document.getElementById("latestTitle").value.trim();

  try {
    const res = await fetch(`/latest_analyze?title=${encodeURIComponent(titleNum)}`, {
      method: "GET",
      headers: {
        Accept: "application/json"
      }
    });
    if (!res.ok) {
      const errText = await res.text();
      output.textContent = `Latest analysis failed (HTTP ${res.status}):\n${errText}`;
      return;
    }
    const data = await res.json();
    if (data.success) {
      output.textContent = "Latest Analysis:\n" + JSON.stringify(data.analysisResult, null, 2);
      // Update chart + top words
      updateAgencyChart(data.analysisResult.analysis.agencies);
      showTopWords(data.analysisResult.analysis.top_words);
    } else {
      output.textContent = `Latest analysis failed:\n` + JSON.stringify(data, null, 2);
    }
  } catch (err) {
    output.textContent = "Error: " + err.message;
  }
}

// -------------------------------------
// Chart.js Bar Chart for Agency References
// -------------------------------------
let agencyChartRef = null;

function updateAgencyChart(agencies) {
  const ctx = document.getElementById("agencyChart").getContext("2d");
  if (agencyChartRef) {
    agencyChartRef.destroy();
  }
  const labels = Object.keys(agencies);
  const values = Object.values(agencies);

  agencyChartRef = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Agency References",
        data: values,
        backgroundColor: "rgba(54,162,235,0.5)"
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

// -------------------------------------
// Display "Top Words" in a <ul>
// -------------------------------------
function showTopWords(topWordsArray) {
  // topWordsArray looks like: [["privacy", 15], ["records", 10], ...]
  const listEl = document.getElementById("topWordsList");
  listEl.innerHTML = ""; // Clear old items

  topWordsArray.forEach(([word, freq]) => {
    const li = document.createElement("li");
    li.textContent = `${word} (${freq})`;
    listEl.appendChild(li);
  });
}