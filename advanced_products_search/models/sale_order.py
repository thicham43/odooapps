# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def search_products(self):
        wizard = self.env['product.search'].create({'so_id': self.id})
        return {'type': 'ir.actions.act_window',
                'name': "Products Search - %s" % self.name,
                'res_model': 'product.search',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {'wiz_id': wizard.id}
                }
