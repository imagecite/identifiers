import flask
import identifiers

app = flask.Flask(__name__, static_url_path='')

@app.template_filter('identifier_link')
def identifier_link(i):
    fmt = '<a href="%s%s/%s">%s</a>'
    return fmt % (flask.request.url_root, i.type, i.ident, str(i))

@app.errorhandler(404)
def not_found(error):
    return (flask.render_template('404.tmpl'), 404)

@app.route('/')
def index():
    return flask.render_template('index.tmpl')

@app.route('/search')
def search():
    return flask.redirect(flask.url_for('identifier', 
                          scheme=flask.request.args['scheme'], 
                          ident=flask.request.args['ident']))

@app.route('/<scheme>/<path:ident>')
def identifier(scheme, ident):
    i = identifiers.Identifier(scheme, ident)
    links = identifiers.get_links(i)
    if not links:
        flask.abort(404)
    return flask.render_template('identifier.tmpl', identifier=i, links=links)

if __name__ == '__main__':
    app.run(debug=True)

application = app
application.debug = True

# eof
