"""
Odoo Model für Etiketten-Batches
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
    
    name = fields.Char('Batchname', required=True, default=lambda self: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('generated', 'Generiert'),
        ('error', 'Fehler'),
    ], default='draft', tracking=True)
    
    # Input
    csv_file = fields.Binary('CSV-Datei', attachment=True)
    csv_filename = fields.Char('Dateiname')
    
    # Output
    pdf_file = fields.Binary('PDF-Etikett', attachment=True, readonly=True)
    pdf_filename = fields.Char('PDF-Name', readonly=True, default='Batch_Lageretiketten.pdf')
    
    # Meta
    created_by = fields.Many2one('res.users', 'Erstellt von', readonly=True, default=lambda self: self.env.user)
    record_count = fields.Integer('Datensätze', readonly=True)
    group_count = fields.Integer('Gruppen (Regal+Ebene)', readonly=True)
    error_message = fields.Text('Fehlermeldung', readonly=True)
    
    # Config
    save_pdf = fields.Boolean('PDF speichern (Audit-Trail)', default=True)
    
    @api.model
    def create(self, vals):
        """Setzt Defaults bei Erstellung"""
        if 'name' not in vals or not vals['name']:
            vals['name'] = f"Batch {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        return super().create(vals)
    
    def action_generate_pdf(self):
        """Generiert PDF aus hochgeladener CSV"""
        from ..lib import PDFLabelGenerator
        
        for batch in self:
            try:
                if not batch.csv_file:
                    raise UserError("Bitte laden Sie zunächst eine CSV-Datei hoch.")
                
                # CSV dekodieren
                csv_content = batch.csv_file.decode('utf-8-sig')
                batch.record_count = len([l for l in csv_content.split('\n') if l.strip() and not l.startswith('Regal')])
                
                # PDF generieren
                generator = PDFLabelGenerator()
                grouped_data = generator.parse_csv_data(csv_content)
                
                if not grouped_data:
                    raise UserError("Keine gültigen Lagerdaten gefunden. Prüfen Sie die CSV-Struktur.")
                
                batch.group_count = len(grouped_data)
                pdf_buffer = generator.generate_pdf(grouped_data)
                
                # Speichern
                batch.pdf_file = base64.b64encode(pdf_buffer.read())
                batch.state = 'generated'
                batch.error_message = False
                
                # Audit-Trail (optional)
                if batch.save_pdf:
                    attachment = self.env['ir.attachment'].create({
                        'name': batch.pdf_filename,
                        'datas': batch.pdf_file,
                        'type': 'binary',
                        'res_model': 'label.batch',
                        'res_id': batch.id,
                    })
                    batch.message_post(
                        body=_("PDF generiert und gespeichert: %s") % attachment.name,
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
