/* Create glossary links */
var context = '.md-main'
var exclude = ['code', '.no-gloss']
var terms = ['project', 'module']
var synonyms = {
    'project': 'projects',
    'module': 'modules'
}
var options = {
  'element': 'mark',
  'className': 'glossary',
  'separateWordSearch': true,
  'accuracy': 'exactly',
  'synonyms': synonyms,
  'caseSensitive': true,
  'exclude': exclude,
  'each': function (node) {
    var link = document.createElement('a')
    var glossAnchor = 'glossary/#' + node.innerText
    var url = new URL(window.location)
    url = url.href.split('getting_started/')[0] + 'getting_started/' + glossAnchor
    link.setAttribute('href', url)
    link.innerHTML = node.innerHTML
    node.innerHTML = link.outerHTML
  }
}
var instance = new Mark(context)
instance.mark(terms, options)