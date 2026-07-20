"""
Odoo Model für Etiketten-Batches
CSV Format: Level, Position, Barcode, Rack
"""
import base64
import io
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LabelBatch(models.Model):
    _name = 'label.batch'
    _description = 'Etikettenblock für Lagerdruck'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Batchname', required=True, default=lambda self: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('generated', 'Generiert'),
        ('error', 'Fehler'),
    ], default='draft')
    
    # Input: CSV (Level/Position/Barcode/Rack Format)
    csv_file = fields.Binary('CSV-Datei', attachment=True)
    csv_filename = fields.Char('Dateiname')
    
    # Output
    pdf_file = fields.Binary('PDF-Etikett', attachment=True, readonly=True)
    pdf_filename = fields.Char('PDF-Name', readonly=True, default='Warehouse_Labels.pdf')
    
    # Meta
    created_by = fields.Many2one('res.users', 'Erstellt von', readonly=True, default=lambda self: self.env.user)
    record_count = fields.Integer('Datensätze', readonly=True)
    group_count = fields.Integer('Labels', readonly=True)
    error_message = fields.Text('Fehlermeldung', readonly=True)
    
    # Config
    save_pdf = fields.Boolean('PDF speichern (Audit-Trail)', default=True)
    
    @api.model
    def create(self, vals_list):
        """Setzt Defaults bei Erstellung"""
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = f"Batch {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        return super().create(vals_list)
    
    def action_generate_pdf(self):
        """Generiert PDF aus CSV (Level/Position/Barcode/Rack Format)"""
        from ..lib import PDFLabelGenerator
        
        for batch in self:
            try:
                if not batch.csv_file:
                    raise UserError("Bitte laden Sie zunächst eine CSV-Datei hoch (Level, Position, Barcode, Rack).")
                
                # CSV dekodieren
                csv_bytes = base64.b64decode(batch.csv_file)
                csv_content = csv_bytes.decode('utf-8-sig')
                
                # PDF generieren (neue Logik: gruppiert dynamisch nach Rack+Position)
                generator = PDFLabelGenerator(label_width=410, label_height=70, qr_size=90)
                labels = generator.parse_csv_data(csv_content)
                
                if not labels:
                    raise UserError("Keine vollständigen Labels gefunden. Benötigt Level 1-4 pro (Rack, Position) Paar.")
                
                batch.record_count = len(labels) * 4  # 4 Slots pro Label
                batch.group_count = len(labels)
                
                # PDF generieren
                pdf_buffer = generator.generate_pdf(labels)
                batch.pdf_file = base64.b64encode(pdf_buffer.read())
                batch.state = 'generated'
                batch.error_message = False
                
                # Audit-Trail
                if batch.save_pdf:
                    attachment = self.env['ir.attachment'].create({
                        'name': batch.pdf_filename,
                        'datas': batch.pdf_file,
                        'type': 'binary',
                        'res_model': 'label.batch',
                        'res_id': batch.id,
                    })
                    batch.message_post(
                        body=_("✅ PDF erfolgreich generiert: %d Labels, %d Slots\nDatei: %s") % (
                            batch.group_count,
                            batch.record_count,
                            attachment.name
                        ),
                        message_type='notification'
                    )
                
            except Exception as e:
                batch.state = 'error'
                batch.error_message = str(e)
                raise UserError(f"Fehler bei PDF-Generierung: {str(e)}")
    
    def action_download_pdf(self):
        """Trigger für PDF-Download"""
        for batch in self:
            if not batch.pdf_file:
                raise UserError("Kein PDF vorhanden. Bitte generieren Sie zunächst ein PDF.")
            
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{batch.id}/pdf_file/{batch.pdf_filename}',
                'target': 'new',
            }
