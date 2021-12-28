# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, urlparse, urlunparse
from flask import Flask, request, session, redirect, url_for, render_template, flash
from .models import list_all_persons, list_all_products, add_product, add_all_products, add_product_connection, get_connections_of_prod, Product, get_prod, connect#, list_all_locations, Person, Location
import json
import ast


def create_app():
  app = Flask(__name__)
  return app


app = create_app()
basket = []


@app.route('/', methods=['GET', 'POST'])
def index():
    all_products = list_all_products()

    if request.method == 'POST':
        prods_to_return = []
        category_filter = request.form.get('categories')
        brand_filter = request.form.get('brands')
        year_filter = request.form.get('years')
        for prod in all_products:
            add = True
            if category_filter != '-' and category_filter != '0':
                if prod['category'] != category_filter:
                    add = False
            if brand_filter != '-' and brand_filter != '0':
                if prod['brand'] != brand_filter:
                    add = False
            if year_filter != '-' and year_filter != '0':
                if prod['model_year'] != year_filter:
                    add = False
            if add:
                prods_to_return.append(prod)
    else:
        prods_to_return = all_products

    return render_template('index.html', product_added=prods_to_return, categories=Product().categories,
                           brands=Product().brands, years=range(2016, 2020), basket_size=len(basket))


@app.route('/basket', methods=['GET', 'POST'])
def basket_display():
    url = urlparse(request.url)

    if 'delete' in parse_qs(url.query).keys():
        id = parse_qs(url.query)['delete'][0]
        for i in range(len(basket)):
            if basket[i]['product_id'] == id:
                basket.pop(i)
                break

    display_done_shopping = False
    if 'buy' in parse_qs(url.query).keys():
        if len(basket) > 1:
            connect(basket)
        basket.clear()
        display_done_shopping = True


    if 'add_to_basket' in parse_qs(url.query).keys():
        prod = get_prod(parse_qs(url.query)['add_to_basket'][0])
        if len(prod) != 0:
            basket.append(prod[0])
    sum_price = 0.00
    for prod in basket:
        sum_price += float(prod['list_price'])

    products_related = []
    if len(basket) != 0:
        all_products = list_all_products()
        conn_ids = get_connections_of_prod(basket[-1]['product_id'])
        conn_ids_dict = {}
        for id in conn_ids:
            if id['product_id'] not in conn_ids_dict.keys():
                conn_ids_dict[id['product_id']] = 0
            conn_ids_dict[id['product_id']] += 1
        sort_orders = sorted(conn_ids_dict.items(), key=lambda x: x[1], reverse=True)
        for id in sort_orders:
            _name = ''
            for prod in all_products:
                if prod['product_id'] == id[0]:
                    products_related.append(prod)

        brand = basket[-1]['brand']
        same_brand = []
        for prod in all_products:
            if prod['brand'] == brand:
                if prod['product_id'] != basket[-1]['product_id']:
                    same_brand.append(prod)
        for prod in same_brand:
            not_in_yet = True
            for rel_prod in products_related:
                if rel_prod['product_id'] == prod['product_id']:
                    not_in_yet = False
            if not_in_yet:
                products_related.append(prod)

    return render_template('basket.html', sum_price=round(sum_price, 2), basket=basket, basket_size=len(basket),
                           products_related=products_related, display_done_shopping=display_done_shopping)


@app.route('/product', methods=['GET','POST'])
def product_display():
    url = urlparse(request.url)
    product_id = parse_qs(url.query)['product_id'][0]
    product = get_prod(product_id)
    if 'add_to_basket' in parse_qs(url.query).keys():
        prod = get_prod(parse_qs(url.query)['add_to_basket'][0])
        if len(prod) != 0:
            basket.append(prod[0])
    all_products = list_all_products()
    conn_ids = get_connections_of_prod(product_id)
    conn_ids_dict = {}
    for id in conn_ids:
        if id['product_id'] not in conn_ids_dict.keys():
            conn_ids_dict[id['product_id']] = 0
        conn_ids_dict[id['product_id']] += 1

    sort_orders = sorted(conn_ids_dict.items(), key=lambda x: x[1], reverse=True)
    product_related = []
    for id in sort_orders:
        _name = ''
        for prod in all_products:
            if prod['product_id'] == id[0]:
                product_related.append(prod)
    brand = product[0]['brand']
    same_brand = []
    for prod in all_products:
        if prod['brand'] == brand:
            if prod['product_id'] != product[0]['product_id']:
                same_brand.append(prod)
    for prod in same_brand:
        not_in_yet = True
        for rel_prod in product_related:
            if rel_prod['product_id'] == prod['product_id']:
                not_in_yet = False
        if not_in_yet:
            product_related.append(prod)

    return render_template('product.html', product=product, product_related=product_related, basket_size=len(basket))