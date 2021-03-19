# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import time
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

    @api.depends('start_date')
    def _get_compute_name(self):
        for line in self:
            line.name = f'{line.start_date.strftime("%m/%d/%Y")} ' \
                        f'- {line.create_date.strftime("%m/%d/%Y")}'

    def generate_sheet(self):
        products = self.env['product.template'].search([('categ_id', '=', self.categ_id.id)]).product_variant_id.ids
        order = self.env['sale.order'].search(
            ['&', ('date_order', '>=', self.start_date), ('date_order', '<=', self.create_date)]).ids
        result = self.env['sale.order.line'].search(['&', ('product_id', 'in', products), ('order_id', 'in', order)])
        for i in result:
            self.env['product_analyzer.sheet'].create({
                # 'product_id': i.product_id.id,
                'direct': i.product_uom_qty,
                'title': i.name,
                'sku': i.product_id.barcode,
                'sheet_id': self.id,
                'inventory': i.product_id.qty_available
            })


class ProductAnalyzerSheet(models.Model):
    _name = 'product_analyzer.sheet'
    _description = 'product_analyzer_sheet'

    sheet_id = fields.Many2one('product_analyzer')
    # categ_id = fields.Many2one(related='sheet_id.categ_id')
    # product_id = fields.Many2one('product.product', string='Product',
    #                              domain="[('categ_id', '=', categ_id)]")
    sku = fields.Char(string='SKU',)
                      # related='product_id.barcode')
    title = fields.Char(string='Title',)
                        # related='product_id.product_tmpl_id.name')
    direct = fields.Float(string='Direct')
                          # related='product_id.stock_move_ids.product_uom_qty')
    inbound = fields.Float(string='Inbound')
    sold = fields.Float(string='Qty Sold', compute='_compute_production')
    inventory = fields.Float(string='Inventory',)
                             # related='product_id.qty_available')
    send_in = fields.Float(string='Send In')
    production = fields.Float(string='Production',
                              compute='_compute_production')
    actual_demand = fields.Float(string='Actual Demand')
    actual_cut = fields.Float(string='Actual Cut')
    completed = fields.Date(string='Completed')

    @api.depends('inventory', 'send_in')
    def _compute_production(self):
        for record in self:
            record.production = record.send_in - record.inventory
            record.sold = record.direct + record.inbound
