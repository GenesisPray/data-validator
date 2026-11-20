#!/usr/bin/env python3
"""
MedBalance Web Server
Serves the Data Validator Web App and provides backend API endpoints for CSV validation.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from validator import validate_csv_content, generate_flagged_csv_bytes

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Cache of last validation result in memory
last_validation_result = None

class DataValidatorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open(os.path.join(DIRECTORY, 'index.html'), 'rb') as f:
                self.wfile.write(f.read())
            return

        elif path == '/api/sample':
            sample_path = os.path.join(DIRECTORY, 'sample_inventory_data.csv')
            if os.path.exists(sample_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="sample_inventory_data.csv"')
                self.end_headers()
                with open(sample_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Sample file not found")
            return

        elif path == '/api/template':
            tpl_path = os.path.join(DIRECTORY, 'template_inventory.csv')
            if os.path.exists(tpl_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="template_inventory.csv"')
                self.end_headers()
                with open(tpl_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Template file not found")
            return

        elif path == '/api/download-flagged':
            global last_validation_result
            if last_validation_result and last_validation_result.get('flagged_rows'):
                flagged_bytes = generate_flagged_csv_bytes(
                    last_validation_result['flagged_rows'],
                    last_validation_result['headers']
                )
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="flagged.csv"')
                self.end_headers()
                self.wfile.write(flagged_bytes)
            else:
                self.send_error(400, "No flagged records currently available. Please upload and validate a file first.")
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/validate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            content_type = self.headers.get('Content-Type', '')
            csv_text = ''

            if 'multipart/form-data' in content_type:
                # Basic multipart boundary extraction
                boundary = content_type.split('boundary=')[1].encode()
                parts = body.split(b'--' + boundary)
                for part in parts:
                    if b'filename=' in part:
                        headers_part, file_body = part.split(b'\r\n\r\n', 1)
                        file_body = file_body.rsplit(b'\r\n', 1)[0]
                        csv_text = file_body.decode('utf-8', errors='replace')
                        break
            else:
                csv_text = body.decode('utf-8', errors='replace')

            global last_validation_result
            last_validation_result = validate_csv_content(csv_text)

            # Write flagged.csv to workspace root automatically as well
            if last_validation_result.get('flagged_rows'):
                flagged_bytes = generate_flagged_csv_bytes(
                    last_validation_result['flagged_rows'],
                    last_validation_result['headers']
                )
                with open(os.path.join(DIRECTORY, 'flagged.csv'), 'wb') as f:
                    f.write(flagged_bytes)

            response_data = {
                'success': True,
                'total_rows': last_validation_result['total_rows'],
                'balanced_rows': last_validation_result['balanced_rows'],
                'flagged_rows_count': last_validation_result['flagged_rows_count'],
                'facilities': last_validation_result['facilities'],
                'facility_types': last_validation_result['facility_types'],
                'facility_stats': last_validation_result['facility_stats'],
                'flagged_rows': last_validation_result['flagged_rows'],
                'headers': last_validation_result['headers'],
                'column_mapping': last_validation_result['column_mapping']
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return

        self.send_error(404, "Endpoint not found")

def run(port=PORT):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, DataValidatorHandler)
    print("=" * 65)
    print("  MEDBALANCE HEALTH INVENTORY DATA VALIDATOR WEB SERVER")
    print("=" * 65)
    print(f"  Web Application available at: http://localhost:{port}")
    print("  Open this link in any browser (Chrome, Edge, Firefox).")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
        print("Server stopped cleanly.")

if __name__ == '__main__':
    run()

