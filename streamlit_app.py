import streamlit as st
import re
import os
import json
import io
import zipfile
import time
import subprocess
from dateutil import parser
from datetime import datetime
import sourcemap 
import requests
import itertools

# CONFIG
st.set_page_config(
    page_title="Forensic Sentinel Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ULTRA-PREMIUM CUSTOM STYLING & FIXES
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Typography & Background */
    .stApp {
        background-color: var(--background-color);
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    h1, h2, h3, h4 { 
        font-family: 'Inter', sans-serif !important; 
        font-weight: 800 !important; 
        letter-spacing: -0.5px;
    }
    
    /* Sleek Sidebar Design */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        border-right: 1px solid rgba(128, 128, 128, 0.1);
        box-shadow: 4px 0 24px rgba(0,0,0,0.03);
    }
    [data-testid="stSidebar"] hr {
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        margin: 2em 0;
    }

    /* VISIBILITY FIX: Premium Text Inputs */
    .stTextInput input, .stNumberInput input {
        background-color: rgba(128, 128, 128, 0.05) !important;
        color: var(--text-color) !important; /* Ensures pasted path is always visible! */
        border: 1.5px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important;
        background-color: transparent !important;
    }

    /* Stunning Gradient Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
        color: #FFFFFF !important;
        border-radius: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        padding: 0.6rem 1.5rem;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
        filter: brightness(1.1);
    }
    div.stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
    }

    /* Elevated Metric Cards */
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.1);
        border-left: 5px solid #3B82F6;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    [data-testid="stMetricValue"] { 
        color: #3B82F6 !important; 
        font-weight: 900 !important; 
        font-size: 28px !important;
    }
    [data-testid="stMetricLabel"] { 
        color: var(--text-color) !important; 
        font-weight: 700 !important; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
        opacity: 0.7;
    }

    /* Premium Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: var(--secondary-background-color); 
        padding: 6px; 
        border-radius: 12px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }
    .stTabs [data-baseweb="tab"] { 
        color: var(--text-color); 
        font-weight: 600; 
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] { 
        background-color: var(--background-color) !important;
        color: #3B82F6 !important; 
        font-weight: 800;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* Soft Expander Styling */
    [data-testid="stExpander"] details summary {
        background-color: var(--secondary-background-color) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        padding: 12px 15px !important;
        transition: all 0.2s ease;
    }
    [data-testid="stExpander"] details summary:hover {
        background-color: rgba(128, 128, 128, 0.08) !important;
    }
    [data-testid="stExpander"] details summary p {
        font-weight: 700 !important;
        color: var(--text-color) !important;
    }

    /* Beautiful File Upload Dropzone */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(59, 130, 246, 0.03) !important;
        border: 2px dashed #3B82F6 !important;
        border-radius: 14px !important;
        padding: 2rem !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(59, 130, 246, 0.08) !important;
        border-color: #2563EB !important;
    }

    /* Enhanced Color-Coded Log Boxes */
    .log-box {
        padding: 1.2rem;
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
        font-size: 13.5px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 6px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        line-height: 1.5;
    }
    .log-crash { border-color: #EF4444; background: rgba(239, 68, 68, 0.05); }
    .log-error { border-color: #F97316; background: rgba(249, 115, 22, 0.05); }
    .log-warn  { border-color: #EAB308; background: rgba(234, 179, 8, 0.05); }
    .log-info  { border-color: #22C55E; background: rgba(34, 197, 94, 0.05); }
    .log-rpc   { border-color: #8B5CF6; background: rgba(139, 92, 246, 0.05); }
    .log-layer { border-color: #EC4899; background: rgba(236, 72, 153, 0.05); }
    
    /* Section Headers */
    .section-header {
        font-weight: 800;
        color: var(--text-color);
        margin-top: 15px;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 1px;
        border-bottom: 2px solid rgba(128, 128, 128, 0.1);
        padding-bottom: 6px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# CONSTANTS & REGEX
SCHEMA_DIR = "schemas"

CRASH_PAT       = re.compile(r"FATAL ERROR: Segmentation fault|Fatal error: Out of memory", re.I)
EMPTY_STACK_PAT = re.compile(r'(?:\\?["\'])?stack(?:\\?["\'])?\s*:\s*([^,\r\n]*)', re.I)

RPC_START_PAT   = re.compile(r"RPC_IN|RPC_START|RPC_REQUEST", re.I)
RPC_END_PAT     = re.compile(r"RPC_OUT|RPC_END|RPC_RESPONSE|RPC_RETURN|RPC_RESULT|RPC_REPLY", re.I)

ID_PAT   = re.compile(r"\b(?:cmdid)[=:\s]+(\d+)|\b(?:id|req_id|request_id|trace_id)[=:\s]+([\w-]+)|\bRPC\w{0,10}[\s]\b([\w\-]{4,})\b", re.I)
API_PAT  = re.compile(r"Plugin_Execute:\s*([\w\.]+)|(?:endpoint|api|url|path)[=_:\s]+([/\w\-\.\{\}\(\)]+)|(/[a-zA-Z][\w\-\./]+)", re.I)
TS_PAT   = re.compile(
    r"\b(\d{4}[-/]\d{2}[-/]\d{2}[T \t]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
    r"|(?:^|\[|\s)(\d{2}[-/]\d{2}[-/]\d{4}[T \t]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)"
    r"|(?:^|\[|\s)(\d{2}:\d{2}:\d{2}[.,]\d+)"
    r"|(?:^|\s)(\d{13,})\b"
)
STACK_CONTINUE_PAT = re.compile(r"^\s+(at\s+|anonymous|Call|stack|at\s*\(|-->|#\d+)", re.I)
ON_SHOW_PAT     = re.compile(r"\[onShow\]", re.I)

VERSION_PAT = re.compile(r"(TPN\d{2,}[A-Za-z0-9_.\-]+)|\b(R\.\d{1,3}\.[\d\.]+)\b|(?:Software|SW\s*ware|SW|UI|Build|Firmware)\s*(?:version|v)?\s*[:=]\s*([A-Za-z0-9_]+\.[\w\d\.\-]+)|(\b\d{3}\.\d{3}\.\d{3}\.\d{3}\b)", re.I)
JS_STACK_PAT = re.compile(r"([\w\.-]+\.js):(\d+):(\d+)", re.I)

# SESSION STATE initialization
for k, v in {
    "std_analysis_history": {},
    "json_analysis_history": {},
    "std_folder_history": [],
    "json_folder_history": [],
    "root_path": os.getcwd(),
    "current_path": os.getcwd(),
    "active_content": None,
    "active_name": "",
    "jump_line": 0,
    "json_config": None,
    "json_log_content": None,
    "json_log_name": "",
    "active_incidents": [],
    "js_map_cache": {},
    "manual_map_path": "",
    "selected_js_files": [],
    "window_layers": [],
    "rpc_delay_threshold": 1.0,
    "time_filter_start": "",
    "time_filter_end": "",
    "all_lines": [],
    "recursive_folder_target": "",
    "recursive_folder_requested": False,
    "last_build_time": 0,
    "current_detected_version": "Unknown",
    "processing_engine": "Local Memory (Small Files)"
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def load_local_source_maps(map_dir):
    # Auto-correct if the user pasted a direct file path instead of a directory
    if os.path.isfile(map_dir) and map_dir.lower().endswith('.map'):
        map_dir = os.path.dirname(map_dir)
        
    log_output = [f"Scanning directory: {map_dir}"]
    try:
        if not os.path.exists(map_dir) or not os.path.isdir(map_dir):
            return None, f"Error: Directory '{map_dir}' does not exist."
        
        maps = [f for f in os.listdir(map_dir) if f.endswith('.map')]
        if maps:
            log_output.append(f"SUCCESS: {len(maps)} source maps found.")
            for mname in maps:
                mpath = os.path.join(map_dir, mname)
                try:
                    with open(mpath, "r", encoding="utf-8-sig", errors="ignore") as mf:
                        content = mf.read()
                        js_name = mname.replace(".map", "")
                        sw_ver = st.session_state.get('current_detected_version', 'Unknown')
                        st.session_state.js_map_cache[f"{sw_ver}_{js_name}"] = content
                        st.session_state.js_map_cache[js_name] = content # Fallback without version tag
                except Exception as file_e:
                    log_output.append(f"Warning: Could not read {mname}: {str(file_e)}")
            return "\n".join(log_output), ""
        else:
            return None, f"Error: No .map files found in '{map_dir}'."
    except Exception as e:
        return None, str(e)

def set_jump_line(line_num):
    st.session_state.jump_line = line_num

def resolve_mapping(js_filename, gen_line, gen_col):
    js_base = os.path.basename(js_filename)
    sw_ver = st.session_state.get('current_detected_version', 'Unknown')
    
    cache_key = f"{sw_ver}_{js_base}"
    map_content = st.session_state.js_map_cache.get(cache_key)
    
    # Check fallback map cache without SW version
    if not map_content:
        map_content = st.session_state.js_map_cache.get(js_base)
    
    # Try finding the map in the specified manual map path
    if not map_content:
        local_dir = st.session_state.get("manual_map_path", "")
        local_map_path = os.path.join(local_dir, js_base + ".map")
        
        if not os.path.exists(local_map_path) and os.path.isdir(local_dir):
            potential_maps = [f for f in os.listdir(local_dir) if f.endswith(".map")]
            for pm in potential_maps:
                if js_base in pm:
                    local_map_path = os.path.join(local_dir, pm)
                    break

        if os.path.exists(local_map_path):
            try:
                with open(local_map_path, "r", encoding="utf-8-sig") as f:
                    map_content = f.read()
                    st.session_state.js_map_cache[cache_key] = map_content
                    st.session_state.js_map_cache[js_base] = map_content
            except: pass
    
    if not map_content:
        return {"error": f"❌ Map for {js_base} not found."}

    try:
        index = sourcemap.load(io.StringIO(map_content))
        g_line = int(gen_line)
        g_col = int(gen_col)
        
        if hasattr(index, 'index') and (g_line - 1) >= len(index.index):
             last_idx = len(index.index) - 1
             res = index.lookup(line=last_idx, column=0)
             if res:
                 return type('MappingResult', (), {
                    'source': getattr(res, 'src', 'unknown') + " (Approx)",
                    'line': getattr(res, 'src_line', 0) + 1,
                    'column': getattr(res, 'src_col', 0),
                    'name': "Boundary_Interpolated"
                 })
             return {"error": f"❌ Line {g_line} is outside the Source Map index."}

        res = index.lookup(line=g_line - 1, column=g_col)
        if not res:
            res = index.lookup(line=g_line - 1, column=0)
            if not res:
                return {"error": f"❌ No mapping found for line {gen_line}."}

        return type('MappingResult', (), {
            'source': getattr(res, 'src', 'unknown'),
            'line': getattr(res, 'src_line', 0) + 1, 
            'column': getattr(res, 'src_col', 0),
            'name': getattr(res, 'name', None)
        })
            
    except Exception as e:
        return {"error": f"Mapping Logic Error: {str(e)}"}

def file_browser_ui(key_suffix: str, is_recursive: bool = False):
    hist_key = "std_folder_history" if key_suffix == "std" else "json_folder_history"
    
    sources = ["Folder Path", "Manual File Browse"] if is_recursive else ["Manual File Browse", "Folder Path"]
    mode = st.selectbox("Input Mode", sources, key=f"mode_{key_suffix}")
    content, name, file_path, folder_target = None, "", None, None

    if mode == "Manual File Browse":
        if st.session_state.processing_engine == "FastAPI (Large file)":
            colA, colB = st.columns(2)
            with colA:
                if st.button("📂 Browse File (Instant)", key=f"tk_btn_{key_suffix}"):
                    import tkinter as tk
                    from tkinter import filedialog
                    try:
                        root = tk.Tk()
                        root.attributes("-topmost", True)
                        root.withdraw()
                        f_path = filedialog.askopenfilename(title="Select Massive Log File", filetypes=[("Log Files", "*.log;*.txt"), ("All Files", "*.*")])
                        root.destroy()
                        if f_path:
                            st.session_state[f"tk_path_{key_suffix}"] = f_path
                            st.toast(f"✅ Ready: {f_path}", icon="📂")
                    except Exception as e:
                        st.error(f"Error opening native browser: {e}")
            with colB:
                if is_recursive:
                    if st.button("📂 Browse Folder (Deep Scan)", key=f"tk_btn_dir_{key_suffix}"):
                        import tkinter as tk
                        from tkinter import filedialog
                        try:
                            root = tk.Tk()
                            root.attributes("-topmost", True)
                            root.withdraw()
                            d_path = filedialog.askdirectory(title="Select Folder for Deep Recursive Scan")
                            root.destroy()
                            if d_path:
                                st.session_state[f"tk_path_{key_suffix}"] = d_path
                                st.toast(f"✅ Folder Ready: {d_path}", icon="📂")
                        except Exception as e:
                            st.error(f"Error opening native folder browser: {e}")
                            
            if st.session_state.get(f"tk_path_{key_suffix}"):
                sel_path = st.session_state[f"tk_path_{key_suffix}"]
                if os.path.isdir(sel_path):
                    folder_target = sel_path
                else:
                    file_path = sel_path
                    
        else:
            uploaded = st.file_uploader("Upload Log(s) or ZIP File", type=['txt','log','zip'], accept_multiple_files=True, key=f"up_{key_suffix}")
            if uploaded:
                st.toast("Logs successfully uploaded!", icon="✅")
                if len(uploaded) == 1:
                    name = uploaded[0].name
                    content = uploaded[0].getvalue()
                    st.session_state.pop("memory_files", None)
                else:
                    st.session_state.memory_files = uploaded
                    st.session_state.pop("active_content", None)
    else: 
        if st.session_state[hist_key]:
            sel = st.selectbox("Recent Folders", ["-- recent --"] + st.session_state[hist_key][::-1], key=f"hist_{key_suffix}")
            if sel != "-- recent --":
                st.session_state.current_path = sel
                st.rerun()

        c_pick, c_path = st.columns([1, 4])
        with c_pick:
            st.write("") 
            if st.button("📂 Pick Folder", key=f"tk_dir_{key_suffix}", use_container_width=True):
                import tkinter as tk
                from tkinter import filedialog
                try:
                    root = tk.Tk()
                    root.attributes("-topmost", True)
                    root.withdraw()
                    d_path = filedialog.askdirectory(title="Select Folder")
                    root.destroy()
                    if d_path:
                        st.session_state.current_path = d_path
                        st.rerun()
                except Exception as e:
                    pass
        with c_path:
            path = st.text_input("Directory Path", st.session_state.current_path, key=f"path_{key_suffix}")

        c1, c2, c3 = st.columns([1,1,2])
        
        if c1.button("🏠 Home", key=f"home_{key_suffix}", use_container_width=True):
            st.session_state.current_path = st.session_state.root_path
            st.rerun()
        if c2.button("⬅ Back", key=f"back_{key_suffix}", use_container_width=True):
            st.session_state.current_path = os.path.dirname(st.session_state.current_path)
            st.rerun()
        if c3.button("↻ Sync", key=f"sync_{key_suffix}", use_container_width=True):
            st.session_state.current_path = path
            st.rerun()

        curr = st.session_state.current_path
        try:
            items = os.listdir(curr)
            folders = sorted(f for f in items if os.path.isdir(os.path.join(curr,f)))
            files   = sorted(f for f in items if f.lower().endswith(('.log','.txt')))
            
            if folders:
                sub = st.selectbox("Subfolders", ["-- Browse --"] + folders, key=f"sub_{key_suffix}")
                if sub != "-- Browse --":
                    st.session_state.current_path = os.path.join(curr, sub)
                    st.rerun()
            
            if is_recursive:
                folder_target = curr
            else:
                if files:
                    fsel = st.selectbox("Log files", ["-- Select --"] + files, key=f"file_{key_suffix}")
                    if fsel != "-- Select --":
                        name = fsel
                        file_path = os.path.join(curr, fsel)
                        if st.session_state.processing_engine == "Local Memory (Small Files)":
                            with open(file_path, "rb") as fp: content = fp.read()
                        if curr not in st.session_state[hist_key]: st.session_state[hist_key].append(curr)
                        st.toast(f"Selected: {name}", icon="📄")
        except Exception as e: st.error(f"Directory error: {e}")
        
    return content, name, file_path, folder_target

def analyze_folder_recursive(folder_path: str, config=None):
    if not folder_path or not os.path.isdir(folder_path):
        st.error("Invalid recursive folder path.")
        return [], {"Crashes": 0, "RPC Delays": 0, "Unreturned RPCs": 0, "Uncaught Errors": 0, "Empty Stack": 0, "Window Layers": 0}, [], "Unknown", []

    files = []
    for root, _, names in os.walk(folder_path):
        for n in names:
            if n.lower().endswith((".log", ".txt")):
                files.append(os.path.join(root, n))

    files = sorted(files)
    if not files:
        st.warning("No .log or .txt files found anywhere in this folder structure.")
        return [], {"Crashes": 0, "RPC Delays": 0, "Unreturned RPCs": 0, "Uncaught Errors": 0, "Empty Stack": 0, "Window Layers": 0}, [], "Unknown", []

    overall_stats = {"Crashes": 0, "RPC Delays": 0, "Unreturned RPCs": 0, "Uncaught Errors": 0, "Empty Stack": 0, "Window Layers": 0}
    if config: overall_stats["Sequence Issues"] = 0
    all_incidents = []
    all_lines = []
    all_window_layers = []
    version_candidates = []
    line_offset = 0

    progress = st.progress(0, text=f"Deep Recursive scan: 0/{len(files)} files")
    for idx, fp in enumerate(files, start=1):
        if st.session_state.processing_engine == "FastAPI (Large file)":
            fastapi_url = st.session_state.get("fastapi_url", "http://localhost:8000")
            try:
                payload = {"file_path": fp, "rpc_delay_threshold": float(st.session_state.rpc_delay_threshold), "config": config}
                response = requests.post(f"{fastapi_url}/analyze_large_file", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    incs = data["incs"]
                    stats = data["stats"]
                    lines = [] 
                    ver = data["version"]
                    window_layers = data["window_layers"]
                else: continue
            except Exception: continue
        else:
            try:
                with open(fp, "rb") as f: raw = f.read()
            except Exception: continue
            incs, stats, lines, ver, window_layers = analyze_log_turbo(raw, config)

        if ver and ver != "Unknown": version_candidates.append(ver)
        rel_file = os.path.relpath(fp, folder_path)

        for inc in incs:
            patched = dict(inc)
            original_line = int(inc.get("line", 0))
            patched["line"] = line_offset + original_line
            patched["text"] = f"[File: {rel_file} | Line: {original_line}]\n{inc.get('text', '')}"
            all_incidents.append(patched)
            if patched["cat"] in overall_stats:
                overall_stats[patched["cat"]] += 1

        for wl in window_layers:
            all_window_layers.append({
                "line": line_offset + int(wl.get("line", 0)),
                "content": f"[File: {rel_file}] {wl.get('content', '')}",
                "timestamp": wl.get("timestamp")
            })

        if st.session_state.processing_engine != "FastAPI (Large file)":
            all_lines.extend([f"[{rel_file}] {ln}" for ln in lines])
            line_offset += len(lines)
            
        progress.progress(idx / len(files), text=f"Deep Recursive scan: {idx}/{len(files)} files")

    progress.empty()
    resolved_version = version_candidates[0] if version_candidates else "Unknown"
    st.session_state.current_detected_version = resolved_version
    st.toast("Deep Recursive Scan Complete!", icon="🔎")
    return all_incidents, overall_stats, all_lines, resolved_version, all_window_layers

def analyze_memory_files_recursive(uploaded_files, config=None):
    overall_stats = {"Crashes": 0, "RPC Delays": 0, "Unreturned RPCs": 0, "Uncaught Errors": 0, "Empty Stack": 0, "Window Layers": 0}
    if config: overall_stats["Sequence Issues"] = 0
    all_incidents = []
    all_lines = []
    all_window_layers = []
    version_candidates = []
    line_offset = 0

    expanded_files = []
    for uf in uploaded_files:
        if uf.name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(uf.getvalue())) as z:
                    for zinfo in z.infolist():
                        if zinfo.is_dir() or not zinfo.filename.lower().endswith((".log", ".txt")):
                            continue
                        with z.open(zinfo) as zf:
                            content = zf.read()
                            mock_file = io.BytesIO(content)
                            mock_file.name = f"{uf.name}/{zinfo.filename}"
                            expanded_files.append(mock_file)
            except Exception as e:
                st.error(f"Error extracting {uf.name}: {e}")
        else:
            expanded_files.append(uf)

    if not expanded_files:
        return [], overall_stats, [], "Unknown", []

    progress = st.progress(0, text=f"Analyzing: 0/{len(expanded_files)} files")
    for idx, uf in enumerate(expanded_files, start=1):
        raw = uf.getvalue() if hasattr(uf, "getvalue") else uf.read()
        incs, stats, lines, ver, window_layers = analyze_log_turbo(raw, config)
        if ver and ver != "Unknown": version_candidates.append(ver)

        rel_file = uf.name

        for inc in incs:
            patched = dict(inc)
            original_line = int(inc.get("line", 0))
            patched["line"] = line_offset + original_line
            patched["text"] = f"[File: {rel_file} | File line: {original_line}]\n{inc.get('text', '')}"
            all_incidents.append(patched)
            
            if patched["cat"] in overall_stats:
                overall_stats[patched["cat"]] += 1

        for wl in window_layers:
            all_window_layers.append({
                "line": line_offset + int(wl.get("line", 0)),
                "content": f"[File: {rel_file}] {wl.get('content', '')}",
                "timestamp": wl.get("timestamp")
            })

        all_lines.extend([f"[{rel_file}] {ln}" for ln in lines])
        line_offset += len(lines)
        progress.progress(idx / len(uploaded_files), text=f"Analyzing: {idx}/{len(uploaded_files)} files")

    progress.empty()
    st.toast("Memory Files Analyzed!", icon="🧠")
    resolved_version = version_candidates[0] if version_candidates else "Unknown"
    return all_incidents, overall_stats, all_lines, resolved_version, all_window_layers

def analyze_log_turbo(file_contents: bytes, config=None):
    if not file_contents: return [], {}, [], [], []
    f = io.TextIOWrapper(io.BytesIO(file_contents), encoding="utf-8", errors="ignore")
    
    is_json = isinstance(config, dict)
    mod_name   = config.get("moduleName") if is_json else None
    ts_filter   = config.get("timestamp")  if is_json else None
    max_latency = st.session_state.rpc_delay_threshold
    seq_rules   = config.get("logSequence", []) if is_json else []
    custom_v_pat = config.get("versionPattern") if is_json else None
    
    v_compiled = VERSION_PAT
    if custom_v_pat:
        try: v_compiled = re.compile(custom_v_pat, re.I)
        except: pass

    stats = {"Crashes": 0, "RPC Delays": 0, "Unreturned RPCs": 0, "Uncaught Errors": 0, "Empty Stack": 0, "Window Layers": 0}
    if is_json: stats["Sequence Issues"] = 0

    incidents, active_req = [], {}
    last_onshow = "Not found"
    last_onshow_line = None
    extracted_version = "Unknown"
    
    seq_parsed = []
    for rule in seq_rules:
        if isinstance(rule, list):
            steps = [str(s).strip() for s in rule if str(s).strip()]
            if steps: seq_parsed.append({"steps": steps, "type": "STRICT"})
        elif isinstance(rule, dict):
            pattern = rule.get("pattern", "")
            if pattern: seq_parsed.append({"pattern": pattern, "name": rule.get("name"), "type": "MATCH"})
    
    active_seq_trackers = {} 
    
    window_layers = []
    lines = []
    
    progress_bar = st.progress(0, text="Analyzing...")
    file_size = len(file_contents)
    bytes_read = 0
    
    raw_lines = f.readlines()

    for i, line in enumerate(raw_lines):
        bytes_read += len(line.encode("utf-8"))
        if i % 10000 == 0:
            progress = min(bytes_read / file_size, 1.0)
            progress_bar.progress(progress, text=f"Analyzing... ({int(progress*100)}%)")
        
        lines.append(line)
        ln = i + 1 
        llow = line.lower()
        
        # Unconstrained Version String check - Grabs longest valid string with dots
        v_match = v_compiled.search(line)
        if v_match:
            for group_val in v_match.groups():
                if group_val:
                    val = group_val.strip()
                    if "." in val and (len(val) >= 11 or val.lower().startswith("r.")):
                        if extracted_version == "Unknown" or len(val) > len(extracted_version):
                            extracted_version = val
                            st.session_state.current_detected_version = extracted_version
        
        if is_json and seq_parsed:
            for s_idx, seq_obj in enumerate(seq_parsed):
                if seq_obj["type"] == "STRICT":
                    seq = seq_obj["steps"]
                    if re.search(re.escape(seq[0]), line, re.I):
                        if s_idx in active_seq_trackers:
                            prev_tracker = active_seq_trackers[s_idx]
                            incidents.append({
                                "cat": "Sequence Issues", "type": "SEQ_BREAK", "line": prev_tracker['start_line'],
                                "text": f"Sequence #{s_idx+1} Failed: '{seq[prev_tracker['next_idx']]}' was never found (Restarted at line {ln})."
                            })
                            stats["Sequence Issues"] += 1
                        active_seq_trackers[s_idx] = {'next_idx': 1, 'start_line': ln}
                        if len(seq) == 1: del active_seq_trackers[s_idx]
                    elif s_idx in active_seq_trackers:
                        tracker = active_seq_trackers[s_idx]
                        if re.search(re.escape(seq[tracker['next_idx']]), line, re.I):
                            tracker['next_idx'] += 1
                            if tracker['next_idx'] >= len(seq): del active_seq_trackers[s_idx]
                else: 
                    if re.search(seq_obj["pattern"], line, re.I):
                        stats["Sequence Issues"] += 1
                        incidents.append({"cat": "Sequence Issues", "type": "SEQ", "line": ln, "text": f"Step matched: {seq_obj.get('name')}\nLine: {line.strip()}"})

        if "[onshow]" in llow:
            last_onshow = line.strip()
            last_onshow_line = ln
            layer_info = [line.strip()]
            lookahead = 1
            while i + lookahead < len(raw_lines):
                next_line = raw_lines[i + lookahead].strip()
                if not next_line: lookahead += 1; continue
                if next_line.lower().startswith("window layer"):
                    layer_info.append(next_line)
                    lookahead += 1
                else: break
            combined_content = "\n".join(layer_info)
            wl_item = {"line": ln, "content": combined_content, "timestamp": None}
            ts_m = TS_PAT.search(line)
            if ts_m:
                raw_ts = next((g.strip() for g in ts_m.groups() if g), None)
                if raw_ts: wl_item["timestamp"] = raw_ts
            window_layers.append(wl_item)
            stats["Window Layers"] += 1
            incidents.append({"cat": "Window Layers", "type": "LAYER_STATE", "line": ln, "text": combined_content})

        if "fatal" in llow:
            if CRASH_PAT.search(line):
                incidents.append({"cat":"Crashes", "type":"CRASH", "line":ln, "text":line})
                stats["Crashes"] += 1

        if "uncaught" in llow:
            stats["Uncaught Errors"] += 1
            unified_stack = []
            stack_mappings = [] 
            
            m_curr = JS_STACK_PAT.search(line)
            if m_curr:
                stack_mappings.append({"file": m_curr.group(1), "line": m_curr.group(2), "col": m_curr.group(3), "label": "Main Trace", "original_full": line.strip()})

            search_limit = max(0, i - 100)
            temp_stack = []
            for j in range(i - 1, search_limit, -1):
                prev_line = raw_lines[j].strip()
                if not prev_line: continue
                temp_stack.insert(0, prev_line)
                if "call stack:" in prev_line.lower():
                    unified_stack = temp_stack
                    for k in range(j + 1, min(j + 50, i)): 
                        m_frame = JS_STACK_PAT.search(raw_lines[k])
                        if m_frame:
                            if len(stack_mappings) < 5: 
                                stack_mappings.append({"file": m_frame.group(1), "line": m_frame.group(2), "col": m_frame.group(3), "label": f"Frame {len(stack_mappings)}", "original_full": raw_lines[k].strip()})
                    break
                if "[onshow]" in prev_line.lower() or "uncaught" in prev_line.lower(): break
            
            unified_stack.append(line.strip())
            incidents.append({
                "cat": "Uncaught Errors", "type": "UNCAUGHT", "line": ln, "text": "\n".join(unified_stack),
                "onshow": last_onshow, "stack_mappings": stack_mappings,
                "window_index": len(window_layers) - 1 if window_layers else None,
                "window_layer_text": f"Line {last_onshow_line}: {last_onshow}" if last_onshow_line else "Not Found"
            })

        if "stack" in llow and ":" in line:
            m = EMPTY_STACK_PAT.search(line)
            if m:
                content_val = (m.group(1) or "").strip().lower()
                cleaned = re.sub(r'[\"\'\s,\[\]\\]', '', content_val)
                if cleaned in {"", "null", "none", "n/a", "0", "undefined", "[]", "{}"}:
                    incidents.append({
                        "cat": "Empty Stack", "type": "NULL_STACK", "line": ln, "text": line, 
                        "onshow": last_onshow, "window_layer_text": f"Line {last_onshow_line}: {last_onshow}" if last_onshow_line else "Not Found"
                    })
                    stats["Empty Stack"] += 1

        if "rpc" in llow:
            rids = []
            for match in ID_PAT.finditer(line):
                g_val = next((g for g in match.groups() if g), None)
                if g_val and g_val not in rids:
                    rids.append(g_val)
                    
            if rids:
                ts_m = TS_PAT.search(line)
                raw_ts = next((g.strip() for g in ts_m.groups() if g), None) if ts_m else None
                
                if RPC_START_PAT.search(line):
                    api_m = API_PAT.search(line)
                    api = next((g for g in api_m.groups() if g), "unknown")
                    active_req[rids[0]] = {"ts": raw_ts, "line": ln, "api": api}
                elif RPC_END_PAT.search(line):
                    popped_rid = None
                    for r in rids:
                        if r in active_req:
                            popped_rid = r
                            break
                    if popped_rid:
                        s = active_req.pop(popped_rid)
                        dur = None
                        if raw_ts and s["ts"]:
                            try:
                                if raw_ts.isdigit(): dur = abs((int(raw_ts) - int(s["ts"])) / 1000.0)
                                else: dur = abs((parser.parse(raw_ts) - parser.parse(s["ts"])).total_seconds())
                            except: dur = None
                        if dur is not None and dur >= max_latency:
                            incidents.append({"cat": "RPC Delays", "type": "SLOW", "line": ln, "text": f"ID: {popped_rid} API: {s['api']}\nDuration: {dur:.2f} s"})
                            stats["RPC Delays"] += 1

    for s_idx, tracker in active_seq_trackers.items():
        incidents.append({
            "cat": "Sequence Issues", "type": "INCOMPLETE", "line": tracker['start_line'],
            "text": f"Sequence #{s_idx+1} Incomplete: File ended before next step was found."
        })
        stats["Sequence Issues"] += 1

    for rid, data in active_req.items():
        incidents.append({"cat": "Unreturned RPCs", "type": "HANG", "line": data["line"], "text": f"ID: {rid} API: {data['api']}"})
        stats["Unreturned RPCs"] += 1

    progress_bar.empty()
    filtered = [inc for inc in incidents if (not mod_name or mod_name.lower() in lines[inc["line"]-1].lower())]
    
    for k in stats.keys(): stats[k] = 0
    for inc in filtered:
        if inc["cat"] in stats:
            stats[inc["cat"]] += 1
            
    return filtered, stats, lines, extracted_version, window_layers

def render_analysis(incs, stats, lines, version="Unknown", window_layers=None):
    if window_layers is None: window_layers = []
    st.markdown(f"### Software Version: <span style='color:#2563EB;'>{version}</span>", unsafe_allow_html=True)

    with st.expander("⚙️ Analysis Configuration", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_threshold = st.number_input("RPC Delay Threshold (s)", min_value=0.1, max_value=60.0, value=float(st.session_state.rpc_delay_threshold))
            if new_threshold != st.session_state.rpc_delay_threshold:
                st.session_state.rpc_delay_threshold = new_threshold
                st.rerun()
        with col2:
            t_start = st.text_input("Start Time Filter", value=st.session_state.time_filter_start, placeholder="Feb 23 08:30")
            if t_start != st.session_state.time_filter_start:
                st.session_state.time_filter_start = t_start
                st.rerun()
        with col3:
            t_end = st.text_input("End Time Filter", value=st.session_state.time_filter_end, placeholder="Feb 24 08:30")
            if t_end != st.session_state.time_filter_end:
                st.session_state.time_filter_end = t_end
                st.rerun()
        
        if st.session_state.time_filter_start or st.session_state.time_filter_end:
            if st.button("Clear Time Filters"):
                st.session_state.time_filter_start = ""
                st.session_state.time_filter_end = ""
                st.rerun()

    # --- SMART TIME FILTER LOGIC ---
    active_incs = incs
    active_stats = stats.copy()
    
    start_str = st.session_state.time_filter_start.strip() if st.session_state.time_filter_start else ""
    end_str = st.session_state.time_filter_end.strip() if st.session_state.time_filter_end else ""
    
    if start_str or end_str:
        active_incs = []
        for k in active_stats.keys(): active_stats[k] = 0
        last_dt = datetime.now() 
        sorted_incs = sorted(incs, key=lambda x: x.get("line", 0))
        
        for inc in sorted_incs:
            raw_text = (lines[inc["line"]-1] if (lines and 0 < inc["line"] <= len(lines)) else "") + " " + (inc.get("raw_line") or inc.get("text", ""))
                  
            m = TS_PAT.search(raw_text)
            inc_dt = None
            if m:
                raw_ts = next((g.strip() for g in m.groups() if g), None)
                if raw_ts:
                    if raw_ts.isdigit() and len(raw_ts) > 10:
                        try: inc_dt = datetime.fromtimestamp(int(raw_ts)/1000.0)
                        except: pass
                    else:
                        try: inc_dt = parser.parse(raw_ts, fuzzy=True)
                        except: pass
            
            if inc_dt: last_dt = inc_dt
            else: inc_dt = last_dt 
                
            keep = True
            if start_str:
                try:
                    s_dt = parser.parse(start_str, default=inc_dt, fuzzy=True)
                    if inc_dt < s_dt: keep = False
                except: pass
            if end_str:
                try:
                    e_dt = parser.parse(end_str, default=inc_dt, fuzzy=True)
                    if inc_dt > e_dt: keep = False
                except: pass
                
            if keep:
                active_incs.append(inc)
                if inc["cat"] in active_stats:
                    active_stats[inc["cat"]] += 1
    
    cols = st.columns(len(active_stats))
    for i, (k,v) in enumerate(active_stats.items()): cols[i].metric(k,v)
    st.divider()
    
    q = st.text_input("Jump to line / Filter", placeholder="line or keyword", key="jump_input")
    if st.button("Apply Jump"):
        if q.isdigit(): 
            set_jump_line(int(q))
            st.rerun()

    cat_to_css = {
        "Crashes": "log-crash", "Uncaught Errors": "log-error", "Empty Stack": "log-warn", 
        "RPC Delays": "log-rpc", "Unreturned RPCs": "log-rpc", "Sequence Issues": "log-info", "Window Layers": "log-layer"
    }
    filter_options = ["All"] + list(active_stats.keys())
    if window_layers:
        if "Window Layers" not in filter_options:
            filter_options.append("Window Layers")
    
    selected_cat = st.selectbox("Select Category", filter_options, key="category_filter")

    def render_incidents(category, group, prefix="main"):
        max_display = 200
        total_items = len(group)
        if total_items > max_display:
            st.warning(f"⚠️ Displaying top {max_display} out of {total_items} items to ensure fast browser performance.")
            group_to_display = group[:max_display]
        else:
            group_to_display = group

        if category == "Window Layers":
            if not group_to_display:
                st.success("No window layers found.")
                return
            for idx, wl in enumerate(group_to_display):
                with st.expander(f"Layer Line {wl['line']} (Event {idx+1})"):
                    st.markdown(f"<div class='log-box log-layer'>{wl['text']}</div>", unsafe_allow_html=True)
                    st.button("→ Jump", key=f"j_wl_{prefix}_{idx}", on_click=set_jump_line, args=(wl['line'],))
            return

        if not group_to_display: 
            st.success("No issues found.")
            return
        for idx, it in enumerate(group_to_display):
            with st.expander(f"Line {it['line']} (Item {idx+1})"):
                if category == "Uncaught Errors":
                    st.markdown('<div class="section-header">Last [onShow] Event</div>', unsafe_allow_html=True)
                    st.code(it.get("onshow", "Not found"), language="text")
                    
                    st.markdown('<div class="section-header">Unified Call Stack & Uncaught Error</div>', unsafe_allow_html=True)
                    st.markdown(f"<div class='log-box log-error'>{it['text']}</div>", unsafe_allow_html=True)
                    
                    st.markdown('<div class="section-header">Decoded Line Mappings</div>', unsafe_allow_html=True)
                    mappings = it.get("stack_mappings", [])
                    if mappings:
                        data_for_table = []
                        for sm_idx, sm in enumerate(mappings):
                            if sm_idx >= 5: break
                            orig = resolve_mapping(sm["file"], sm["line"], sm["col"])
                            original_log = sm.get("original_full", "")
                            
                            mapped_str = ""
                            if orig and not isinstance(orig, dict):
                                mapped_str = f"{orig.source}:{orig.line}:{orig.column}"
                            else:
                                mapped_str = f"Error: {orig.get('error')}" if isinstance(orig, dict) else "Unknown"
                            
                            data_for_table.append({
                                "Log Frame Source": original_log,
                                "Mapped Source Location": mapped_str
                            })
                        
                        st.table(data_for_table)
                    else:
                        st.warning("No JS frames detected for mapping.")
                else:
                    st.markdown(f"<div class='log-box {cat_to_css.get(category, 'log-info')}'>{it['text']}</div>", unsafe_allow_html=True)

                st.button("→ Jump", key=f"j_{prefix}_{category}_{it['line']}_{idx}", on_click=set_jump_line, args=(it['line'],))

    if selected_cat == "All":
        all_tabs = [k for k in active_stats.keys() if active_stats[k] > 0]
        if window_layers and "Window Layers" not in all_tabs:
            all_tabs.append("Window Layers")
        
        if not all_tabs:
            st.info("No logs to display.")
        else:
            tabs = st.tabs([f"{k}" for k in all_tabs])
            for i, cat in enumerate(all_tabs):
                with tabs[i]: 
                    render_incidents(cat, [it for it in active_incs if it["cat"] == cat], prefix=f"tab_{i}")
    else: 
        render_incidents(selected_cat, [it for it in active_incs if it["cat"] == selected_cat], prefix="single")
    
    st.subheader("Log Viewer")
    if lines:
        jump = st.session_state.jump_line
        start, end = max(0, jump-150), min(len(lines), jump+350)
        if jump == 0: end = min(len(lines), 200)
        
        html_lines = []
        for idx in range(start, end):
            ln = idx + 1
            cls = "log-line jump-target" if (ln == jump) else "log-line"
            raw_text = lines[idx].replace("<","&lt;").replace(">","&gt;")
            html_lines.append(f'<div id="L{ln}" class="{cls}"><span class="line-number">{ln}</span><span class="log-content">{raw_text}</span></div>')
        
        # LOG VIEWER FIX: Added @media dark theme query directly into the iframe so the custom logs auto-invert!
        st.components.v1.html(f"""
            <style>
            body {{ margin: 0; padding: 0; background: #F8FAFC; color: #1E293B; }}
            .log-viewer-container {{
                font-family: 'Courier New', monospace;
                font-size: 13.5px;
            }}
            .log-line {{
                display: flex;
                align-items: flex-start;
                padding: 4px 8px;
                border-bottom: 1px solid #E2E8F0;
            }}
            .line-number {{
                color: #94A3B8;
                padding-right: 12px;
                font-weight: bold;
                border-right: 1px solid #E2E8F0;
                margin-right: 12px;
                min-width: 60px;
                flex-shrink: 0;
                text-align: right;
                user-select: none;
            }}
            .log-content {{
                white-space: pre-wrap;
                word-break: break-word;
                color: #1E293B !important;
                width: 100%;
            }}
            .jump-target {{
                background-color: #FEF08A !important;
                border-left: 6px solid #EAB308 !important;
            }}
            .jump-target .log-content {{
                color: #854D0E !important;
                font-weight: bold;
            }}
            
            ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            ::-webkit-scrollbar-track {{ background: #F8FAFC; }}
            ::-webkit-scrollbar-thumb {{ background: #CBD5E1; border-radius: 4px; }}
            ::-webkit-scrollbar-thumb:hover {{ background: #94A3B8; }}

            /* THIS HANDLES THE DARK THEME LOGIC FOR THE IFRAME */
            @media (prefers-color-scheme: dark) {{
                body {{ background: #0E1117; color: #FAFAFA; }}
                .log-line {{ border-bottom: 1px solid #262730; }}
                .line-number {{ color: #6b7280; border-right: 1px solid #262730; }}
                .log-content {{ color: #FAFAFA !important; }}
                .jump-target {{ background-color: #422006 !important; border-left: 6px solid #EAB308 !important; }}
                .jump-target .log-content {{ color: #FDE047 !important; font-weight: bold; }}
                ::-webkit-scrollbar-track {{ background: #0E1117; }}
                ::-webkit-scrollbar-thumb {{ background: #4B5563; }}
                ::-webkit-scrollbar-thumb:hover {{ background: #6B7280; }}
                #scroll-container {{ border: 1px solid #262730 !important; }}
            }}
            </style>
            <div id="scroll-container" class="log-viewer-container" style="height:600px; overflow:auto; border:1px solid #CBD5E1; border-radius: 8px;">
                {"".join(html_lines)}
            </div>
            <script>
                var element = document.getElementById("L{jump}");
                if (element) {{
                    element.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            </script>
        """, height=620)
    else:
        st.info("No logs loaded for viewer. Note: Deep Recursive mode disables log viewer memory to protect RAM.")

# --- SIDEBAR (3 TOP LEVEL MODES) ---
with st.sidebar:
    st.title("🛡️ Forensic Sentinel")

    with st.expander("🗺️ Local Source Map Sync", expanded=True):
        manual_path = st.text_input(
            "Local Map Directory Path", 
            value=r"C:\path\to\your\source_maps",
            key="manual_path"
        )
        st.session_state.manual_map_path = manual_path

        if st.button("🚀 Sync Source Maps", key="btn_sync_maps"):
            if manual_path:
                with st.spinner("Loading local Source Maps..."):
                    out, err = load_local_source_maps(manual_path)
                    if out:
                        st.toast("Maps Synced Successfully!", icon="✅")
                        st.success("Maps Synced!")
                        with st.expander("Details"): st.text(out)
                    else: st.error(f"Execution Error: {err}")
            else: st.warning("Provide a valid directory path.")

    st.divider()
    
    app_mode = st.radio("Operating Mode", ["Standard Analysis", "JSON Analysis", "Recursive Analysis"])
    
    st.divider()
    st.markdown("### ⚙️ Processing Engine")
    processing_engine = st.radio("Engine Select", ["Local Memory (Small Files)", "FastAPI (Large file)"])
    st.session_state.processing_engine = processing_engine
    
    if processing_engine == "FastAPI (Large file)":
        fastapi_url = st.text_input("FastAPI Server URL", "http://localhost:8000")
        st.session_state.fastapi_url = fastapi_url
    st.divider()

    # --- UI ROUTING DEPENDING ON MODE ---
    if app_mode == "Standard Analysis":
        cont, nam, f_path, _ = file_browser_ui("std", is_recursive=False)
        if f_path and processing_engine == "FastAPI (Large file)":
            st.session_state.fastapi_target_file = f_path
            st.session_state.active_content = None
        elif cont: 
            st.session_state.active_content, st.session_state.active_name = cont, nam
            st.session_state.fastapi_target_file = None
            
        if st.session_state.get("memory_files"):
            if st.button("Process Multiple Uploads"): pass

    elif app_mode == "JSON Analysis":
        schema_source = st.radio("Schema Source", ["Folder", "Upload"], horizontal=True)
        if schema_source == "Folder":
            jfiles = [f for f in os.listdir(SCHEMA_DIR) if f.endswith(".json")] if os.path.exists(SCHEMA_DIR) else []
            sel = st.selectbox("Select schema", ["choose"] + sorted(jfiles))
            if sel != "choose":
                with open(os.path.join(SCHEMA_DIR, sel)) as f: st.session_state.json_config = json.load(f)
        else:
            up_schema = st.file_uploader("Upload Schema JSON", type=["json"])
            if up_schema: st.session_state.json_config = json.load(up_schema)

        jc, jn, f_path, _ = file_browser_ui("json", is_recursive=False)
        if f_path and processing_engine == "FastAPI (Large file)":
            st.session_state.fastapi_target_file = f_path
            st.session_state.json_log_content = None
        elif jc: 
            st.session_state.json_log_content, st.session_state.json_log_name = jc, jn
            st.session_state.fastapi_target_file = None

    elif app_mode == "Recursive Analysis":
        use_json_rec = st.checkbox("Enable JSON Configuration?")
        if use_json_rec:
            schema_source = st.radio("Schema Source", ["Folder", "Upload"], horizontal=True, key="rec_ss")
            if schema_source == "Folder":
                jfiles = [f for f in os.listdir(SCHEMA_DIR) if f.endswith(".json")] if os.path.exists(SCHEMA_DIR) else []
                sel = st.selectbox("Select schema", ["choose"] + sorted(jfiles), key="rec_s")
                if sel != "choose":
                    with open(os.path.join(SCHEMA_DIR, sel)) as f: st.session_state.json_config = json.load(f)
            else:
                up_schema = st.file_uploader("Upload Schema JSON", type=["json"], key="rec_up")
                if up_schema: st.session_state.json_config = json.load(up_schema)
        else:
            st.session_state.json_config = None

        _, _, _, folder_target = file_browser_ui("rec", is_recursive=True)
        if folder_target:
            st.session_state.recursive_folder_target = folder_target
        if st.button("Start Deep Recursive Scan", use_container_width=True, type="primary"):
            st.session_state.recursive_folder_requested = True

# --- MAIN EXECUTION ---
if app_mode == "Recursive Analysis" and st.session_state.get("recursive_folder_requested"):
    st.header(f"📂 Deep Recursive Analysis")
    folder_to_scan = st.session_state.get("recursive_folder_target")
    config_to_apply = st.session_state.json_config if st.session_state.get("json_config") else None
    
    incs, stats, lines, ver, window_layers = analyze_folder_recursive(folder_to_scan, config=config_to_apply)
    st.session_state.active_incidents = incs 
    st.session_state.recursive_folder_requested = False 
    render_analysis(incs, stats, lines, ver, window_layers)

elif st.session_state.processing_engine == "FastAPI (Large file)":
    st.header(f"🚀 FastAPI Large File Processor ({app_mode})")
    
    if st.session_state.get("fastapi_target_file"):
        file_path = st.session_state.fastapi_target_file
        fastapi_url = st.session_state.get("fastapi_url", "http://localhost:8000")
        
        if st.button("Process with FastAPI", type="primary"):
            with st.spinner(f"FastAPI is analyzing {os.path.basename(file_path)}..."):
                try:
                    config_to_send = st.session_state.json_config if app_mode == "JSON Analysis" else None
                    payload = {"file_path": file_path, "rpc_delay_threshold": float(st.session_state.rpc_delay_threshold), "config": config_to_send}
                    
                    # Pop-up for visibility
                    st.toast("⚡ Splitting massive file into parallel chunks for sub-minute processing...", icon="🚀")
                    
                    response = requests.post(f"{fastapi_url}/analyze_large_file", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.toast("✅ Analysis Complete!", icon="🎉")
                        st.success("✅ Analysis Complete!")
                        st.session_state.active_incidents = data["incs"]
                        st.session_state.fastapi_stats = data["stats"]
                        st.session_state.fastapi_version = data["version"]
                        st.session_state.fastapi_window_layers = data["window_layers"]
                        st.session_state.fastapi_file_path = file_path 
                        st.session_state.fastapi_total_lines = data["total_lines"]
                        st.rerun() 
                    else: st.error(f"Error from FastAPI: {response.text}")
                except Exception as e: st.error(f"Failed to connect to FastAPI: {str(e)}")
                    
    if "fastapi_file_path" in st.session_state and st.session_state.get("fastapi_file_path") == st.session_state.get("fastapi_target_file"):
        total = st.session_state.fastapi_total_lines
        fp = st.session_state.fastapi_file_path
        
        jump = st.session_state.jump_line
        start = max(0, jump - 150)
        end = min(total, jump + 350)
        if jump == 0: end = min(total, 200)

        sparse_lines = [""] * total 
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                for idx, line in enumerate(itertools.islice(f, start, end), start):
                    sparse_lines[idx] = line
        except Exception as e:
            st.error(f"Error loading log lines for viewer: {e}")
            
        render_analysis(
            st.session_state.active_incidents, st.session_state.fastapi_stats, sparse_lines, 
            st.session_state.fastapi_version, st.session_state.fastapi_window_layers
        )
    elif not st.session_state.get("fastapi_target_file"):
        st.info("Please browse and select a log file from the sidebar.")

else:
    # --- LOCAL MEMORY EXECUTION ---
    if app_mode == "Standard Analysis":
        if st.session_state.get("memory_files"):
            incs, stats, lines, ver, window_layers = analyze_memory_files_recursive(st.session_state.memory_files)
            st.session_state.active_incidents = incs 
            render_analysis(incs, stats, lines, ver, window_layers)
        elif st.session_state.active_content:
            incs, stats, lines, ver, window_layers = analyze_log_turbo(st.session_state.active_content)
            st.session_state.active_incidents = incs 
            render_analysis(incs, stats, lines, ver, window_layers)
    elif app_mode == "JSON Analysis":
        if st.session_state.json_config and st.session_state.json_log_content:
            incs, stats, lines, ver, window_layers = analyze_log_turbo(st.session_state.json_log_content, st.session_state.json_config)
            st.session_state.active_incidents = incs 
            render_analysis(incs, stats, lines, ver, window_layers)
