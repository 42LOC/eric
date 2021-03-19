# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import relativedelta
import random


class ProductAnalyzer(models.Model):
    _name = 'product_analyzer'
    _description = 'product_analyzer'

    # default_code = fields.Char(size=64, required=True, index=True)
    # default_code = fields.Integer('Internal Code', readonly=True,
    # compute='code',
    # default=random.randint(1000, 9000)
    # )
    categ_id = fields.Many2one('product.category', string='Product Category'
                               # related='product_id.categ_id'
                               )
    line_ids = fields.One2many('product_analyzer.sheet', 'sheet_id')
    start_date = fields.Date(string='Order history start date',
                             default=datetime.date.today() - relativedelta.relativedelta(months=1))


class ProductAnalyzerSheet(models.Model):
    _name = 'product_analyzer.sheet'
    _description = 'product_analyzer_sheet'

    sheet_id = fields.Many2one('product_analyzer', required=True, auto_join=True)
    categ_id = fields.Many2one(related='sheet_id.categ_id')
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('categ_id', '=', categ_id)]")
    sku = fields.Char(string='SKU', related='product_id.barcode')
    title = fields.Char(string='Title', related='product_id.product_tmpl_id.name')
    direct = fields.Float(string='Direct', related='product_id.stock_move_ids.product_uom_qty')
    replenishment = fields.Float(string='Replenishment')
    sold = fields.Float(string='Qty Sold', compute='_compute_production')
    inventory = fields.Float(string='Inventory', related='product_id.qty_available')
    demand = fields.Float(string='Demand')
    production = fields.Float(string='Production', compute='_compute_production')
    actual_demand = fields.Float(string='Actual Demand')
    actual_production = fields.Float(string='Actual Production')
    completed = fields.Date(string='Completed')

    @api.depends('inventory', 'demand')
    def _compute_production(self):
        for record in self:
            record.production = record.demand - record.inventory
            record.sold = record.direct + record.replenishment


    # @api.depends('direct', 'replenishment')
    # def _compute_sold(self):
    #     for record in self:

