import os
import subprocess
from pathlib import Path
import base64
import io

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(
    [
        html.H1("WAV File Processor"),
        dcc.Upload(
            id="upload-wav",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=False,
            accept=".wav",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Label("Output Directory", html_for="output-dir"), width="auto", className="column"),
                dbc.Col(
                    dbc.Input(id="output-dir", type="text", placeholder="Enter output directory"),
                    width="auto",
                    className="column",
                ),
            ],
            align="center",
            className="no-gutters",
        ),
        html.Div(id="output"),
    ],
    fluid=True,
)

def process_wav(contents, filename, output_dir):
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    temp_wav = Path(f"temp/{filename}")
    temp_wav.parent.mkdir(parents=True, exist_ok=True)
    op_wavpath = Path(output_dir, filename)
    op_wavpath = op_wavpath.with_suffix(".mp3")

    with open(temp_wav, "wb") as f:
        f.write(io.BytesIO(decoded).read())

    python_script = "/Users/mikeshih/Documents/code/dash/convertfile.py"
    subprocess.run(['python', python_script, '-i', str(temp_wav), '-o', str(op_wavpath)])

    return f"Processed {filename} using {python_script}"

@app.callback(
    Output("output", "children"),
    [Input("upload-wav", "contents")],
    [State("upload-wav", "filename"), State("output-dir", "value")],
)
def update_output(contents, filename, output_dir):
    if contents is not None and output_dir is not None:
        result = process_wav(contents, filename, output_dir)
        return html.Div([html.Hr(), html.P(result)])
    return None

if __name__ == "__main__":
    app.run_server(debug=False)
