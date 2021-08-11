# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductSearch(models.Model):
    _name = "product.search"
    _description = 'Product Search Engine'

    so_id = fields.Many2one(comodel_name="sale.order", string="SO")
    frs_id = fields.Many2one(comodel_name="res.partner", string="Fournisseur")
    categ_id = fields.Many2one(comodel_name="product.type", string="Type Produit")
    name = fields.Char(string="Désignation")
    reference = fields.Char(string="Référence")
    product_ids = fields.Many2many(comodel_name="product.template", relation="product_search_product_template_rel", string="Articles")
    inserted_products = fields.One2many(comodel_name="inserted.product", inverse_name="wizard_id", string="Articles insérés")
    nb_prods = fields.Text(string='nb of prods found')


    @api.onchange('frs_id', 'categ_id', 'name', 'reference',)
    def onchange_fields_search(self):

        req = """ SELECT pt.id  FROM product_template pt
                  INNER JOIN product_product pp ON pp.product_tmpl_id = pt.id
                  INNER JOIN res_partner frs ON frs.id = pt.frs_id
                  WHERE frs.active = True AND pt.separateur != True AND  pt.sale_ok = True
              """

        if not (self.frs_id or self.categ_id or self.name or self.reference):
            self.product_ids = None
            return

        if self.frs_id:
            req += " AND pt.frs_id = %s" % self.frs_id.id

        if self.categ_id:
            req += " AND pt.categ_id = %s" % self.categ_id.id

        if self.reference:
            reference = self.reference.replace("'", "''")
            if self.force_reference == 'frs':
                req += " AND pt.frs_code ilike  '%%%s%%' " % reference
            elif self.force_reference == 'com':
                req += " AND pt.commercial_code ilike '%%%s%%' " % reference
            else:
                req += " AND (pt.frs_code ilike  '%%%s%%' OR pt.commercial_code ilike '%%%s%%') " % (reference, reference)

        if self.name:
            if " " in self.name:
                designation = self.name.replace("'", "''")
                words = designation.split(" ")
                if words:
                    req += " AND ("
                    for w in words:
                        if words.index(w) == len(words) - 1:
                            req += " pt.name ilike '%%%s%%')" % w
                        else:
                            req += " pt.name ilike '%%%s%%' AND" % w
            else:
                designation = self.name.replace("'", "''")
                req += " AND pt.name ilike '%{}%'".format(designation)

        req_count = req.replace("SELECT pt.id", "SELECT count(pt.id)")
        self._cr.execute(req_count)
        result_count = self._cr.fetchall()
        result_count = int(result_count[0][0])
        req += " ORDER BY pt.name"

        self.product_ids = None
        self.nb_prods = None
        if result_count > 1000:
            self.nb_prods = '+1000 articles trouvés! \n Veuillez affiner votre recherche :)'
        elif result_count == 0:
            self.nb_prods = 'Aucun article trouvé!'
        else:
            self._cr.execute(req)
            self.product_ids = [p[0] for p in self._cr.fetchall()]


    def reset(self):
        q = "DELETE FROM product_search_product_template_rel WHERE product_search_id=%s" % self.id
        self._cr.execute(q)
        reset_all_fields = """ UPDATE product_search SET frs_id=null, categ_id=null, name=null,
                               reference=null, nb_prods=null WHERE id = %s
                           """ % self.id
        self._cr.execute(reset_all_fields)
        return {'type': 'ir.actions.act_window',
                'name': "Products Search",
                'res_model': 'product.search',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                }


    def action_close(self):
        q1 = "DELETE FROM product_search_product_template_rel WHERE product_search_id = %s " % self.id
        q2 = "DELETE FROM product_search WHERE id = %s " % self.id
        self._cr.execute(q1)
        self._cr.execute(q2)


    @api.model
    def do_insert_products(self, wizard_id, selected_prods_ids):
        wizard = self.env['product.search'].browse(wizard_id)
        so = wizard.so_id
        sol_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']
        for pid in selected_prods_ids:
            product = product_obj.search([('product_tmpl_id', '=', pid)])
            price = product.list_price
            next_sequence = so.order_line and max([l.sequence for l in so.order_line]) + 1 or 1
            vals = {'order_id': so.id,
                    'price_unit': price,
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': 1,
                    'sequence': next_sequence,
                    }
            sol_obj.create(vals)
        return selected_prods_ids


class InsertedProduct(models.Model):
    _name = "inserted.product"
    _description = 'Inserted Products through Search Engine'

    wizard_id = fields.Many2one(comodel_name="product.search", string="Search wizard")
    frs = fields.Char(string='Frs')
    name = fields.Char(string='Désignation')
    frs_code = fields.Char(string='Réf Fournisseur')
    unit_price = fields.Char(string='Unit Price')
