# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import relativedelta


class ProductAnalyzer(models.Model):
    _name = 'product_analyzer'
    _description = 'product_analyzer'
    _rec_name = 'field'

    field = fields.Char(default='Configuration', store=False)
    name = fields.Char(string="Name", compute='_get_compute_name')
    available = fields.Boolean(string="Available", default=True)
    categ_id = fields.Many2one('product.category', string='Product Category')
    create_date = fields.Date(string="Start day", default=datetime.date.today())
    line_ids = fields.One2many('product_analyzer.sheet', 'sheet_id')
    start_date = fields.Date(string='Order history start date',
                             default=datetime.date.today() - relativedelta.relativedelta(months=1))
    active = fields.Boolean(default=True)

    @api.depends('start_date')
    def _get_compute_name(self):
        for line in self:
            line.name = f'{line.start_date.strftime("%m/%d/%Y")} ' \
                        f'- {line.create_date.strftime("%m/%d/%Y")}'

    def generate_sheet(self):
        products = self.env['product.template'].search(
            [('categ_id', '=', self.categ_id.id)]).product_variant_id
        order = self.env['sale.order'].search(
            ['&', ('date_order', '>=', self.start_date), ('date_order', '<=', self.create_date)]).ids
        for line in self.line_ids:
            if line.category_id.id != self.categ_id.id:
                line.unlink()
        if products:
            for product in products:
                sheet = self.env['product_analyzer.sheet'].search(
                    ['&', ('title', '=', product.name), ('sheet_id', '=', self.id)])
                if order and products:
                    self.env.cr.execute(f"""SELECT SUM (product_uom_qty) AS total
                                        FROM sale_order_line
                                        WHERE product_id = {product.id} AND order_id IN %s """,
                                        [tuple(order)])
                    result = self.env.cr.dictfetchall()
                    if not sheet.id:
                        self.env['product_analyzer.sheet'].create({
                            'direct': result[0]['total'],
                            'title': product.display_name,
                            # 'sku': i.product_id.barcode,
                            'sheet_id': self.id,
                            'inventory': product.qty_available,
                            'category_id': product.categ_id.id
                        })
                    else:
                        sheet.update({
                            'direct': result[0]['total'],
                            # 'title': product.name,
                            # 'sku': i.product_id.barcode,
                            # 'sheet_id': self.id,
                            'inventory': product.qty_available,
                            'category_id': product.categ_id.id
                        })
                else:
                    sheet.unlink()


class ProductAnalyzerSheet(models.Model):
    _name = 'product_analyzer.sheet'
    _description = 'product_analyzer_sheet'

    sheet_id = fields.Many2one('product_analyzer')
    category_id = fields.Many2one('product.category')
    sku = fields.Char(string='SKU')
    title = fields.Char(string='Title')
    direct = fields.Float(string='Direct')
    inbound = fields.Float(string='Inbound')
    sold = fields.Float(string='Qty Sold', store=True, compute='_compute_production')
    inventory = fields.Float(string='Inventory')
    send_in = fields.Float(string='Send In')
    production = fields.Float(string='Production', store=True, compute='_compute_production')
    actual_demand = fields.Float(string='Actual Demand')
    actual_cut = fields.Float(string='Actual Cut')
    completed = fields.Date(string='Completed')
    active = fields.Boolean(default=True)

    @api.depends('inventory', 'send_in', 'direct', 'inbound')
    def _compute_production(self):
        for record in self:
            record.production = record.send_in - record.inventory
            record.sold = record.direct + record.inbound
