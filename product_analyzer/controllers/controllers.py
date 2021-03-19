# -*- coding: utf-8 -*-
# from odoo import http


# class ProductAnalyzer(http.Controller):
#     @http.route('/product_analyzer/product_analyzer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_analyzer/product_analyzer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_analyzer.listing', {
#             'root': '/product_analyzer/product_analyzer',
#             'objects': http.request.env['product_analyzer.product_analyzer'].search([]),
#         })

#     @http.route('/product_analyzer/product_analyzer/objects/<model("product_analyzer.product_analyzer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_analyzer.object', {
#             'object': obj
#         })
