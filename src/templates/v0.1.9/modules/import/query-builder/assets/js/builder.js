$(document).ready(function () {
  // Query Builder options
  var options = {
    allow_empty: true,
    filters: schema,
    default_filter: 'name',
    icons: {
      add_group: 'fa fa-plus-square',
      add_rule: 'fa fa-plus-circle',
      remove_group: 'fa fa-minus-square',
      remove_rule: 'fa fa-minus-circle',
      error: 'fa fa-exclamation-triangle'
    }
  }

  // Instantiate the Query Builder
  $('#builder').queryBuilder(options)

  $(document).on('click', '.parse-mongo', function () {
    // Remove previous error messages
    $('.has-error').find('.rule-actions > .error-message').remove()
    // Build and show the querystring
    var querystring = JSON.stringify($('#builder').queryBuilder('getMongo'), undefined, 2)
    $('#json-querystring').html(querystring)
    $('#pretty-json-querystring').html('<pre><code>' + querystring + '</code></pre>')
    $('#query-preview').show()
  })

  $(document).on('click', '.reset', function () {
    $('#builder').queryBuilder('reset')
    $('#json-querystring', '#pretty-json-querystring').empty()
    $('#query-preview').hide()
  })
})
