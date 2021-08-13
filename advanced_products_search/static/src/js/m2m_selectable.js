odoo.define('advanced_products_search.m2m_selectable', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');
var registry = require('web.field_registry');
var core = require('web.core');
var qweb = core.qweb;
var Dialog = require('web.Dialog');
var rpc = require('web.rpc');

var FieldM2mSelectable = relational_fields.FieldMany2Many.extend({
    description: "Many2many_Selectable",
    supportedFieldTypes: ['many2many'],

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.renderer.hasSelectors = true;
            self.$el.prepend(qweb.render("Many2ManySelectable", {widget: self}));
            self.$el.find(".btn_add").click(function(){
	        	self.add_selected_products();
	        });
        });
    },


    add_selected_products: function() {
        var self = this;
        var selected_ids = self.get_selected_ids();
        if (selected_ids) {
            rpc.query({model: 'product.search',
                       method: 'do_insert_products',
                       args: [self.res_id, selected_ids]
                      }).then(function(added_prods_data) {
                          self.update_inserted_products_tab();
                          self.clear_selection();
                          self.show_added_products_count(added_prods_data.length);
                        });
        }
    },


    get_selected_ids: function (){
        if (!this.renderer.selection.length){
			   new Dialog(this, {title: "Attention",
                                 size: 'medium',
                                 $content: $("<div/>").html("Please select at least one product!")
			                     }).open();
               return false;
        }
        var ids = [];

        const checked_rows = this.$('tr').filter((i, el) => this.renderer.selection.includes(el.dataset.id));
        checked_rows.find('.o_list_record_selector input').prop('checked', true);

        for(let i=0; i < checked_rows.length; i++) {
            ids.push(parseInt(checked_rows[i].lastChild.textContent));
        }
        return ids;
    },


    update_inserted_products_tab: function (){
        const checked_rows = this.$('tr').filter((i, el) => this.renderer.selection.includes(el.dataset.id));
        const tbody = $(".list_inserted_products table tbody");
        _.each(checked_rows, function(row) {
             const row_clone = row.cloneNode(true);
             row_clone.removeChild(row_clone.firstElementChild)
             tbody.prepend(row_clone);
        })
    },


    clear_selection: function (){
        const checked_rows = this.$('tr').filter((i, el) => this.renderer.selection.includes(el.dataset.id));
        checked_rows.find('.o_list_record_selector input').prop('checked', false);
    },


    show_added_products_count: function (prods_count){
        var unit = prods_count === 1 ? " Product" : " Products";
        var tab_header = $(".page_inserted_products a")[0];
        tab_header.style = "background:#f2f2f2;color:green;font-weight:bold;";
        tab_header.textContent = "+"+ prods_count + unit;
        setTimeout(function(){tab_header.style = "";
		    					     tab_header.textContent = "Used Products";}, 1000);
    },


});


registry.add('m2m_selectable', FieldM2mSelectable);

});
