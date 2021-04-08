from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import tempfile
from odoo.tools.misc import xlwt
import io
import base64
import time
from dateutil.relativedelta import relativedelta
from pytz import timezone


class LocationWiseReportWiz(models.TransientModel):
    _name = 'location.wise.report.wiz'
    _description = 'Location Wise Report'

    caterogy_ids = fields.Many2many('product.category',string="Product Category")
    location_id = fields.Many2one('stock.location',string="Location")
    select_location = fields.Selection([('all','All'),('location','Location')],default='all')

    @api.multi
    def location_wise_report(self):

        filename = ('Location wise Report') + '.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Location Wise')
        font = xlwt.Font()
        font.bold = True
        for_left = xlwt.easyxf("font: bold 1, color black; borders: top double, bottom double, left double, right double; align: horiz left")
        for_left_not_bold = xlwt.easyxf("font: color black; align: horiz left")
        for_center_bold = xlwt.easyxf("font: bold 1, color black; align: horiz center")
        GREEN_TABLE_HEADER = xlwt.easyxf(
                 'font: bold 1, name Tahoma, height 250;'
                 'align: vertical center, horizontal center, wrap on;'
                 'borders: top double, bottom double, left double, right double;'
                 )
        loc_header = xlwt.easyxf(
                 'font: bold 1, name Tahoma, height 200;'
                 'align: vertical center, horizontal center, wrap on;'
                 'borders: top double, bottom double, left double, right double;'
                 )
        style = xlwt.easyxf('font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
        
        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'

        worksheet.row(0).height = 400
        worksheet.col(0).width = 8000
        worksheet.col(1).width = 6000
        worksheet.col(2).width = 3500
        worksheet.col(3).width = 8000

        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders

        row = 2
        worksheet.write(row, 0, 'Product Name' or '', for_left)
        worksheet.write(row, 1, 'Product Category' or '', for_left)
        worksheet.write(row, 2,  'Current Stock' or '', for_left)
        worksheet.write(row, 3,  'Location' or '', for_left)

        if self.caterogy_ids and self.select_location == 'location' and self.location_id:
            product_ids = self.env['stock.quant'].search(
                [('product_id.active', '=', True), ('product_id.categ_id', 'in', self.caterogy_ids.ids),('location_id','=',self.location_id.id)],order='id desc')
            title = self.location_id.name + 'Location'
        elif self.caterogy_ids and self.select_location == 'all' and not self.location_id:
            product_ids = self.env['stock.quant'].search(
                [('product_id.active', '=', True), ('product_id.categ_id', 'in', self.caterogy_ids.ids)],order='id desc')
            title ="Stock Report Location Wise"
        
        title = title
        worksheet.write_merge(0,1,0,3,title,GREEN_TABLE_HEADER)

        # Group By of Location
        if product_ids:
            if self.select_location == 'all':
                row =0
                order_data = self.env['stock.quant'].read_group([('id', 'in', product_ids.ids)],['location_id'],['location_id'], lazy=False)
                pr_list = []
                for ref in order_data:
                    if ref['location_id']:
                        pr_list.append(ref['location_id'])
                for order in pr_list:
                    row += 2
                    quant_id = self.env['stock.quant'].browse(order)
                    location_name = quant_id[1].id
                    worksheet.write_merge(row+1, row+1, 0, 3,str(location_name), loc_header)
                    row += 1
                    for rec in product_ids:
                        if order[0] == rec.location_id.id:
                            row = row + 1
                            worksheet.write(row, 0, rec.product_id.display_name or '', for_left_not_bold)
                            worksheet.write(row, 1, rec.product_id.categ_id.name or '', for_left_not_bold)
                            worksheet.write(row, 2, rec.quantity  or '', for_left_not_bold)
                            worksheet.write(row, 3, str(rec.location_id.location_id.name) + '/' +  str(rec.location_id.name) or '', for_left_not_bold)
            else:
                row = 3
                for rec in product_ids:
                    worksheet.write(row, 0, rec.product_id.display_name or '', for_left_not_bold)
                    worksheet.write(row, 1, rec.product_id.categ_id.name or '', for_left_not_bold)
                    worksheet.write(row, 2, rec.quantity  or '', for_left_not_bold)
                    worksheet.write(row, 3, str(rec.location_id.location_id.name) + '/' +  str(rec.location_id.name) or '', for_left_not_bold)
                    row += 1
        else:
            raise UserError(_('No Record Founds.'))
        
        fp = io.BytesIO()
        workbook.save(fp)
        location_wise_id = self.env['location.wise.report.excel.extended'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return{
            'view_mode': 'form',
            'res_id': location_wise_id.id,
            'res_model': 'location.wise.report.excel.extended',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }

class LocationWiseExcelExtended(models.Model):
    _name = 'location.wise.report.excel.extended'
    _description = "Filing Loss Excel Extended"

    excel_file = fields.Binary('Download Report :-')
    file_name = fields.Char('Excel File', size=64)

