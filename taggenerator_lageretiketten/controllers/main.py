"""
Web-Controller für Etikettenmodul
"""
from odoo import http
from odoo.http import request


class LabelBatchController(http.Controller):
    
    @http.route('/label_batch/api/generate', type='json', auth='user', methods=['POST'])
    def generate_label_batch(self, **kwargs):
        """API-Endpoint für PDF-Generierung (zukünftig für externe Systeme)"""
        csv_data = kwargs.get('csv_data')
        if not csv_data:
            return {'error': 'Keine CSV-Daten'}
        
        # Batch erstellen und generieren
        batch = request.env['label.batch'].create({
            'csv_file': csv_data.encode('utf-8'),
            'csv_filename': kwargs.get('filename', 'import.csv'),
        })
        batch.action_generate_pdf()
        
        return {
            'success': True,
            'batch_id': batch.id,
            'name': batch.name,
        }
