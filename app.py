from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ───── Get PIPELINE results ────────────────────────────────────────
#  detector = model_pipeline()


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sentiment API</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
 
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
  :root {
    --bg: #0d0d0d;
    --surface: #161616;
    --border: #2a2a2a;
    --text: #e8e8e8;
    --muted: #666;
    --accent: #c084fc;
    --neg: #ff4d6d;
    --neu: #f0c040;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
  }
 
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
 
  .wrap {
    width: 100%;
    max-width: 560px;
  }
 
  .label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
  }
 
  h1 {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 4px;
  }
 
  .sub {
    font-size: .85rem;
    color: var(--muted);
    margin-bottom: 32px;
    font-family: var(--mono);
  }
 
  textarea {
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
    color: var(--text);
    font-family: var(--sans);
    font-size: .9rem;
    resize: vertical;
    min-height: 110px;
    outline: none;
    transition: border-color .2s;
  }
  textarea:focus { border-color: #444; }
 
  button {
    margin-top: 12px;
    width: 100%;
    padding: 13px;
    background: var(--accent);
    color: #fff;
    font-family: var(--mono);
    font-size: .85rem;
    font-weight: 600;
    letter-spacing: .06em;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: opacity .15s;
  }
  button:hover { opacity: .85; }
  button:disabled { opacity: .4; cursor: not-allowed; }
 
  .result {
    margin-top: 24px;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    display: none;
  }
 
  .result-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }
 
  .badge {
    font-family: var(--mono);
    font-size: .78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .08em;
    padding: 3px 10px;
    border-radius: 20px;
    background: #1a1a1a;
  }
  .badge.positive { color: var(--accent); border: 1px solid var(--accent); }
  .badge.negative { color: var(--neg);    border: 1px solid var(--neg); }
  .badge.neutral  { color: var(--neu);    border: 1px solid var(--neu); }
 
  .conf {
    font-family: var(--mono);
    font-size: .8rem;
    color: var(--muted);
  }
 
  .bar-wrap {
    padding: 14px 16px;
  }
 
  .bar-track {
    height: 4px;
    background: #222;
    border-radius: 4px;
    overflow: hidden;
  }
 
  .bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width .5s ease;
  }
  .bar-fill.positive { background: var(--accent); }
  .bar-fill.negative { background: var(--neg); }
  .bar-fill.neutral  { background: var(--neu); }
 
  .json-block {
    padding: 14px 16px;
    border-top: 1px solid var(--border);
    background: #111;
  }
  pre {
    font-family: var(--mono);
    font-size: .78rem;
    color: #aaa;
    white-space: pre-wrap;
    word-break: break-all;
  }
 
  .err {
    margin-top: 14px;
    padding: 12px;
    border: 1px solid var(--neg);
    border-radius: 6px;
    font-family: var(--mono);
    font-size: .8rem;
    color: var(--neg);
    display: none;
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="label">Sentiment Analysis API</div>
  <h1>Text Sentiment</h1>
  <p class="sub">POST /predict → { sentiment, confidence }</p>
 
  <textarea id="txt" placeholder="Type or paste text here…"></textarea>
  <button id="btn" onclick="analyze()">Analyze</button>
  <div class="err" id="err"></div>
 
  <div class="result" id="res">
    <div class="result-header">
      <span class="badge" id="badge"></span>
      <span class="conf" id="conf"></span>
    </div>
    <div class="bar-wrap">
      <div class="bar-track"><div class="bar-fill" id="bar" style="width:0%"></div></div>
    </div>
    <div class="json-block"><pre id="json"></pre></div>
  </div>
</div>
 
<script>
async function analyze() {
  const text = document.getElementById('txt').value.trim();
  const btn  = document.getElementById('btn');
  const err  = document.getElementById('err');
  const res  = document.getElementById('res');
 
  err.style.display = 'none';
  res.style.display  = 'none';
 
  if (!text) { showErr('Please enter some text.'); return; }
 
  btn.disabled = true;
  btn.textContent = 'Analyzing…';
 
  try {
    const r = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'Server error');
 
    const s = (data.sentiment || '').toLowerCase();
    const c = data.confidence ?? 0;
 
    document.getElementById('badge').textContent = s;
    document.getElementById('badge').className   = 'badge ' + s;
    document.getElementById('conf').textContent  = (c * 100).toFixed(1) + '% confidence';
    document.getElementById('bar').style.width   = (c * 100) + '%';
    document.getElementById('bar').className     = 'bar-fill ' + s;
    document.getElementById('json').textContent  = JSON.stringify(data, null, 2);
 
    res.style.display = 'block';
  } catch(e) {
    showErr(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze';
  }
}
 
function showErr(msg) {
  const el = document.getElementById('err');
  el.textContent = msg;
  el.style.display = 'block';
}
 
document.getElementById('txt').addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.ctrlKey) analyze();
});
</script>
</body>
</html>
"""

# ── Routes ──────────────────────────────────────

@app.route('/')
def home():
    return render_template_string(HTML)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # ── Save results from Pipeline ──
    # sentiment, confidence = detector.analyze_sentiment(text) 

    # return jsonify({
    #     'sentiment':  str(sentiment),   # "positive" | "negative" | "neutral"
    #     'confidence': str(confidence)
    # })


    return jsonify({
        'sentiment':  "positive",
        'confidence': "0.95"
    })


# ── Run ─────────────────────────────────────────

app.run(host='0.0.0.0', port=5000, debug=True)